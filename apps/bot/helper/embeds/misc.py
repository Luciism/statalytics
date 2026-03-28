"""Miscellaneous embeds."""

from typing import Any

from discord import Embed
import statalib as lib
from statalib import PlayerName, PlayerUUID, config
from statalib.accounts import Subscription


class MiscEmbeds:
    """Miscellaneous embeds."""

    @staticmethod
    def credits() -> Embed:
        """Project credits embed."""
        embed = (
            Embed(
                title="Credits",
                description="Statalytics was made possible by the following:",
                color=config.embed_color("primary"),
            )
            .set_thumbnail(url="https://statalytics.net/image/branding/logo.png?v=2")
            .add_field(
                name="Lead Bot Developer",
                value="[lukism](https://github.com/Luciism)",
                inline=True,
            )
            .add_field(
                name="Community Manager",
                value="[caspuhh](https://github.com/casparml)",
                inline=True,
            )
            .add_field(name="", value="", inline=False)  # Spacer
            .add_field(
                name="Web Developers",
                value="[caspuhh](https://github.com/casparml)\n "
                + "[lukism](https://github.com/Luciism)",
                inline=True,
            )
            .add_field(
                name="Beta Testers",
                value="[caspuhh](https://github.com/casparml)\n"
                + "[polsulpicien](https://discordapp.com/users/647487369246801921)",
                inline=True,
            )
            .add_field(
                name="",
                value="Github Contributers: [click here]"
                + "(https://github.com/Luciism/statalytics/graphs/contributors)",
                inline=False,
            )
        )
        return embed

    @staticmethod
    def services_info(info: dict[str, Any]) -> Embed:
        """Services info embed."""
        devs = ", ".join(config("global.developers"))

        embed = (
            Embed(
                title="Statalytics Info",
                color=config.embed_color("primary"),
            )
            .set_thumbnail(url="https://statalytics.net/image/branding/logo.png?v=2")
            .add_field(
                name="Key Metrics",
                value=f"> Uptime: `{info['uptime']}`\n> Ping: `{info['ping']}ms`\n> Commands: "
                + f"`{info['commands']}`\n> Version: `{config('apps.bot.version')}`",
                inline=True,
            )
            .add_field(name="", value="", inline=True)
            .add_field(
                name="Bot Usage Stats",
                value=f"> Servers: `{info['servers']}`\n> Users: `{info['users']}`\n> Commands "
                + f"Ran: `{info['commands_ran']}`\n> Linked Users: `{info['linked_users']}`\n\u200b",
                inline=True,
            )
            .add_field(
                name="Specifications",
                value=f"> Devs: `{devs}`\n> Library: `discord.py`\n> Python: "
                + f"`{info['python_ver']}`\n> Shard Count: `{info['shard_count']}`",
                inline=True,
            )
            .add_field(name="", value="", inline=True)
            .add_field(
                name="Links",
                value=f"> [Invite]({config('global.links.invite_url')})\n"
                + f"> [Website](https://statalytics.net)\n"
                + f"> [Support]({config('global.links.support_server')})\n"
                + f"> [GitHub]({config('global.links.github')})",
                inline=True,
            )
        )
        return embed

    @staticmethod
    def player_skin(username: PlayerName, uuid: PlayerUUID) -> Embed:
        """Player skin display embed."""
        embed = Embed(
            title=f"{username}'s Skin",
            url=f"https://namemc.com/profile/{uuid}",
            description=f"Click [here](https://crafatar.com/skins/{uuid}) to download",
            color=config.embed_color("primary"),
        ).set_image(url="attachment://skin.png")
        return embed

    @staticmethod
    def suggestion_message(
        discord_username: str, discord_user_id: int, suggestion: str
    ) -> Embed:
        """User feature suggestion embed."""
        embed = Embed(
            title=f"Suggestion by {discord_username} ({discord_user_id})",
            color=config.embed_color("primary"),
        ).add_field(name="Suggestion", value=suggestion)
        return embed

    @staticmethod
    def voting_info(last_vote: str, total_votes: int) -> Embed:
        """User voting info embed."""
        vote_links = config("global.links.voting")

        rewards_duration = config.voter_rewards_duration

        free_tier_command_cooldown: dict[str, int] = Subscription.get_package_property(
            "free", "generic_command_cooldown")
        rate = free_tier_command_cooldown.get('rate', 1)
        per = free_tier_command_cooldown.get('per', 1)

        reduced_cooldown = round((per / rate) * 0.5, 2)
    
        embed = (
            Embed(
                title="Vote for Statalytics!",
                description="Voting helps Statalytics grow by increasing public exposure.",
                color=config.embed_color("primary"),
            )
            .set_thumbnail(url="https://statalytics.net/image/branding/logo.png?v=2")
            .add_field(
                name="Rewards",
                value=
                    f"For the next **{rewards_duration}** after you vote, you'll have:\n"
                    + f"- Access to all voter themes.\n"
                    + f"- Cooldowns reduced by 50% ({reduced_cooldown}s)\n\n"
                    + "*You can change your theme pack with `/settings`*",
                inline=False,
            )
            .add_field(
                name="Links",
                value=f"Vote on [top.gg]({vote_links['top.gg']})\n"
                + f"Vote on [discordbotlist.com]({vote_links['discordbotlist.com']})\n"
                + f"Vote on [discords.com]({vote_links['discords.com']})",
                inline=False,
            )
            .add_field(
                name="Your Voting History",
                value=f"Last Vote: {last_vote}\nTotal Votes: {total_votes}",
                inline=False,
            )
        )
        return embed
