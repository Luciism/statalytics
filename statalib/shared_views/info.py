"""Help and info buttons / views."""

import discord

from ..functions import load_embeds
from .custom import CustomBaseView


class InfoButton(discord.ui.Button):
    """Base class for info buttons."""
    def __init__(
        self, label: str, embed_file: str, row: int=1, color: str='primary'
    ) -> None:
        """
        Create a button which sends an embed upon being pressed.

        :param label: The label of the button component.
        :param embed_file: The filename of the embed JSON file to send.
        :param row: The row for the button to appear on the view.
        :param color: The color of the embed.
        """
        self.embed_file = embed_file
        self.color = color

        emoji = discord.PartialEmoji(name='info_white', id=1128651261890285659)
        super().__init__(
            label=label, style=discord.ButtonStyle.gray,
            emoji=emoji, row=row, custom_id=f'{label.lower()}_info_button')


    async def callback(self, interaction: discord.Interaction):
        embeds = load_embeds(self.embed_file, color=self.color)
        await interaction.response.send_message(embeds=embeds, ephemeral=True)


class SessionInfoButton(CustomBaseView):
    """Session info button."""
    def __init__(self) -> None:
        super().__init__(timeout=None)
        self.add_item(InfoButton('Sessions', 'help/sessions'))

class ProjectionInfoButton(CustomBaseView):
    """Projection info button."""
    def __init__(self) -> None:
        super().__init__(timeout=None)
        self.add_item(InfoButton('Projection', 'help/projection'))

class ComparisonInfoButton(CustomBaseView):
    """Comparison info button."""
    def __init__(self) -> None:
        super().__init__(timeout=None)
        self.add_item(InfoButton('Comparison', 'help/compare'))

class RotationalInfoButton(CustomBaseView):
    """Rotational info button."""
    def __init__(self) -> None:
        super().__init__(timeout=None)
        self.add_item(InfoButton('Rotational', 'help/rotational'))

class LinkingInfoButton(CustomBaseView):
    """Linking info button."""
    def __init__(self) -> None:
        super().__init__(timeout=None)
        self.add_item(InfoButton('Linking', 'help/linking'))

class SettingsInfoButton(CustomBaseView):
    """Settings info button."""
    def __init__(self) -> None:
        super().__init__(timeout=None)
        self.add_item(InfoButton('Settings', 'help/settings'))

class OtherInfoButton(CustomBaseView):
    """Button that shows info on all other commands."""
    def __init__(self) -> None:
        super().__init__(timeout=None)
        self.add_item(InfoButton('Other', 'help/other'))

class TrackerResettingInfoButton(CustomBaseView):
    """Tracker resetting info button."""
    def __init__(self) -> None:
        super().__init__(timeout=None)
        self.add_item(InfoButton('Historical Resetting', 'tracker_resetting'))

class HelpMenuButtons(CustomBaseView):
    """Help menu buttons view."""
    def __init__(self) -> None:
        super().__init__(timeout=None)
        self.add_item(InfoButton('Sessions', 'help/sessions', row=1))
        self.add_item(InfoButton('Projection', 'help/projection', row=1))
        self.add_item(InfoButton('Comparison', 'help/compare', row=1))
        self.add_item(InfoButton('Rotational', 'help/rotational', row=2))
        self.add_item(InfoButton('Linking', 'help/linking', row=2))
        self.add_item(InfoButton('Settings', 'help/settings', row=2))
        self.add_item(InfoButton('Other', 'help/other', row=2))


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
    client.add_view(HelpMenuButtons())
    client.add_view(TrackerResettingInfoButton())
