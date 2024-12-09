"""Problem info embeds."""

import os

from discord import Embed

from ..cfg import config


class ProblemsEmbeds:
    """Problem info embeds."""
    @staticmethod
    def no_premium_2026() -> Embed:
        """User has no access to 2026 command."""
        embed = Embed(
            title="That player doesn't have premium!",
            description=
                "In order to view stats for 2026, a [premium plan]"
                "(https://statalytics.net/premium) is required!",
            color=config.embed_color("warning"),
        )
        embed.add_field(
            name="How does it work?",
            value=
                "`-` You can view any player's stats for 2026 if you have a premium plan.\n"
                "`-` You can view a player's stats for 2026 if they have a premium plan.",
            inline=True
        )
        return embed

    @staticmethod
    def no_premium_yearly() -> Embed:
        """User has no access to yearly command."""
        embed = Embed(
            title="That player doesn't have premium!",
            description=
                "In order to view yearly stats, a [premium plan]"
                "(https://statalytics.net/premium) is required!",
            color=5793266,
        )
        embed.add_field(
            name="How does it work?",
            value=
                "`-` You can view any player's yearly stats if you have a premium plan.\n"
                "`-` You can view a player's yearly stats if they have a premium plan.",
            inline=True
        )
        return embed

    @staticmethod
    def antisniper_connection_error() -> Embed:
        """Antisniper API connection error."""
        embed = Embed(
            title="Antisniper API Connection Error",
            description=
                "There was an issue connecting to Antisniper's API! Please try again later.",
            color=config.embed_color("danger")
        )
        return embed

    @staticmethod
    def user_blacklisted() -> Embed:
        """User cannot access command because they are blacklisted."""
        embed = Embed(
            title="You are blacklisted!",
            description=
                "You are currently unable to access commands due "
                "to an active blacklist on your account!",
            color=config.embed_color("danger")
        )
        return embed

    @staticmethod
    def command_on_cooldown(retry_after: float) -> Embed:
        """Command is on cooldown."""
        embed = Embed(
            title="Command on cooldown!",
            description=
                f"Wait another `{retry_after}` and try again!\n[Premium supporters]"
                "(https://statalytics.net/premium) bypass this restriction.",
            color=config.embed_color("warning")
        )
        embed.set_thumbnail(url="https://statalytics.net/static/images/cooldown_hourglass.png")
        return embed

    @staticmethod
    def error_occured(command_name: str | None, error: str) -> Embed:
        """Generic error embed."""
        support_url = config("global.links.support_server")
        is_dev_mode = os.getenv("ENVIRONMENT").lower() == "development"

        embed = Embed(
            title=
                f"An error occured while running /{command_name}!"
                if command_name else
                "An error occured while trying to complete your request.",
            description=
                "There was an error processing your request. Please try again later.\n"
                f"If the problem persists, please [get in touch]({support_url})"
                + f"\n```{error}```" if is_dev_mode else "",
            color=config.embed_color("danger")
        )
        return embed

    @staticmethod
    def hypixel_connection_error() -> Embed:
        """Hypixel API connection error."""
        embed = Embed(
            title="Hypixel API Connection Error",
            description=
                "There was an issue connecting to Hypixel's API! Please try again later.",
            color=config.embed_color("danger")
        )
        return embed

    @staticmethod
    def linking_error() -> Embed:
        """Hypixel Discord connection mismatch."""
        embed = Embed(
            title="Hypixel Discord Connection Mismatch!",
            description=
                "To successfully link your account, please ensure that your Hypixel Discord "
                "connection corresponds accurately with your current Discord tag.",
            color=config.embed_color("danger")
        )
        embed.set_image(url="https://statalytics.net/static/gifs/link.gif")
        return embed

    @staticmethod
    def max_lookback_exceeded(max_lookback: int) -> Embed:
        """Maximum lookback exceeded."""
        embed = Embed(
            title="Maximum lookback exceeded!",
            description=
                "The maximum lookback for viewing that player's historical rotational "
                f"stats is {max_lookback}!",
            color=config.embed_color("warning")
        )
        embed.add_field(
            name="How it works:",
            value=
                f"`-` You can view history up to `{max_lookback}` days with yours or the "
                "checked player's plan.\n"
                "`-` You can view longer history if you or the checked player has a "
                "premium plan.",
            inline=True
        )
        embed.add_field(
            name="Limits",
            value=
                "`-` Free tier maximum lookback - 30 days\n"
                "`-` Basic tier maxmum lookback  - 60 days\n"
                "`-` Pro tier maximum lookback - unlimited",
            inline=True
        )
        return embed

    @staticmethod
    def missing_permissions() -> Embed:
        """Insufficient user permissions."""
        embed = Embed(
            title="Missing permissions!",
            description="You do not have the required permissions to access this command!",
            color=config.embed_color("danger")
        )
        return embed

    @staticmethod
    def mojang_api_error() -> Embed:
        """Mojang API error."""
        embed = Embed(
            title="Mojang API Error",
            description=
                "There was an issue fetching player information from Mojang's API.\n"
                "Please try again in a moment!",
            color=config.embed_color("danger")
        )
        return embed
