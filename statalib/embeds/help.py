"""Embeds for the help menu."""

from discord import Embed

from ..cfg import config


class HelpEmbeds:
    """Embeds for the help menu."""
    @staticmethod
    def help() -> Embed:
        """Help menu embed."""
        embed = Embed(
            title="Statalytics Help Menu",
            description=
                "To get more information on the different features of statalytics, please "
                "navigate using the buttons below. Each button will go in depth on different "
                "functionality and how it works.",
            color=config.embed_color("primary")
        )
        return embed

    @staticmethod
    def compare() -> Embed:
        """Compare info embed."""
        embed = Embed(
            title="Stat Comparison Info Page",
            description=
                "- The Stat Comparison feature lets users compare the stats of two players."
                "\n- To use this feature, run the `/compare` command and provide the names "
                "of the two players.\n- If your account is linked, providing only one player "
                "will compare your stats with theirs.",
            color=config.embed_color("primary")
        )
        embed.add_field(
            name="**Commands:**",
            value="`/compare <player_1> [<player_2>]`"
        )
        return embed

    @staticmethod
    def linking() -> Embed:
        """Linking info embed."""
        embed = Embed(
            title="Stat Linking Info Page",
            description=
                "- Linking your account is a quality-of-life feature that offers several "
                "benefits.\n- You can use commands without specifying a player, manage your "
                "sessions, and more.\n- To link your account, make sure that your Discord "
                "account is connected to Hypixel with your current Discord tag.\n- Upon "
                "linking, if the target player does not already have an active session, one "
                "will be created automatically",
            color=config.embed_color("primary")
        )
        embed.add_field(
            name="**Commands:**",
            value="`/link <player>`\n`/unlink`"
        )
        return embed

    @staticmethod
    def projection() -> Embed:
        """Projection info embed."""
        embed = Embed(
            title="Stat Projection Info Page",
            description=
                "- The Bedwars Stat Projection feature predicts your stats at any given "
                "bedwrs star.\n- Projected stats uses session stats for accurate "
                "forecasting, so a long session is recommended for precise results.\n- You "
                "can specify a session for projections otherwise it will be dynamically "
                "determined.\n- The `/prestige` command gives a detailed breakdown of "
                "expected stats and dates.\n- The `/year 2026` command predicts your stats "
                "for the year 2026, giving a quick overview of your future performance in "
                "that year.",
            color=config.embed_color("primary")
        )
        embed.add_field(
            name="**Commands:**",
            value=
            "`/prestige [<prestige>] [<player>] [<session>]`\n`/year 2026 "
            "[<player>] [<session>]`\n`/year 2027 [<player>] [<session>]`"
        )
        return embed

    @staticmethod
    def rotational() -> Embed:
        """Rotational info embed."""
        embed = Embed(
            title="Rotational Stat Tracking Info Page",
            description=
                "- The `/daily`, `/weekly`, `/monthly`, and `/yearly` commands show your "
                "current stats for the respective rotation time periods. They reflect your "
                "performance in the ongoing day, week, month, or year.\n- The `/last` "
                "commands show your previous stats for the respective time periods. They "
                "summarize your performance in the completed day, week, month, or year.\n- "
                "The `/difference` command group shows the difference in your stats for the "
                "respective time periods. They compare your performance in the current day, "
                "week, month, or year to the previous one.\n- Adding a number after the "
                "`/last` commands shows the stats of a specific past period. For example, "
                "/lastweek 2 shows the stats of two weeks ago.",
            color=config.embed_color("primary")
        )
        embed.add_field(
            name="**Commands:**",
            value=
            "`/daily [<player>] [<session>]`\n`/weekly [<player>] [<session>]`\n`/monthly "
            "[<player>] [<session>]`\n`/yearly [<player>] [<session>]`\n\n`/lastday "
            "[<player>] [<days>]`\n`/lastweek [<player>] [<weeks>]`\n`/lastmonth "
            "[<player>] [<months>]`\n`/lastyear [<player>] [<years>]`\n\n`/difference "
            "daily [<player>] [<session>]`\n`/difference weekly [<player>] [<session>]`"
            "\n`/difference monthly [<player>] [<session>]`\n`/difference yearly "
            "[<player>] [<session>]`"
        )
        return embed

    @staticmethod
    def sessions() -> Embed:
        """Session info embed."""
        embed = Embed(
            title="Session Info Page",
            description=
                "- Sessions are used to track stats that can be factored into calculations "
                "for commands like `/prestige`, `/milestones`, and `/year 2026.\n- If a "
                "session is not specified in a session based command, the default session "
                "is the one with the lowest ID.\n- A new session will be automatically "
                "created for a player when they link to another player, if they do not have "
                "an existing session.\n- For `/milestones`, if a player has no session, no "
                "session is used. If a player has a session, the default session is used "
                "unless specified otherwise.\n- Specifying a session with the ID of 0 for "
                "`/milestones` will run the calculations without using a session.",
            color=config.embed_color("primary")
        )
        embed.add_field(
            name="**Commands:**",
            value=
            "`/session active`\n`/session start`\n`/session end [<session>]`\n`/session "
            "reset [<session>]`\n`/session stats [<session>] [<player>]`"
        )
        return embed

    @staticmethod
    def settings() -> Embed:
        """Settings info embed."""
        embed = Embed(
            title="Settings Info Page",
            description=
                "**Themes**\n- Themes are the background of the rendered image and can be "
                "unlocked by voting\n- Voter themes have a temporary access period after "
                "voting\n- Exclusive themes are available anytime for those who have unlocked "
                "them\n- A premium subscription unlocks all voter themes permanently but not "
                "all exclusive themes\n\n**Reset Times**\n- You can set a time for your "
                "tracked stats to reset by specifying a GMT offset and the desired reset "
                "hour. This allows you to configure reset times based on your local time, "
                "regardless of your location.\n- Discord-based reset times take priority "
                "over player-based reset times.\n- When a Discord account changes its reset "
                "time, any linked player's reset time will update to match.\n- Players are "
                "automatically assigned a random reset hour when their historical tracking is "
                "initiated.\n- Player-based reset times are used if a Discord-based reset time "
                "is not configured",
            color=config.embed_color("primary")
        )
        embed.add_field(
            name="**Commands:**",
            value="`/settings`"
        )
        return embed

    @staticmethod
    def other() -> Embed:
        """Other commands info embed."""
        embed = Embed(
            title="Misc Commands Info Page",
            description=
                "### Bedwars Stats Related\n`/milestones [<player>] [<session>]` - show "
                "milestone predictions for a player\n`/mostplayed [<player>]` - show most "
                "played modes as a bar plot\n`/winstreaks [<player>]` - show information on a "
                "player's bedwars winstreaks\n`/resources [<player>]` - show resource stats "
                "collected such as iron and gold\n`/pointless [<player>]` - show "
                "miscellaneous pointless bedwars stats\n`/practice [<player>]` - show "
                "practice stats such as bridging and fireball jumping\n`/bedwars [<player>]` "
                "- show a generic overview of the bedwars stats for a player\n`/average "
                "[<player>]` - show average stats and ratios per game and per star\n`/quests "
                "[<player>]` - view the quests stats of a player\n\n`/activecosmetics "
                "[<player>]` - show currently selected cosmetics for a player\n`/displayname "
                "[<player>]` - render bedwars display name with prefix and star\n`/hotbar "
                "[<player>]` - show hotbar layout preference for a player\n`/shop [<player>]` "
                "- show configured quickbuy layout for a player\n\n### Player Utilities\n"
                "`/who [<player>]` - convert username to uuid or vice versa\n`/skin "
                "[<player>]` - view or download the skin of a player\n\n### Bot Related\n"
                "`/vote` - get voting information and links\n`/info` - get metrics for "
                "statalytics such as uptime and latency",
            color=config.embed_color("primary")
        )
        return embed

    @staticmethod
    def tracker_resetting() -> Embed:
        """Rotational resetting info embed."""
        embed = Embed(
            title="How Rotational Stat Resetting Works",
            description=
                "Hypixel API changes and growth require a new, efficient rotational stats "
                "reset system for non-premium users. Automatic resets remain available for "
                "premium supporters.",
            color=config.embed_color("primary")
        )
        embed.add_field(
            name="User Prompted Resetting",
            value=
                "Command execution by users triggers API calls that fetch player stats. This "
                "data is reused to reset rotational stats, ensuring accuracy by only "
                "triggering resets periodically. One drawback of this approach is that "
                "resetting may not align to the beginning of days, weeks, months, etc.",
            inline=False
        )
        embed.add_field(
            name="Automatic Resetting",
            value=
                "This method, now only available to [premium supporters](https://statalytics.net/"
                "premium), automatically resets periodically at the beginning of every day, "
                "week, month, etc. User configured reset times are also taken into account.",
            inline=False
        )
        return embed
