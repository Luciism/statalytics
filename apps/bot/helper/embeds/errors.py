"""Problem info embeds."""

import os

from discord import Embed
from statalib import config


class ErrorEmbeds:
    """Error info embeds."""

    @staticmethod
    def command_on_cooldown(retry_after: float) -> Embed:
        """Command is on cooldown."""
        embed = Embed(
            title="Command on cooldown!",
            description=f"Wait another `{retry_after}s` and try again!\n[Premium supporters]"
            + "(https://statalytics.net/premium) bypass this restriction.",
            color=config.embed_color("warning"),
        ).set_thumbnail(
            url="https://statalytics.net/static/images/cooldown_hourglass.png"
        )
        return embed

    @staticmethod
    def error_occured(command_name: str | None, error: str) -> Embed:
        """Generic error embed."""
        support_url = config("global.links.support_server")
        is_dev_mode = os.getenv("ENVIRONMENT").lower() == "development"

        embed = Embed(
            title=(
                f"An error occured while running /{command_name}!"
                if command_name
                else "An error occured while trying to complete your request."
            ),
            description=(
                "There was an error processing your request. Please try again later.\n"
                + f"If the problem persists, please [get in touch]({support_url})."
                + f"\n```{error}```"
                if is_dev_mode
                else ""
            ),
            color=config.embed_color("danger"),
        )
        return embed

    @staticmethod
    def hypixel_connection_error() -> Embed:
        """Hypixel API connection error."""
        embed = Embed(
            title="Hypixel API Connection Error",
            description="There was an issue connecting to Hypixel's API! Please try again later.",
            color=config.embed_color("danger"),
        )
        return embed

    @staticmethod
    def mojang_api_error() -> Embed:
        """Mojang API error."""
        embed = Embed(
            title="Mojang API Error",
            description="There was an issue fetching player information from Mojang's API.\n"
            + "Please try again in a moment!",
            color=config.embed_color("danger"),
        )
        return embed

