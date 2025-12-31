from typing import final
from datetime import datetime, UTC

import discord
import statalib as lib
from statalib.embeds import LeaderboardEmbeds
from discord import TextChannel, app_commands
from discord.ext import commands
from statalib.hypixel.lbs import LiveLeaderboardsRepo
from statalib.hypixel.lbs.models import GuildLiveLeaderboard, LEADERBOARD_TYPES

import helper


LOADING_EMOJI = "<a:loading1:1062561739989860462>"

@final
class LiveLeaderboardsCog(commands.Cog):
    def __init__(self, client: helper.Client):
        self.client = client

    live_lb_group = app_commands.Group(
        name="liveleaderboard",
        description="Manage leaderboard channels.",
        allowed_contexts=app_commands.AppCommandContext(
            guild=True, dm_channel=False, private_channel=True
        ),
        allowed_installs=app_commands.AppInstallationType(guild=True, user=False),
        default_permissions=discord.Permissions(discord.Permissions.manage_guild.flag)
    )

    lb_channel_group: app_commands.Group = app_commands.Group(
        name="channel",
        description="Manage leaderboard channels.",
        allowed_contexts=live_lb_group.allowed_contexts,
        allowed_installs=live_lb_group.allowed_installs,
        parent=live_lb_group,
    )


    async def remove_zombie_leaderboard(
        self,
        guild: discord.Guild,
        live_lb: GuildLiveLeaderboard
    ) -> None:
        channel = guild.get_channel(live_lb.channel_id)

        if channel is None:
            return

        if not isinstance(channel, TextChannel):
            return

        message = channel.get_partial_message(live_lb.message_id)
        try:
            await message.delete()
        except (discord.errors.NotFound, discord.errors.Forbidden):
            pass

    async def initialize_live_leaderboard_message(self, message: discord.Message, lb_path: str) -> None:
        embeds, files = await helper.leaderboards.generate_embeds_for_leaderboard_path(lb_path)
        content = f"Last updated <t:{int(datetime.now(UTC).timestamp())}:R>"
        _ = await message.edit(content=content, embeds=embeds, attachments=files)

    @lb_channel_group.command(
        name="set",
        description="Set the leaderboard channels.")
    @app_commands.choices(leaderboard=[
        app_commands.Choice(name=lb.title, value=lb.path)
        for lb in LEADERBOARD_TYPES.values()])
    async def set_leaderboard_channel(
        self,
        interaction: discord.Interaction,
        channel: TextChannel,
        leaderboard: app_commands.Choice[str],
    ) -> None:
        lb = leaderboard
        await interaction.response.defer(ephemeral=True)
        await helper.interactions.run_interaction_checks(interaction)

        if not (guild := interaction.guild):
            return

        existing_live_lb = await LiveLeaderboardsRepo.get_guild_live_lb(guild.id, lb.value)

        try:
            new_live_lb_msg = await channel.send(f"Initializing live leaderboard {LOADING_EMOJI}")
        except discord.errors.Forbidden:
            await interaction.followup.send(
                embed=LeaderboardEmbeds.missing_send_messages_permission(
                    self.client.user.id, channel.id))
            return

        lb_channel = GuildLiveLeaderboard(
            interaction.guild.id, channel.id, lb.value, new_live_lb_msg.id
        )

        _ = await LiveLeaderboardsRepo.set_live_leaderboard(lb_channel)
        await interaction.followup.send(
            embed=LeaderboardEmbeds.channel_initialized(channel.id, lb.name))

        # Remove old message and create new
        if existing_live_lb:
            await self.remove_zombie_leaderboard(guild, existing_live_lb)

        await self.initialize_live_leaderboard_message(new_live_lb_msg, lb.value)

        lib.usage.update_command_stats(interaction.user.id, "set_live_lb")

    @lb_channel_group.command(
        name="unset",
        description="Unset the leaderboard channels.",)
    @app_commands.choices(leaderboard=[
        app_commands.Choice(name=lb.title, value=lb.path)
        for lb in LEADERBOARD_TYPES.values()])
    async def unset_leaderboard_channel(
        self,
        interaction: discord.Interaction,
        leaderboard: app_commands.Choice[str],
    ) -> None:
        lb_path = leaderboard.value
        await interaction.response.defer(ephemeral=True)
        await helper.interactions.run_interaction_checks(interaction)

        if not (guild := interaction.guild):
            return

        existing_live_lb = await LiveLeaderboardsRepo.unset_live_leaderboard(guild.id, lb_path)

        if existing_live_lb is None:
            await interaction.followup.send(
                embed=LeaderboardEmbeds.no_leaderboard_channel_set(leaderboard.name))
            return
        else:
            await self.remove_zombie_leaderboard(guild, existing_live_lb)

        channel = interaction.guild.get_channel(existing_live_lb.channel_id)

        await interaction.followup.send(
            embed=LeaderboardEmbeds.terminated_live_leaderboard(
                channel.id if channel else None, leaderboard.name)
        )

        lib.usage.update_command_stats(interaction.user.id, "unset_live_lb")

    @lb_channel_group.command(
        name="list",
        description="List the leaderboard channels.",)
    async def list_leaderboard_channels(
        self,
        interaction: discord.Interaction,
    ) -> None:
        await interaction.response.defer(ephemeral=True)
        await helper.interactions.run_interaction_checks(interaction)

        if not interaction.guild:
            return

        live_lbs = await LiveLeaderboardsRepo.get_all_guild_live_lbs(interaction.guild.id)

        channels: dict[str | None, str] = {
            lb.title: "`Unset`" for lb in LEADERBOARD_TYPES.values()
        }

        for live_lb in live_lbs:
            c = interaction.guild.get_channel(live_lb.channel_id)

            lb_info = LEADERBOARD_TYPES.get(live_lb.leaderboard_path)
            if lb_info is None:
                continue
            
            if c is None:
                channels[lb_info.title] = "`Unknown Channel`"
                continue

            channels[lb_info.title] = c.mention

        
        await interaction.followup.send(embed=LeaderboardEmbeds.list_live_leaderboards(channels))

        lib.usage.update_command_stats(interaction.user.id, "list_live_lbs")


async def setup(client: helper.Client) -> None:
    await client.add_cog(LiveLeaderboardsCog(client))
