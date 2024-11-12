import asyncio
import logging
import time
import sqlite3
from datetime import datetime, timedelta, timezone, UTC
from os import getenv

from discord.ext import commands, tasks
from dotenv import load_dotenv

load_dotenv()

import statalib
from statalib import rotational_stats as rotational


root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
root_logger.addHandler(statalib.CustomTimedRotatingFileHandler(
    logs_dir=f"{statalib.REL_PATH}/logs/bot"
))

logger = logging.getLogger('statalytics.trackers')
logger.setLevel(logging.DEBUG)


"""
This query is designed to find data from the `rotational_info` table that
needs to be reset based on the reset times configured in the
`configured_reset_times` and `default_reset_times` tables. The query
uses `LEFT JOIN` to combine data from the `rotational_info`,
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

The result of the query is a set of rows from the `rotational_info` table
that meet the specified conditions. You can use this result set to
find and process data from the `rotational_info` table that needs to be
reset based on the configured reset times.

Please note that if a negative value is obtained from subtracting
timezone from reset_hour, it will be adjusted by adding 24 before
performing modulus operation. This ensures that negative numbers are
handled appropriately.
"""

query = """
SELECT DISTINCT rotational_info.uuid
FROM rotational_info
LEFT JOIN linked_accounts
  ON rotational_info.uuid = linked_accounts.uuid
LEFT JOIN configured_reset_times
  ON linked_accounts.discord_id = configured_reset_times.discord_id
LEFT JOIN default_reset_times
  ON rotational_info.uuid = default_reset_times.uuid
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


class Client(commands.AutoShardedBot):
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

    auto_reset_config: dict = \
        statalib.config('apps.bot.tracker_resetting.automatic') or {}

    utc_now = datetime.now(UTC)

    with statalib.db_connect() as conn:
        cursor = conn.cursor()

        cursor.execute(query, (utc_now.hour,))
        players_to_reset = cursor.fetchall()

    logger.info(f'Total trackers to reset: {len(players_to_reset) // 4}')

    for uuid in players_to_reset:
        uuid = uuid[0]

        # Prevent refetching data for multiple trackers
        if uuid in fetched_players:
            continue

        try:
            start_time = time.time()

            # Ensure user has access
            if not statalib.rotational_stats.has_auto_reset_access(
                    uuid, auto_reset_config):
                continue

            logger.info(f'Resetting trackers for: {uuid}')
            reset_time = rotational.get_dynamic_reset_time(uuid)

            # Get respective datatime object
            tz_now = datetime.now(timezone(timedelta(hours=reset_time.utc_offset)))
            tz_now.replace(hour=reset_time.reset_hour % 24)

            fetched_players.append(uuid)  # Prevent duplicate fetching

            hypixel_data = await statalib.fetch_hypixel_data_rate_limit_safe(
                uuid, attempts=15)  # Mildly important that it succeeds

            if not hypixel_data.get('success'):
                logger.warning(f"Hypixel request unsuccessful: {hypixel_data}")
                continue

            client.dispatch(
                'tracker_reset',
                uuid=uuid,
                hypixel_data=hypixel_data,
                timezone=tz_now
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
) -> None:
    """
    :param uuid: the uuid of the player whos trackers are being reset
    :param hypixel_data: the current hypixel data of the player
    :param timezone: the current time of the player's configured timezone
    """
    resetting = rotational.RotationalResetting(uuid)
    yesterday_dt = (timezone - timedelta(days=1))

    def reset_rotational(rotation_type: rotational.RotationType) -> None:
        try:
            snapshot_id = resetting.archive_rotational_data(
                period_id=rotational.HistoricalRotationPeriodID(
                    rotation_type, datetime_info=yesterday_dt),
                current_hypixel_data=hypixel_data
            )
            resetting.refresh_rotational_data(
                rotation_type=rotation_type, current_hypixel_data=hypixel_data)
        except sqlite3.IntegrityError:
            return logger.debug(
                f'Auto reset for {rotation_type.value} tracker failed. '
                f'UUID: {uuid} / Reason: historical data exists')

        logger.debug(
            f'Auto reset {rotation_type.value} tracker. '
            f'UUID: {uuid} / Snapshot ID: {snapshot_id}')

    reset_rotational(rotational.RotationType.DAILY)  # Reset daily

    if timezone.weekday() == 6:
        reset_rotational(rotational.RotationType.WEEKLY)  # Reset weekly

    if timezone.day == 1:
        reset_rotational(rotational.RotationType.MONTHLY)  # Reset monthly

    if timezone.timetuple().tm_yday == 1:
        reset_rotational(rotational.RotationType.YEARLY)  # Reset yearly


# @reset_trackers_loop.before_loop
# async def before_reset_trackers_loop():
#     await statalib.align_to_hour()


@reset_trackers_loop.error
async def on_reset_trackers_loop_error(error):
    reset_trackers_loop.restart()
    await statalib.log_error_msg(client, error)


if __name__ == '__main__':
    client.run(getenv('DISCORD_BOT_TOKEN'), root_logger=True)
