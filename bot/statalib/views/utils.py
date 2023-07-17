import discord


class LinkButton:
    def __init__(self, label, url, emoji=None) -> None:
        button = discord.ui.Button(label=label, url=url, emoji=emoji)
        self.view = discord.ui.View()
        self.view.add_item(button)
