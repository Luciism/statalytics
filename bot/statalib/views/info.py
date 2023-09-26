import discord

from ..functions import load_embeds
from .custom import CustomBaseView


class InfoButton(discord.ui.Button):
    def __init__(self, label: str, embed_file: str,
                 row: int=1, color: str='primary'):
        """
        Creates button which sends an embed upon being pressed
        :param label: the label of the button component
        :param embed_file: the filename of the embed json file
        :param row: the row for the button to appear on
        :param color: the color of the embed
        """
        self.embed_file = embed_file
        self.color = color

        emoji = discord.PartialEmoji(name='info_white', id=1128651261890285659)
        super().__init__(label=label, style=discord.ButtonStyle.gray,
                         emoji=emoji, row=row, custom_id=f'{label.lower()}_info_button')


    async def callback(self, interaction: discord.Interaction):
        embeds = load_embeds(self.embed_file, color=self.color)
        await interaction.response.send_message(embeds=embeds, ephemeral=True)


class SessionInfoButton(CustomBaseView):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(InfoButton('Sessions', 'help/sessions'))

class ProjectionInfoButton(CustomBaseView):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(InfoButton('Projection', 'help/projection'))

class ComparisonInfoButton(CustomBaseView):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(InfoButton('Comparison', 'help/compare'))

class HistoricalInfoButton(CustomBaseView):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(InfoButton('Historical', 'help/historical'))

class LinkingInfoButton(CustomBaseView):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(InfoButton('Linking', 'help/linking'))

class SettingsInfoButton(CustomBaseView):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(InfoButton('Settings', 'help/settings'))

class OtherInfoButton(CustomBaseView):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(InfoButton('Other', 'help/other'))


class HelpMenuButtons(CustomBaseView):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(InfoButton('Sessions', 'help/sessions', row=1))
        self.add_item(InfoButton('Projection', 'help/projection', row=1))
        self.add_item(InfoButton('Comparison', 'help/compare', row=1))
        self.add_item(InfoButton('Historical', 'help/historical', row=2))
        self.add_item(InfoButton('Linking', 'help/linking', row=2))
        self.add_item(InfoButton('Settings', 'help/settings', row=2))
        self.add_item(InfoButton('Other', 'help/other', row=2))


def add_info_view(client: discord.Client):
    client.add_view(SessionInfoButton())
    client.add_view(ProjectionInfoButton())
    client.add_view(ComparisonInfoButton())
    client.add_view(HistoricalInfoButton())
    client.add_view(LinkingInfoButton())
    client.add_view(OtherInfoButton())
    client.add_view(HelpMenuButtons())
