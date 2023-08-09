from calendar import monthrange
from datetime import datetime
from os import getenv
from typing import Callable

from discord.ext import commands, tasks

from dotenv import load_dotenv
load_dotenv()

from statalib import (
    reset_historical,
    align_to_hour,
    log_error_msg
)


class Client(commands.Bot):
    def __init__(self):
        super().__init__(intents=None, command_prefix='$')

    async def on_ready(self):
        print(f'Logged in as {client.user} (ID: {client.user.id})\n------')

    async def setup_hook(self) -> None:
        reset_daily.start()
        reset_weekly.start()
        reset_monthly.start()
        reset_yearly.start()

client = Client()


@client.tree.error
async def on_tree_error(interaction, error):
    return

@client.event
async def on_command_error(ctx, error):
    return


@tasks.loop(hours=1)
async def reset_daily():
    condition: Callable[[datetime], bool] = \
        lambda _: True

    await reset_historical(
        tracker='daily',
        period_format='daily_%Y_%m_%d',
        condition=condition,
        client=client
    )


@tasks.loop(hours=1)
async def reset_weekly():
    utc_now = datetime.utcnow()
    if not utc_now.weekday() in (5, 6, 0):
        return

    condition: Callable[[datetime], bool] = \
        lambda timezone: timezone.weekday() == 6

    await reset_historical(
        tracker='weekly',
        period_format='weekly_%Y_%U',
        condition=condition,
        client=client
    )


@tasks.loop(hours=1)
async def reset_monthly():
    utc_now = datetime.utcnow()
    month_len = monthrange(utc_now.year, utc_now.month)[1]
    # allows for a 3 day reset period (last, first, second)
    if not utc_now.day in (1, 2) and not utc_now.day == month_len:
        return

    condition: Callable[[datetime], bool] = \
        lambda timezone: timezone.day == 1

    await reset_historical(
        tracker='monthly',
        period_format='monthly_%Y_%m',
        condition=condition,
        client=client
    )


@tasks.loop(hours=1)
async def reset_yearly():
    utc_now = datetime.utcnow()
    if not utc_now.timetuple().tm_yday in (1, 2, 365, 366):
        return

    condition: Callable[[datetime], bool] = \
        lambda timezone: timezone.timetuple().tm_yday == 1

    await reset_historical(
        tracker='yearly',
        period_format='yearly_%Y',
        condition=condition,
        client=client
    )


@reset_daily.before_loop
@reset_weekly.before_loop
@reset_monthly.before_loop
@reset_yearly.before_loop
async def before_resetting():
    await align_to_hour()


@reset_daily.error
@reset_weekly.error
@reset_monthly.error
@reset_yearly.error
async def on_reset_error(error):
    await log_error_msg(client, error)


if __name__ == '__main__':
    client.run(getenv('BOT_TOKEN'))
