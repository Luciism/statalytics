import discord
from discord.ext import commands

import statalib as lib
import helper


class UsageCommandCog(commands.Cog):
    def build_embed(self, command_usage, column_names: list[str]) -> discord.Embed:
        if not command_usage:
            return discord.Embed(
                title='No Command Usage!',
                description=
                'You have no command usage stats as you have never run a command.',
                color=lib.config.embed_color('primary')
            )

        usage_dict = {}

        for i, usage in enumerate(command_usage[1:]):
            if usage:
                usage_dict[column_names[i+1]] = usage

        overall = '**Overall - 0**'
        description = []

        sorted_usage = sorted(
            usage_dict.items(),
            key=lambda x: x[1],
            reverse=True
        )

        for key, value in sorted_usage:
            if key == 'overall':
                overall = f'**Overall - {value}**'
                continue
            command = lib.ASSET_LOADER.command_map.get(key, '/unknown')
            description.append(f'`{command}` - `{value}`')

        embed = discord.Embed(
            title="Your Command Usage", description=overall,
            color=lib.config.embed_color('primary'))

        for i in range(0, len(description), 10):
            sublist = description[i:i+10]
            embed.add_field(name='', value='\n'.join(sublist))

        return embed



    @helper.decorators.app_command("usage")
    @helper.interactions.access_permitted_check()
    async def usage_stats(self, interaction: discord.Interaction):
        await interaction.response.defer()

        discord_id = interaction.user.id

        with lib.db.db_connect() as conn:
            cursor = conn.cursor()

            command_usage = cursor.execute(
                f"SELECT * FROM command_usage WHERE discord_id = {discord_id}"
            ).fetchone()

            column_names = [desc[0] for desc in cursor.description]

        embed = self.build_embed(command_usage, column_names)
        await interaction.followup.send(embed=embed)


async def setup(client: helper.Client) -> None:
    await client.add_cog(UsageCommandCog())
