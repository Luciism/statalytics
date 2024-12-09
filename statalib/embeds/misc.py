"""Miscellaneous embeds."""

from typing import Any
from discord import Embed

from ..cfg import config
from ..aliases import PlayerName, PlayerUUID


class MiscEmbeds:
    """Miscellaneous embeds."""
    @staticmethod
    def credits() -> Embed:
        """Project credits embed."""
        embed = Embed(
            title="Credits",
            description="Statalytics was made possible by the following:",
            color=config.embed_color("primary"),
        )
        embed.set_thumbnail(url="https://statalytics.net/image/logo.png?v=2")
        embed.add_field(
            name="Lead Bot Developer",
            value="[lukism](https://github.com/Luciism)",
            inline=True)
        embed.add_field(
            name="Community Manager",
            value="[caspuhh](https://github.com/casparml)",
            inline=True)
        embed.add_field(name="", value="")  # Spacer
        embed.add_field(
            name="Web Engineers",
            value="[caspuhh](https://github.com/casparml)\n[lukism](https://github.com/Luciism)",
            inline=True)
        embed.add_field(name="", value="")  # Spacer
        embed.add_field(
            name="API Engineers",
            value="[caspuhh](https://github.com/casparml)\n[lukism](https://github.com/Luciism)",
            inline=True)
        return embed

    @staticmethod
    def services_info(info: dict[str, Any]) -> Embed:
        """Services info embed."""
        embed = Embed(
            title="Statalytics Info",
            color=config.embed_color("primary"),
        )
        embed.set_thumbnail(url="https://statalytics.net/image/logo.png?v=2")
        embed.add_field(
            name="Key Metrics",
            value=
                f"> Uptime: `{info['uptime']}`\n> Ping: `{info['ping']}`\n> Commands: "
                f"`{info['commands']}`\n> Version: `{config('apps.bot.version')}`",
            inline=True
        )
        embed.add_field(
            name="",
            value="",
            inline=True
        )
        embed.add_field(
            name="Bot Usage Stats",
            value=
                f"> Servers: `{info['servers']}`\n> Users: `{info['users']}`\n> Commands "
                f"Ran: `{info['commands_ran']}`\n> Linked Users: `{info['linked_users']}`\n\u200B",
            inline=True
        )
        devs = ', '.join(config("global.developers"))
        embed.add_field(
            name="Specifications",
            value=
                f"> Devs: `{devs}`\n> Library: `discord.py`\n> Python: "
                f"`{info['python_ver']}`\n> Shard Count: `{info['shard_count']}`",
            inline=True
        )
        embed.add_field(
            name="",
            value="",
            inline=True
        )
        embed.add_field(
            name="Links",
            value=
                f"> [Invite]({info['invite_url']})\n> [Website](https://statalytics.net)\n"
                f"> [Support]({config('global.links.support_server')})\n"
                "> [GitHub]({config('global.links.github')})",
            inline=True
        )
        return embed

    @staticmethod
    def support_server_rules() -> Embed:
        """Support server rules embed."""
        embed = Embed(
            title=":books: Server Rules",
            description=
                "`\u2022` No advertising other Discord servers or external websites.\n"
                "`\u2022` No spamming messages, emojis, or images in the chat.\n"
                "`\u2022` No NSFW content.\n"
                "`\u2022` No discrimination of any kind is tolerated.\n"
                "`\u2022` Do not share personal information about other users.\n"
                "`\u2022` Do not engage in toxic or disrespectful behavior towards others.\n"
                "`\u2022` You must follow Discord's Terms of Service and Community Guidelines.\n"
                "`\u2022` Use appropriate language in all channels, including voice channels.\n"
                "`\u2022` Do not impersonate other users, staff, or services.\n"
                "`\u2022` Follow any additional rules specific to certain channels.",
            color=config.embed_color("primary")
        )
        return embed

    @staticmethod
    def player_skin(username: PlayerName, uuid: PlayerUUID) -> Embed:
        """Player skin display embed."""
        embed = Embed(
            title=f"{username}'s Skin",
            url=f"https://namemc.com/profile/{uuid}",
            description=f"Click [here](https://crafatar.com/skins/{uuid}) to download",
            color=config.embed_color("primary")
        )
        embed.set_image(url="attachment://skin.png")
        return embed

    @staticmethod
    def hypixel_status(server_info: dict[str, Any]) -> list[Embed]:
        """Hypixel status info embed."""
        status_embed = Embed(
            "Hypixel Status",
            description=
                "Hypixel's current server information.\n\n"
                f"**` > ` Status**: `{server_info['status']}`\n"
                f"**` > ` IP**: **`{server_info['ip']}`**\n"
                f"**` > ` Version**: `{server_info['version']}`\n\n"
                f"**` > ` Updated**: <t:{server_info['updated_timestamp']}>",
            color=3092790
        )
        status_embed.set_footer(text="Powered by api.polsu.xyz")
        status_embed.set_thumbnail(
            url=f"https://api.polsu.xyz/assets/minecraft/server/icon/{server_info['ip']}.png")
        status_embed.set_image(
            url=f"https://api.polsu.xyz/assets/minecraft/server/map/{server_info['ip']}.png")

        ping_embed = Embed(
            "Ping",
            description=
                f"**` > ` Ping**: `{server_info['ping']}`\n\n"
                f"**` > ` Max**: `{server_info['max_ping']}`\n"
                f"**` > ` Average**: `{server_info['avg_ping']}`\n"
                f"**` > ` Min**: `{server_info['min_ping']}`",
            color=3092790
        )
        ping_embed.set_footer(text="UTC Time  -  Ping in ms (USA - Los Angeles)")
        ping_embed.set_image(
            url=f"https://api.polsu.xyz/assets/minecraft/server/ping/{server_info['ip']}.png")

        players_embed = Embed(
            "Players",
            description=
                f"**` > ` Players**: `{server_info['players']}` / `"
                f"{server_info['max_players']}`\n\n"
                f"**` > ` Peak**: `{server_info['peak_players']}`\n"
                f"**` > ` Average**: `{server_info['avg_players']}`\n"
                f"**` > ` Min**: `{server_info['min_players']}`",
            color=3092790
        )
        players_embed.set_image(
            url=f"https://api.polsu.xyz/assets/minecraft/server/players/{server_info['ip']}.png")

        return [status_embed, ping_embed, players_embed]

    @staticmethod
    def suggestion_message(
        discord_username: str,
        discord_user_id: int,
        suggestion: str
    ) -> Embed:
        """User feature suggestion embed."""
        embed = Embed(
            title=f"Suggestion by {discord_username} ({discord_user_id})",
            color=config.embed_color("primary")
        )
        embed.add_field(
            name="Suggestion",
            value=suggestion
        )
        return embed

    @staticmethod
    def voting_info(last_vote: str, total_votes: int) -> Embed:
        """User voting info embed."""
        embed = Embed(
            title="Vote for Statalytics!",
            description="Voting helps Statalytics grow by increasing public exposure.",
            color=config.embed_color("primary")
        )
        embed.set_thumbnail(url="https://statalytics.net/image/logo.png?v=2")
        vote_links = config('global.links.voting')
        embed.add_field(
            name="Links",
            value=
                f"Vote on [top.gg]({vote_links['top.gg']})\n"
                f"Vote on [discordbotlist.com]({vote_links['discordbotlist.com']})\n"
                f"Vote on [discords.com]({vote_links['discords.com']})",
            inline=True
        )
        embed.add_field(
            name="Rewards",
            value=
                "Theme packs for 24 hours.\n"
                "Cooldowns reduced by 50% (1.75s)\n\n"
                "*You can change your theme pack with `/settings`*",
            inline=True
        )
        embed.add_field(
            name="Your Voting History",
            value=
                f"Last Vote: {last_vote}\n"
                f"Total Votes: {total_votes}",
            inline=True
        )
        return embed
