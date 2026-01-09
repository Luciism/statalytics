"""Problem info embeds."""

import os

from discord import Embed
from statalib import config


class ProblemsEmbeds:
    """Problem info embeds."""

    @staticmethod
    def no_premium_2028() -> Embed:
        """User has no access to 2028 command."""
        embed = Embed(
            title="That player doesn't have premium!",
            description="In order to view stats for 2028, a [premium plan]"
            + "(https://statalytics.net/premium) is required!",
            color=config.embed_color("warning"),
        ).add_field(
            name="How does it work?",
            value="`-` You can view any player's stats for 2028 if you have a premium plan.\n"
            + "`-` You can view a player's stats for 2028 if they have a premium plan.",
            inline=True,
        )
        return embed

    @staticmethod
    def no_premium_yearly() -> Embed:
        """User has no access to yearly command."""
        embed = Embed(
            title="That player doesn't have premium!",
            description="In order to view yearly stats, a [premium plan]"
            + "(https://statalytics.net/premium) is required!",
            color=5793266,
        ).add_field(
            name="How does it work?",
            value="`-` You can view any player's yearly stats if you have a premium plan.\n"
            + "`-` You can view a player's yearly stats if they have a premium plan.",
            inline=True,
        )
        return embed

    @staticmethod
    def antisniper_connection_error() -> Embed:
        """Antisniper API connection error."""
        embed = Embed(
            title="Antisniper API Connection Error",
            description="There was an issue connecting to Antisniper's API! Please try again later.",
            color=config.embed_color("danger"),
        )
        return embed

    @staticmethod
    def user_blacklisted() -> Embed:
        """User cannot access command because they are blacklisted."""
        embed = Embed(
            title="You are blacklisted!",
            description="You are currently unable to access commands due "
            + "to an active blacklist on your account!",
            color=config.embed_color("danger"),
        )
        return embed

    @staticmethod
    def linking_error() -> Embed:
        """Hypixel Discord connection mismatch."""
        embed = Embed(
            title="Hypixel Discord Connection Mismatch!",
            description="To successfully link your account, please ensure that your Hypixel Discord "
            + "connection corresponds accurately with your current Discord tag.",
            color=config.embed_color("danger"),
        ).set_image(url="https://statalytics.net/static/gifs/link.gif")
        return embed

    @staticmethod
    def max_lookback_exceeded(max_lookback: int) -> Embed:
        """Maximum lookback exceeded."""
        embed = (
            Embed(
                title="Maximum lookback exceeded!",
                description="The maximum lookback for viewing that player's historical rotational "
                + f"stats is {max_lookback}!",
                color=config.embed_color("warning"),
            )
            .add_field(
                name="How it works:",
                value=f"`-` You can view history up to `{max_lookback}` days with yours or the "
                + "checked player's plan.\n"
                + "`-` You can view longer history if you or the checked player has a "
                + "premium plan.",
                inline=False,
            )
            .add_field(
                name="Limits",
                value="`-` Free tier maximum lookback - 30 days\n"
                + "`-` Basic tier maxmum lookback  - 60 days\n"
                + "`-` Pro tier maximum lookback - unlimited",
                inline=False,
            )
        )
        return embed

    @staticmethod
    def missing_permissions() -> Embed:
        """Insufficient user permissions."""
        embed = Embed(
            title="Missing permissions!",
            description="You do not have the required permissions to access this command!",
            color=config.embed_color("danger"),
        )
        return embed

