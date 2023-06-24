import discord
from discord import app_commands
from discord.ext import commands

from helper.errors import MCUserNotFoundError
from helper.themes import get_owned_themes, set_active_theme
from helper.historical import update_reset_time_configured
from helper.linking import linking_interaction
from helper.functions import (
    update_command_stats,
    get_embed_color,
    get_config
)


HOURS = ['12am', '1am', '2am', '3am', '4am', '5am', '6am', '7am', '8am', '9am', '10am', '11am',
         '12pm', '1pm', '2pm', '3pm', '4pm', '5pm', '6pm', '7pm', '8pm', '9pm', '10pm', '11pm']


class Select(discord.ui.Select):
    def __init__(self, placeholder, options, min_values, max_values):
        super().__init__(placeholder=placeholder, max_values=max_values,
                         min_values=min_values, options=options)
        self.placeholder = placeholder


    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        discord_id = interaction.user.id

        value = self.values[0]
        if self.placeholder == "Select Theme":
            if value == 'none': value = None
            set_active_theme(discord_id, value)
            await interaction.followup.send('Successfully updated theme!', ephemeral=True)
            return

        if self.placeholder in ('Select your GMT offset', 'Select your reset hour'):
            method = 'timezone' if self.placeholder == 'Select your GMT offset' else 'reset_hour'
            update_reset_time_configured(interaction.user.id, value, method)

            if method == 'timezone':
                message = f'Successfully updated timezone to `GMT{"+" if int(value) >= 0 else ""}{value}:00`'
            else:
                message = f'Successfully updated reset hour to `{HOURS[int(value)]}`'
            await interaction.followup.send(message, ephemeral=True)
            return


class SelectView(discord.ui.View):
    def __init__(self, interaction: discord.Interaction, view_data: list | tuple, *, timeout=300):
        super().__init__(timeout=timeout)
        for view in view_data:
            self.add_item(
                Select(view['placeholder'], view['options'],
                       view['min_values'], view['max_values']))

        self.interaction = interaction


    async def on_timeout(self) -> None:
        for child in self.children:
            child.disabled = True

        await self.interaction.edit_original_response(view=self)


class LinkAccountModal(discord.ui.Modal, title='Link Account'):
    username = discord.ui.TextInput(label='Username', placeholder='Statalytics', style=discord.TextStyle.short)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            await linking_interaction(interaction, str(self.username))
        except MCUserNotFoundError:
            return


class SettingsButtons(discord.ui.View):
    def __init__(self, interaction: discord.Interaction) -> None:
        super().__init__(timeout=300)
        self.interaction = interaction

    async def on_timeout(self) -> None:
        for child in self.children:
            child.disabled = True
        await self.interaction.edit_original_response(view=self)


    @discord.ui.button(label="Active Theme", style=discord.ButtonStyle.gray, custom_id="active_theme", row=1)
    async def active_theme(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="Select a theme pack!",
            description="In order for your selected theme pack to take effect, you must have voted in the past 24 HOURS.\n\n [Premium](https://statalytics.net/store) users bypass this restriction.",
            color=get_embed_color('primary')
        )

        owned_themes = get_owned_themes(interaction.user.id)
        theme_packs: dict = get_config()['theme_packs']

        available_themes: dict = theme_packs['voter_themes']
        for owned_theme in owned_themes:
            available_themes[owned_theme] = theme_packs['exclusive_themes'][owned_theme]

        options = [discord.SelectOption(label=value, value=key) for key, value in available_themes.items()]
        view_data = [{
            'placeholder': 'Select Theme',
            'options': options,
            'min_values': 1,
            'max_values': 1
        }]
        view = SelectView(interaction=interaction, view_data=view_data)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


    @discord.ui.button(label="Reset Time", style=discord.ButtonStyle.gray, custom_id="reset_time", row=1)
    async def reset_time(self, interaction: discord.Interaction, button: discord.ui.Button):

        embed = discord.Embed(
            title='Configure reset time',
            description="""
                This will determine when your daily, weekly, monthly, and yearly stats roll over.
                GMT offset - your timezone offset to Greenwich Mean Time
                Reset hour - the hour which your historical stats will rollover

                Click [here](https://greenwichmeantime.com/current-time/) if you are unsure of your GMT offset.""".replace('    ', ''),
            color=get_embed_color('primary')
        )
        options_1 = [discord.SelectOption(label=f'GMT{"+" if i-12 >= 0 else ""}{i-12}', value=i-12) for i in reversed(range(25))]
        options_2 = [discord.SelectOption(label=hour, value=i) for i, hour in zip(range(24), HOURS)]
        view_data = [{
            'placeholder': 'Select your GMT offset',
            'options': options_1,
            'min_values': 1,
            'max_values': 1
        },
        {
            'placeholder': 'Select your reset hour',
            'options': options_2,
            'min_values': 1,
            'max_values': 1
        }]

        await interaction.response.send_message(
            embed=embed,
            view=SelectView(interaction=interaction, view_data=view_data),
            ephemeral=True
        )


    @discord.ui.button(label="Linked Account", style=discord.ButtonStyle.gray, custom_id="linked_account", row=1)
    async def linked_account(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(LinkAccountModal())


class Settings(commands.Cog):
    def __init__(self, client):
        self.client: discord.Client = client

    @app_commands.command(name="settings", description="Edit your configuration for statalytics")
    async def settings(self, interaction: discord.Interaction):
        await interaction.response.defer()
        embed_color = get_embed_color('primary')

        embed = discord.Embed(
            title='Configure your settings for Statalytics',
            description='Use the buttons below to customize your experience.',
            color=embed_color
        )
        await interaction.followup.send(embed=embed, view=SettingsButtons(interaction=interaction))

        update_command_stats(interaction.user.id, 'settings')


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Settings(client))
