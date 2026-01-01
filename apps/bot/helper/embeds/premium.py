"""Premium info embeds."""

from discord import Embed
from statalib import config


class PremiumEmbeds:
    """Premium info embeds."""

    @staticmethod
    def premium() -> Embed:
        """Premium info embed."""
        embed = Embed(
            title="Statalytics Premium",
            description="Statalytics offers a set of premium plans that offer a range of extended "
            + "functionality and customizability.\n\nUse the buttons below for information "
            + "on the available premium tiers.",
            url="https://statalytics.net/premium",
            color=config.embed_color("primary"),
        )
        return embed

    @staticmethod
    def pro() -> Embed:
        """Pro package info embed."""
        embed = (
            Embed(
                title="Statalytics Pro (Tier 2)",
                url="https://statalytics.net/premium",
                color=config.embed_color("primary"),
            )
            .add_field(
                name="Past, present, and future stats",
                value="- Auto Rotational Resets - rotational stats automatically rollover "
                + "daily/weekly/etc.\n- Yearly Stats - view your own or another player's "
                + "yearly rotational stats.\n- 2027 Stats - predict your own or another "
                + "player's stats for the year 2027.\n- Infinite Historical Lookback - view "
                + "historical rotational stats with no limits.\n- Up to 5 Active Sessions - "
                + "activate up to 5 sessions at one time.",
                inline=False,
            )
            .add_field(
                name="Customizability, ease of access, misc",
                value="- Custom Backgrounds - upload your own images to be used in image renders.\n"
                + "- Unlock All Themes - get instant access to all voter themes without voting.\n"
                + "- No Command Cooldowns - remove cooldowns on commands ran.\n"
                + "- Username Autocomplete - be added to the username autocomplete options.\n"
                + "- Beta Access - access and give feedback on up and coming beta features.",
                inline=False,
            )
        )
        return embed

    @staticmethod
    def basic() -> Embed:
        """Basic package info embed."""
        embed = (
            Embed(
                title="Statalytics Basic (Tier 1)",
                url="https://statalytics.net/premium",
                color=config.embed_color("primary"),
            )
            .add_field(
                name="Past, present, and future stats",
                value="- Yearly Stats - view your own or another player's yearly rotational stats.\n"
                + "- 2027 Stats - predict your own or another player's stats for the year 2027."
                + "\n- 60 Day Historical Lookback - view historical rotational stats with a 60 "
                + "day limit.\n- Up to 3 Active Sessions - activate up to 3 sessions at one "
                + "time.",
                inline=False,
            )
            .add_field(
                name="Customizability, ease of access, misc",
                value="- Unlock All Themes - get instant access to all voter themes without voting."
                + "\n- No Command Cooldowns - remove cooldowns on commands ran.\n"
                + "- Username Autocomplete - be added to the username autocomplete options.",
                inline=False,
            )
        )
        return embed
