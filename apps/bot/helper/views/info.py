"""Help and info buttons / views."""

import discord

from ..embeds import Embeds
from ._custom import CustomBaseView


class InfoButton(discord.ui.Button):
    """Base class for info buttons."""

    def __init__(
        self, label: str, embed: discord.Embed, docs_url: str | None = None
    ) -> None:
        """
        Create a button which sends an embed upon being pressed.

        :param label: The label of the button component.
        :param embed: The embed object to send.
        """
        self.embed = embed
        self.docs_url = docs_url

        emoji = discord.PartialEmoji(name="info_white", id=1128651261890285659)
        super().__init__(
            label=label,
            style=discord.ButtonStyle.gray,
            emoji=emoji,
            custom_id=f"{label.lower()}_info_button",
        )

    async def callback(self, interaction: discord.Interaction):
        view = discord.ui.View()
        if self.docs_url is not None:
            docs_btn = discord.ui.Button(
                label="Docs Reference",
                url=self.docs_url,
                emoji="<:docs:1325495671272374272>",
            )
            view.add_item(docs_btn)
        await interaction.response.send_message(
            embed=self.embed, view=view, ephemeral=True
        )


class SessionInfoButton(CustomBaseView):
    """Session info button."""

    @staticmethod
    def button():
        return InfoButton(
            "Sessions",
            Embeds.help.sessions(),
            "https://docs.statalytics.net/features/session-stats/",
        )

    def __init__(self) -> None:
        super().__init__(timeout=None)
        _ = self.add_item(self.button())


class ProjectionInfoButton(CustomBaseView):
    """Projection info button."""

    @staticmethod
    def button():
        return InfoButton(
            "Projection",
            Embeds.help.projection(),
            "https://docs.statalytics.net/features/projection/",
        )

    def __init__(self) -> None:
        super().__init__(timeout=None)
        _ = self.add_item(self.button())


class ComparisonInfoButton(CustomBaseView):
    """Comparison info button."""

    @staticmethod
    def button():
        return InfoButton(
            "Comparison",
            Embeds.help.compare(),
            "https://docs.statalytics.net/features/other-bedwars-commands/#stat-comparison",
        )

    def __init__(self) -> None:
        super().__init__(timeout=None)
        _ = self.add_item(self.button())


class RotationalInfoButton(CustomBaseView):
    """Rotational info button."""

    @staticmethod
    def button():
        return InfoButton(
            "Rotational",
            Embeds.help.rotational(),
            "https://docs.statalytics.net/features/rotational-stats/",
        )

    def __init__(self) -> None:
        super().__init__(timeout=None)
        _ = self.add_item(self.button())


class LinkingInfoButton(CustomBaseView):
    """Linking info button."""

    @staticmethod
    def button():
        return InfoButton(
            "Linking",
            Embeds.help.linking(),
            "https://docs.statalytics.net/settings/linking/",
        )

    def __init__(self) -> None:
        super().__init__(timeout=None)
        _ = self.add_item(self.button())


class SettingsInfoButton(CustomBaseView):
    """Settings info button."""

    @staticmethod
    def button():
        return InfoButton(
            "Settings",
            Embeds.help.settings(),
            "https://docs.statalytics.net/settings/linking",
        )

    def __init__(self) -> None:
        super().__init__(timeout=None)
        _ = self.add_item(self.button())


class OtherInfoButton(CustomBaseView):
    """Button that shows info on all other commands."""

    @staticmethod
    def button():
        return InfoButton(
            "Other",
            Embeds.help.other(),
            "https://docs.statalytics.net/features/other-bedwars-commands/",
        )

    def __init__(self) -> None:
        super().__init__(timeout=None)
        _ = self.add_item(self.button())


class RotationalResettingInfoButton(CustomBaseView):
    """Rotational resetting info button."""

    @staticmethod
    def button():
        return InfoButton(
            "Rotational Resetting",
            Embeds.help.tracker_resetting(),
            "https://docs.statalytics.net/features/rotational-stats/",
        )

    def __init__(self) -> None:
        super().__init__(timeout=None)
        _ = self.add_item(self.button())


class LeaderboardsInfoButton(CustomBaseView):
    """Leaderboards info button."""

    @staticmethod
    def button():
        return InfoButton(
            "Leaderboards",
            Embeds.help.leaderboards(),
            "https://docs.statalytics.net/features/leaderboards/",  # TODO
        )

    def __init__(self) -> None:
        super().__init__(timeout=None)
        _ = self.add_item(self.button())


class HelpMenuButtons(CustomBaseView):
    """Help menu buttons view."""

    def __init__(self) -> None:
        super().__init__(timeout=None)
        _ = (
            self.add_item(LeaderboardsInfoButton.button())
            .add_item(SessionInfoButton.button())
            .add_item(ProjectionInfoButton.button())
            .add_item(ComparisonInfoButton.button())
            .add_item(RotationalInfoButton.button())
            .add_item(LinkingInfoButton.button())
            .add_item(SettingsInfoButton.button())
            .add_item(OtherInfoButton.button())
        )


def add_info_view(client: discord.Client) -> None:
    """
    Add all info buttons and views to the Discord client for persistence.

    :param client: The Discord client.
    """
    client.add_view(LeaderboardsInfoButton())
    client.add_view(SessionInfoButton())
    client.add_view(ProjectionInfoButton())
    client.add_view(ComparisonInfoButton())
    client.add_view(RotationalInfoButton())
    client.add_view(LinkingInfoButton())
    client.add_view(OtherInfoButton())
    client.add_view(RotationalResettingInfoButton())

    client.add_view(HelpMenuButtons())
