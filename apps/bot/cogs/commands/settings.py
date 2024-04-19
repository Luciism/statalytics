import discord
from discord import app_commands
from discord.ext import commands

import statalib as lib


HOURS = [
    '12am', '1am', '2am', '3am', '4am', '5am',
    '6am', '7am', '8am', '9am', '10am', '11am',
    '12pm', '1pm', '2pm', '3pm', '4pm', '5pm',
    '6pm', '7pm', '8pm', '9pm', '10pm', '11pm'
]


class SettingsSelect(discord.ui.Select):
    def __init__(self, placeholder, options, min_values, max_values):
        super().__init__(
            placeholder=placeholder,
            max_values=max_values,
            min_values=min_values,
            options=options
        )

        self.placeholder = placeholder


    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await lib.run_interaction_checks(interaction)

        discord_id = interaction.user.id

        value = self.values[0]
        if self.placeholder == "Select Theme":
            if value == 'none':
                value = None
            lib.set_active_theme(discord_id, value)
            await interaction.followup.send('Successfully updated theme!', ephemeral=True)
            return

        if self.placeholder in ('Select your GMT offset', 'Select your reset hour'):
            value = int(value)
            if self.placeholder == 'Select your GMT offset':
                lib.update_reset_time_configured(interaction.user.id, value, 'timezone')

                message = f'Successfully updated timezone to `GMT{lib.prefix_int(value)}:00`'
            else:
                lib.update_reset_time_configured(interaction.user.id, value, 'reset_hour')

                message = f'Successfully updated reset hour to `{HOURS[value]}`'

            await interaction.followup.send(message, ephemeral=True)
            return


class SettingsSelectView(lib.CustomBaseView):
    def __init__(self, interaction: discord.Interaction,
                 view_data: list | tuple, *, timeout=300):
        super().__init__(timeout=timeout)
        for view in view_data:
            self.add_item(
                SettingsSelect(view['placeholder'], view['options'],
                       view['min_values'], view['max_values']))

        self.interaction = interaction


    async def on_timeout(self) -> None:
        for child in self.children:
            child.disabled = True

        try:
            await self.interaction.edit_original_response(view=self)
        except discord.errors.NotFound:
            pass


class LinkAccountModal(lib.CustomBaseModal, title='Link Account'):
    player = discord.ui.TextInput(
        label='Player',
        placeholder='Statalytics',
        style=discord.TextStyle.short
    )

    async def on_submit(self, interaction: discord.Interaction):
        await lib.linking_interaction(interaction, str(self.player))


class SettingsButtons(lib.CustomBaseView):
    def __init__(self, interaction: discord.Interaction) -> None:
        super().__init__(timeout=300)
        self.interaction = interaction

    async def on_timeout(self) -> None:
        for child in self.children:
            child.disabled = True

        try:
            await self.interaction.edit_original_response(view=self)
        except discord.errors.NotFound:
            pass


    @discord.ui.button(
        label="Active Theme",
        style=discord.ButtonStyle.gray,
        custom_id="active_theme",
        row=1)
    async def active_theme(self, interaction: discord.Interaction,
                           button: discord.ui.Button):
        await lib.run_interaction_checks(interaction)

        embeds = lib.load_embeds('active_theme', color='primary')

        owned_themes = lib.get_owned_themes(interaction.user.id)
        theme_packs: dict = lib.config('global.theme_packs')

        # themes available to anyone through voting
        available_themes: dict = theme_packs['voter_themes']

        # owned exclusive themes
        for owned_theme in owned_themes:
            available_themes[owned_theme] = theme_packs['exclusive_themes'][owned_theme]

        options = [discord.SelectOption(label=properties.get('display_name'), value=name)
                   for name, properties in available_themes.items()]

        view_data = [{
            'placeholder': 'Select Theme',
            'options': options,
            'min_values': 1,
            'max_values': 1
        }]

        view = SettingsSelectView(interaction=interaction, view_data=view_data)
        await interaction.response.send_message(
            embeds=embeds, view=view, ephemeral=True)


    @discord.ui.button(
        label="Reset Time",
        style=discord.ButtonStyle.gray,
        custom_id="reset_time", row=1)
    async def reset_time(self, interaction: discord.Interaction,
                         button: discord.ui.Button):
        await lib.run_interaction_checks(interaction)

        embeds = lib.load_embeds('reset_time', color='primary')

        options_1 = [discord.SelectOption(
            label=f'GMT{lib.prefix_int(i-12)}', value=i-12)
            for i in reversed(range(25))]

        options_2 = [discord.SelectOption(label=hour, value=i)
                     for i, hour in zip(range(24), HOURS)]

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
            embeds=embeds,
            view=SettingsSelectView(interaction=interaction, view_data=view_data),
            ephemeral=True
        )


    @discord.ui.button(
        label="Linked Account",
        style=discord.ButtonStyle.gray,
        custom_id="linked_account", row=1)
    async def linked_account(self, interaction: discord.Interaction,
                             button: discord.ui.Button):
        await lib.run_interaction_checks(interaction)
        await interaction.response.send_modal(LinkAccountModal())



class Settings(commands.Cog):
    def __init__(self, client):
        self.client: commands.Bot = client

    @app_commands.command(
        name="settings",
        description="Edit your configuration for statalytics")
    async def settings(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await lib.run_interaction_checks(interaction)

        embeds = lib.load_embeds('settings', color='primary')
        await interaction.followup.send(
            embeds=embeds, view=SettingsButtons(interaction=interaction))

        lib.update_command_stats(interaction.user.id, 'settings')


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Settings(client))
