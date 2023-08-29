from os import getenv

from discord.ext import commands, tasks

from statalib import (
    get_linked_total,
    get_user_total,
    get_commands_total,
    get_config,
    log_error_msg
)


class Metrics(commands.Cog):
    def __init__(self, client):
        self.client: commands.Bot = client

        self.channels = {}


    async def get_channel(self, channel_id: int):
        channel = self.channels.get(channel_id)

        if not channel:
            await self.client.wait_until_ready()
            channel = self.client.get_channel(channel_id)
            self.channels[channel_id] = channel

        return channel


    async def update_channel_name(self, channel_name: str,
                                  channel_id: int):
        channel = await self.get_channel(channel_id)
        await channel.edit(name=channel_name)


    @tasks.loop(minutes=20)
    async def update_metrics_loop(self):
        await self.client.wait_until_ready()

        metrics = {
            'linked': get_linked_total(),
            'users': get_user_total(),
            'commands': get_commands_total(),
            'servers': len(self.client.guilds)
        }

        channels_config: dict = get_config()['metrics_channels']

        for key, value in metrics.items():
            channel_name = channels_config[key]['name']
            channel_name = channel_name.format(amount=f'{value:,}')

            # Allow for escaped unicode emojis
            channel_name = bytes(channel_name, 'utf-8').decode('unicode-escape')

            channel_id = channels_config[key]['id']

            await self.update_channel_name(channel_name, channel_id)


    @update_metrics_loop.error
    async def on_update_metrics_error(self, error):
        await log_error_msg(self.client, error)


    async def cog_load(self):
        if getenv('ENVIRONMENT') == 'production':
            self.update_metrics_loop.start()


    async def cog_unload(self):
        self.update_metrics_loop.cancel()


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Metrics(client))
