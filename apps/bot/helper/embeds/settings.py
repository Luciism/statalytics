"""Settings embeds."""

from discord import Embed
import statalib as lib
from statalib import config


class SettingsEmbeds:
    """Settings embeds."""

    @staticmethod
    def settings() -> Embed:
        """Settings menu embed."""
        embed = Embed(
            title="Configure your settings for Statalytics",
            description="Use the buttons below to customize your experience.",
            color=config.embed_color("primary"),
        )
        return embed

    @staticmethod
    def select_theme() -> Embed:
        """Select theme embed."""
        rewards_duration = config.voter_rewards_duration

        embed = Embed(
            title="Select a theme pack!",
            description="In order for your selected theme pack to take effect, " 
                + f"you must have voted for Statalytics in the past **{rewards_duration}**. "
                + "(Use `/vote`)\n\n "
                + "[Premium supporters](https://statalytics.net/premium) bypass this restriction.",
            color=config.embed_color("primary"),
        )
        return embed

    @staticmethod
    def configure_reset_time() -> Embed:
        """Configure reset time embed."""
        embed = Embed(
            title="Configure reset time",
            description="This will determine when your daily, weekly, monthly, and yearly stats "
            + "roll over.\nGMT offset - your timezone offset to Greenwich Mean Time\n"
            + "Reset hour - the hour which your rotational stats will rollover\n\nClick "
            + "[here](https://greenwichmeantime.com/current-time/) if you are unsure of "
            + "your GMT offset.",
            color=config.embed_color("primary"),
        )
        return embed
