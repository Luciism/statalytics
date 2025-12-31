"""Leaderboard info embeds."""

from discord import Embed

from ..cfg import config


class LeaderboardEmbeds:
    """Leaderboard info embeds."""
    @staticmethod
    def missing_send_messages_permission(client_id: int, channel_id: int) -> Embed:
        """Bot is missing the `send_messages` permission required for leaderboards."""
        embed = Embed(
            title="Missing Permissions",
            description=
                f"<@{client_id}> is missing the `Send Messages` permission "
                + f"required for live leaderboards to work in <#{channel_id}>.",
            color=config.embed_color("danger"),
        )
        return embed

    @staticmethod
    def channel_initialized(channel_id: int, lb_title: str) -> Embed:
        """A live leaderboard channel was successfully initialized."""
        embed = Embed(
            title="Live Leaderboard Channel Initialized",
            description=
                f"The `{lb_title}` leaderboard has been initialized in <#{channel_id}>",
            color=config.embed_color("primary"),
        )
        return embed

    @staticmethod
    def no_leaderboard_channel_set(lb_title: str) -> Embed:
        """There is no live leaderboard channel set for the given leaderboard."""
        embed = Embed(
            title="No Live Leaderboard Channel",
            description=
                "There is not a live leaderboard channel that is " 
                + f"configured for the `{lb_title}` leaderboard.",
            color=config.embed_color("danger"),
        )
        return embed


    @staticmethod
    def terminated_live_leaderboard(channel_id: int | None, lb_title: str) -> Embed:
        """The live leaderboard was terminated successfully."""
        mention = f"<#{channel_id}>" if channel_id else "`Unknown Channel`"
        embed = Embed(
            title="Live Leaderboard Channel Unset",
            description=
                f"The channel {mention} is no longer attached to the `{lb_title}` "
                + "leaderboard and will no longer recieve leaderboard updates.",
            color=config.embed_color("primary"),
        )
        return embed

    @staticmethod
    def list_live_leaderboards(lb_channel_map: dict[str, str]) -> Embed:
        """List of live leaderboards in a guild."""
        embed = Embed(
            title="Configured Live Leaderboards",
            description="\n".join(f"{lb}: {ch}" for lb, ch in lb_channel_map.items()),
            color=config.embed_color("primary"),
        )
        return embed

