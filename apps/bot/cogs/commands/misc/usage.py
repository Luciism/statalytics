import discord
from discord.ext import commands

import statalib as lib
import helper


class UsageCommandCog(commands.Cog):
    def build_embed(self, command_usage: list[tuple[str, int]]) -> discord.Embed:
        if not command_usage:
            return discord.Embed(
                title='No Command Usage!',
                description=
                    'You have no command usage stats as you have never run a command.',
                color=lib.config.embed_color('primary')
            )

        sorted_usage = sorted(
            command_usage,
            key=lambda x: x[1],
            reverse=True
        )

        usage_entries: list[str] = []

        for cmd_id, times_used in sorted_usage:
            try:
                command = lib.commands.get_command(cmd_id)
                command_name = ""

                if command.parent:
                    command_name += f"{command.parent} "

                command_name += command.name

            except lib.commands.CommandNotFoundError:
                command_name = "unknown"

            usage_entries.append(f'`/{command_name}` - `{times_used}`')

        total = sum([cmd[1] for cmd in command_usage])

        embed = discord.Embed(
            title="Your Command Usage",
            description=f"**Overall - {total}**",
            color=lib.config.embed_color('primary'))

        for i in range(0, len(usage_entries), 10):
            sublist = usage_entries[i:i+10]
            _ = embed.add_field(name='', value='\n'.join(sublist))

        return embed



    @helper.decorators.app_command("usage")
    @helper.interactions.access_permitted_check()
    async def usage_stats(self, interaction: discord.Interaction):
        await interaction.response.defer()

        with lib.db.db_connect() as conn:
            cursor = conn.cursor()

            command_usage = cursor.execute(
                "SELECT command_id, times_used FROM command_metrics "
                + "WHERE discord_user_id = ?", [interaction.user.id]
            ).fetchall()

        embed = self.build_embed(command_usage)
        await interaction.followup.send(embed=embed)


async def setup(client: helper.Client) -> None:
    await client.add_cog(UsageCommandCog())
