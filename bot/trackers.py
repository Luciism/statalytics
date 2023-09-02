import asyncio
import logging
import sqlite3
import time
from datetime import datetime, timedelta
from os import getenv

from discord.ext import commands, tasks
from dotenv import load_dotenv

load_dotenv()

from statalib import (
    CustomTimedRotatingFileHandler,
    save_historical,
    reset_tracker,
    fetch_hypixel_data_rate_limit_safe,
    bedwars_data_to_tracked_stats_tuple,
    align_to_hour,
    log_error_msg,
    get_reset_time,
    get_player_dict,
    get_level,
    PlayerUUID
)


logger = logging.getLogger('statalytics')
logger.setLevel(logging.INFO)
logger.addHandler(CustomTimedRotatingFileHandler())


"""
This query is designed to find data from the `trackers` table that
needs to be reset based on the reset times configured in the
`configured_reset_times` and `default_reset_times` tables.
The query uses `LEFT JOIN` to combine data from the `trackers`,
`linked_accounts`, `configured_reset_times`, and `default_reset_times` tables.

The `configured_reset_times` table stores reset times configured by
discord id, while the `default_reset_times` table stores default reset
times by player uuid.

The query uses data from the `configured_reset_times` table if it is
available for the respective discord id, otherwise it uses data from
the `default_reset_times` table.

The query checks if the combined `timezone + reset_hour` value from
either the `configured_reset_times` or `default_reset_times` tables
equals x, where x is a parameter passed to the query. The query also
wraps, so 23 would be 23, but 24 would be 0, etc. If neither the
`configured_reset_times` nor the `default_reset_times` tables have
data for the respective discord id or player uuid, then the query
returns a value of 0.

The result of the query is a set of rows from the `trackers` table
that meet the specified conditions. You can use this result set to
find and process data from the `trackers` table that needs to be reset
based on the configured reset times.
"""
query = """
SELECT trackers.uuid FROM trackers
LEFT JOIN linked_accounts ON trackers.uuid = linked_accounts.uuid
LEFT JOIN configured_reset_times ON linked_accounts.discord_id = configured_reset_times.discord_id
LEFT JOIN default_reset_times ON trackers.uuid = default_reset_times.uuid
WHERE (COALESCE(
    configured_reset_times.timezone + configured_reset_times.reset_hour,
    default_reset_times.timezone + default_reset_times.reset_hour,
    0
) % 24) = ?;
"""


class Client(commands.Bot):
    def __init__(self):
        super().__init__(intents=None, command_prefix='$')

    async def on_ready(self):
        print(f'Logged in as {client.user} (ID: {client.user.id})\n------')

    async def setup_hook(self) -> None:
        reset_trackers.start()

client = Client()

# Bounce all command errors
@client.event
@client.tree.error
async def on_command_error(_, __):
    return


@tasks.loop(hours=1)
async def reset_trackers():
    logger.info('Scheduled tracker reset event starting...')
    fetched_players = []

    utc_now = datetime.utcnow()

    with sqlite3.connect('database/core.db') as conn:
        cursor = conn.cursor()

        cursor.execute(query, (utc_now.hour,))
        data_to_reset = cursor.fetchall()

    logger.info(f'Total trackers to reset: {len(data_to_reset) // 4}')

    for tracker_data in data_to_reset:
        uuid = tracker_data[0]

        # prevents fetching data for multiple trackers
        if not uuid in fetched_players:
            logger.info(f'Resetting trackers for: {uuid}')

            try:
                start_time = time.time()

                reset_time = get_reset_time(uuid)

                # now + gmt offset
                timezone = utc_now + timedelta(hours=reset_time[0])

                hypixel_data = await fetch_hypixel_data_rate_limit_safe(uuid, attempts=15)
                client.dispatch(
                    'tracker_reset',
                    uuid=uuid,
                    hypixel_data=hypixel_data,
                    timezone=timezone
                )

                fetched_players.append(uuid)
            except Exception as error:
                await log_error_msg(client, error)

            # limit requests to 1 per 2 seconds
            time_elapsed = time.time() - start_time
            await asyncio.sleep(2 - time_elapsed)


@client.event
async def on_tracker_reset(
    uuid: PlayerUUID,
    hypixel_data: dict,
    timezone: datetime
):
    """
    :param uuid: the uuid of the player whos trackers are being reset
    :param hypixel_data: the current hypixel data of the player
    :param timezone: the current time of the player's configured timezone
    """
    hypixel_data = get_player_dict(hypixel_data)

    bedwars_data: dict = hypixel_data.get("stats", {}).get("Bedwars", {})
    bedwars_data_list = bedwars_data_to_tracked_stats_tuple(bedwars_data)

    level = get_level(bedwars_data.get('Experience', 0))

    yesterday = (timezone - timedelta(days=1))

    # reset daily
    save_historical(
        tracker='daily',
        bedwars_data=bedwars_data_list,
        uuid=uuid,
        current_level=level,
        period=yesterday.strftime('daily_%Y_%m_%d')
    )
    await reset_tracker(
        uuid, tracker='daily', bedwars_data=bedwars_data_list)

    # reset weekly
    if timezone.weekday() == 6:
        save_historical(
            tracker='weekly',
            bedwars_data=bedwars_data_list,
            uuid=uuid,
            current_level=level,
            period=yesterday.strftime('weekly_%Y_%U')
        )
        await reset_tracker(
            uuid, tracker='weekly', bedwars_data=bedwars_data_list)

    # reset monthly
    if timezone.day == 1:
        save_historical(
            tracker='monthly',
            bedwars_data=bedwars_data_list,
            uuid=uuid,
            current_level=level,
            period=yesterday.strftime('monthly_%Y_%m')
        )
        await reset_tracker(
            uuid, tracker='monthly', bedwars_data=bedwars_data_list)

    # reset yearly
    if timezone.timetuple().tm_yday == 1:
        save_historical(
            tracker='yearly',
            bedwars_data=bedwars_data_list,
            uuid=uuid,
            current_level=level,
            period=yesterday.strftime('yearly_%Y')
        )
        await reset_tracker(
            uuid, tracker='yearly', bedwars_data=bedwars_data_list)


@reset_trackers.before_loop
async def before_reset_trackers():
    await align_to_hour()


@reset_trackers.error
async def on_reset_trackers_error(error):
    reset_trackers.restart()
    await log_error_msg(client, error)


if __name__ == '__main__':
    client.run(getenv('BOT_TOKEN'), root_logger=True)
