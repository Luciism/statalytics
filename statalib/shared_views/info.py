"""Help and info buttons / views."""

import discord

from ..embeds import Embeds
from .custom import CustomBaseView


class InfoButton(discord.ui.Button):
    """Base class for info buttons."""
    def __init__(
        self, label: str, embed: discord.Embed
    ) -> None:
        """
        Create a button which sends an embed upon being pressed.

        :param label: The label of the button component.
        :param embed: The embed object to send.
        """
        self.embed = embed

        emoji = discord.PartialEmoji(name='info_white', id=1128651261890285659)
        super().__init__(
            label=label, style=discord.ButtonStyle.gray,
            emoji=emoji, custom_id=f'{label.lower()}_info_button')

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(embed=self.embed, ephemeral=True)


class SessionInfoButton(CustomBaseView):
    """Session info button."""
    button = InfoButton('Sessions', Embeds.help.sessions())

    def __init__(self) -> None:
        super().__init__(timeout=None)
        self.add_item(self.button)

class ProjectionInfoButton(CustomBaseView):
    """Projection info button."""
    button = InfoButton('Projection', Embeds.help.projection())

    def __init__(self) -> None:
        super().__init__(timeout=None)
        self.add_item(self.button)

class ComparisonInfoButton(CustomBaseView):
    """Comparison info button."""
    button = InfoButton('Comparison', Embeds.help.compare())

    def __init__(self) -> None:
        super().__init__(timeout=None)
        self.add_item(self.button)

class RotationalInfoButton(CustomBaseView):
    """Rotational info button."""
    button = InfoButton('Rotational', Embeds.help.rotational())

    def __init__(self) -> None:
        super().__init__(timeout=None)
        self.add_item(self.button)

class LinkingInfoButton(CustomBaseView):
    """Linking info button."""
    button = InfoButton('Linking', Embeds.help.linking())

    def __init__(self) -> None:
        super().__init__(timeout=None)
        self.add_item(self.button)

class SettingsInfoButton(CustomBaseView):
    """Settings info button."""
    button = InfoButton('Settings', Embeds.help.settings())

    def __init__(self) -> None:
        super().__init__(timeout=None)
        self.add_item(self.button)

class OtherInfoButton(CustomBaseView):
    """Button that shows info on all other commands."""
    button = InfoButton('Other', Embeds.help.other())

    def __init__(self) -> None:
        super().__init__(timeout=None)
        self.add_item(self.button)

class RotationalResettingInfoButton(CustomBaseView):
    """Rotational resetting info button."""
    button = InfoButton('Rotational Resetting', Embeds.help.tracker_resetting())

    def __init__(self) -> None:
        super().__init__(timeout=None)
        self.add_item(self.button)

class HelpMenuButtons(CustomBaseView):
    """Help menu buttons view."""
    def __init__(self) -> None:
        super().__init__(timeout=None)
        self.add_item(SessionInfoButton.button)
        self.add_item(ProjectionInfoButton.button)
        self.add_item(ComparisonInfoButton.button)
        self.add_item(RotationalInfoButton.button)
        self.add_item(LinkingInfoButton.button)
        self.add_item(SettingsInfoButton.button)
        self.add_item(OtherInfoButton.button)


def add_info_view(client: discord.Client) -> None:
    """
    Add all info buttons and views to the Discord client for persistence.

    :param client: The Discord client.
    """
    client.add_view(SessionInfoButton())
    client.add_view(ProjectionInfoButton())
    client.add_view(ComparisonInfoButton())
    client.add_view(RotationalInfoButton())
    client.add_view(LinkingInfoButton())
    client.add_view(OtherInfoButton())
    client.add_view(RotationalResettingInfoButton())

    client.add_view(HelpMenuButtons())
