import asyncio
import logging
import sqlite3
import time
from datetime import datetime, timedelta, UTC
from os import getenv

from discord.ext import commands, tasks
from dotenv import load_dotenv

load_dotenv()

import statalib


root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
root_logger.addHandler(statalib.CustomTimedRotatingFileHandler(
    logs_dir=f"{statalib.REL_PATH}/logs/bot"
))

logger = logging.getLogger('statalytics.trackers')
logger.setLevel(logging.DEBUG)


"""
This query is designed to find data from the `trackers_new` table that
needs to be reset based on the reset times configured in the
`configured_reset_times` and `default_reset_times` tables. The query
uses `LEFT JOIN` to combine data from the `trackers_new`,
`linked_accounts`, `configured_reset_times`, and `default_reset_times`
tables.

The `configured_reset_times` table stores reset times configured by
discord id, while the `default_reset_times` table stores default reset
times by player uuid.

The query uses data from the `configured_reset_times` table if it is
available for the respective discord id, otherwise it uses data from
the `default_reset_times` table.

The query checks if the combined `reset_hour - timezone` value from
either the `configured_reset_times` or `default_reset_times` tables
equals x, where x is a parameter passed to the query. The query also
wraps, so 23 would be 23, but 24 would be 0, etc. If neither the
`configured_reset_times` nor the `default_reset_times` tables have
data for the respective discord id or player uuid, then the query
returns a value of 0.

The result of the query is a set of rows from the `trackers_new` table
that meet the specified conditions. You can use this result set to
find and process data from the `trackers_new` table that needs to be
reset based on the configured reset times.

Please note that if a negative value is obtained from subtracting
timezone from reset_hour, it will be adjusted by adding 24 before
performing modulus operation. This ensures that negative numbers are
handled appropriately.
"""

query = """
SELECT trackers_new.uuid FROM trackers_new
LEFT JOIN linked_accounts
    ON trackers_new.uuid = linked_accounts.uuid
LEFT JOIN configured_reset_times
    ON linked_accounts.discord_id = configured_reset_times.discord_id
LEFT JOIN default_reset_times
    ON trackers_new.uuid = default_reset_times.uuid
WHERE (
    COALESCE(
        CASE WHEN configured_reset_times.reset_hour - configured_reset_times.timezone < 0
            THEN configured_reset_times.reset_hour - configured_reset_times.timezone + 24
            ELSE configured_reset_times.reset_hour - configured_reset_times.timezone END,
        CASE WHEN default_reset_times.reset_hour - default_reset_times.timezone < 0
            THEN default_reset_times.reset_hour - default_reset_times.timezone + 24
            ELSE default_reset_times.reset_hour - default_reset_times.timezone END,
        0
    ) % 24
) = ?;
"""

# OLD query
"""
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
        logger.info(f'Logged in as {client.user} (ID: {client.user.id})\n------')

    async def setup_hook(self) -> None:
        reset_trackers_loop.start()

client = Client()

# Bounce all command errors
@client.event
@client.tree.error
async def on_command_error(_, __):
    return


async def reset_trackers():
    fetched_players = []

    auto_reset_config: dict = statalib.config('apps.bot.tracker_resetting.automatic') or {}

    utc_now = datetime.now(UTC)

    with sqlite3.connect(statalib.config.DB_FILE_PATH) as conn:
        cursor = conn.cursor()

        cursor.execute(query, (utc_now.hour,))
        data_to_reset = cursor.fetchall()

    logger.info(f'Total trackers to reset: {len(data_to_reset) // 4}')

    for tracker_data in data_to_reset:
        uuid = tracker_data[0]

        # prevents refetching data for multiple trackers
        if uuid in fetched_players:
            continue

        try:
            start_time = time.time()

            # criteria
            if not statalib.has_auto_reset(uuid, auto_reset_config):
                continue

            logger.info(f'Resetting trackers for: {uuid}')
            reset_time = statalib.get_reset_time(uuid)

            # now + gmt offset
            timezone = utc_now + timedelta(hours=reset_time[0])

            fetched_players.append(uuid)

            hypixel_data = await statalib.fetch_hypixel_data_rate_limit_safe(uuid, attempts=15)

            if not hypixel_data.get('success'):
                logger.warning(f"Hypixel request unsuccessful: {hypixel_data}")
                continue

            client.dispatch(
                'tracker_reset',
                uuid=uuid,
                hypixel_data=hypixel_data,
                timezone=timezone
            )

        except Exception as error:
            await statalib.log_error_msg(client, error)

        # limit requests to 1 per 2 seconds
        time_elapsed = time.time() - start_time
        await asyncio.sleep(2 - time_elapsed)


@tasks.loop(hours=1)
async def reset_trackers_loop():
    logger.info('Scheduled tracker reset event starting...')
    await reset_trackers()


@client.event
async def on_tracker_reset(
    uuid: statalib.PlayerUUID,
    hypixel_data: dict,
    timezone: datetime
):
    """
    :param uuid: the uuid of the player whos trackers are being reset
    :param hypixel_data: the current hypixel data of the player
    :param timezone: the current time of the player's configured timezone
    """
    hypixel_data = statalib.get_player_dict(hypixel_data)

    bedwars_data: dict = hypixel_data.get("stats", {}).get("Bedwars", {})
    bedwars_data_list = statalib.bedwars_data_to_tracked_stats_tuple(bedwars_data)

    level = statalib.get_level(bedwars_data.get('Experience', 0))

    yesterday = (timezone - timedelta(days=1))

    # reset daily
    statalib.save_historical(
        tracker='daily',
        bedwars_data=bedwars_data_list,
        uuid=uuid,
        current_level=level,
        period=yesterday.strftime('daily_%Y_%m_%d')
    )
    await statalib.reset_tracker(
        uuid, tracker='daily', bedwars_data=bedwars_data_list)
    logger.debug(f'Reset daily tracker for: {uuid}')

    # reset weekly
    if timezone.weekday() == 6:
        statalib.save_historical(
            tracker='weekly',
            bedwars_data=bedwars_data_list,
            uuid=uuid,
            current_level=level,
            period=yesterday.strftime('weekly_%Y_%U')
        )
        await statalib.reset_tracker(
            uuid, tracker='weekly', bedwars_data=bedwars_data_list)
        logger.debug(f'Reset weekly tracker for: {uuid}')

    # reset monthly
    if timezone.day == 1:
        statalib.save_historical(
            tracker='monthly',
            bedwars_data=bedwars_data_list,
            uuid=uuid,
            current_level=level,
            period=yesterday.strftime('monthly_%Y_%m')
        )
        await statalib.reset_tracker(
            uuid, tracker='monthly', bedwars_data=bedwars_data_list)
        logger.debug(f'Reset monthly tracker for: {uuid}')

    # reset yearly
    if timezone.timetuple().tm_yday == 1:
        statalib.save_historical(
            tracker='yearly',
            bedwars_data=bedwars_data_list,
            uuid=uuid,
            current_level=level,
            period=yesterday.strftime('yearly_%Y')
        )
        await statalib.reset_tracker(
            uuid, tracker='yearly', bedwars_data=bedwars_data_list)
        logger.debug(f'Reset yearly tracker for: {uuid}')


@reset_trackers_loop.before_loop
async def before_reset_trackers_loop():
    await statalib.align_to_hour()


@reset_trackers_loop.error
async def on_reset_trackers_loop_error(error):
    reset_trackers_loop.restart()
    await statalib.log_error_msg(client, error)


if __name__ == '__main__':
    client.run(getenv('DISCORD_BOT_TOKEN'), root_logger=True)
