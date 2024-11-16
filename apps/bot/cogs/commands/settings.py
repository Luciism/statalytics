from abc import abstractmethod

import discord
from discord import app_commands
from discord.ext import commands

import statalib as lib
from statalib import rotational_stats as rotational
import helper


HOURS = [
    '12am', '1am', '2am', '3am', '4am', '5am',
    '6am', '7am', '8am', '9am', '10am', '11am',
    '12pm', '1pm', '2pm', '3pm', '4pm', '5pm',
    '6pm', '7pm', '8pm', '9pm', '10pm', '11pm'
]

MINUTES = [0, 15, 30, 45]


class ActiveThemeSelect(discord.ui.Select):
    def __init__(self, options: list[discord.SelectOption]):
        super().__init__(
            placeholder='Select Theme', max_values=1, min_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await helper.interactions.run_interaction_checks(interaction)

        discord_id = interaction.user.id
        selection = self.values[0]

        if selection == 'none':
            selection = None

        lib.set_active_theme(discord_id, selection)
        await interaction.followup.send('Theme updated successfully!', ephemeral=True)


class _ResetTimeSelectBase(discord.ui.Select):
    def __init__(self, options: list[discord.SelectOption], placeholder: str):
        super().__init__(
            placeholder=placeholder,
            max_values=1, min_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await helper.interactions.run_interaction_checks(interaction)

        manager = lib.rotational_stats.ConfiguredResetTimeManager(interaction.user.id)
        message = self.make_updates(manager, int(self.values[0]))

        await interaction.followup.send(message, ephemeral=True)

    @abstractmethod
    def make_updates(
        self, manager: rotational.ConfiguredResetTimeManager, selection: int
    ) -> str: ...

class UTCOffsetSelect(_ResetTimeSelectBase):
    def make_updates(
        self, manager: rotational.ConfiguredResetTimeManager, selection: int
    ) -> str:
        manager.update(lib.rotational_stats.ResetTime(utc_offset=selection))
        return f'Timezone updated to **GMT{lib.prefix_int(selection)}:00**'

class ResetHourSelect(_ResetTimeSelectBase):
    def make_updates(
        self, manager: rotational.ConfiguredResetTimeManager, selection: int
    ) -> str:
        manager.update(lib.rotational_stats.ResetTime(reset_hour=selection))
        fmted_time = lib.format_12hr_time(selection, manager.get().reset_minute)
        return f'Reset time updated to **{fmted_time}**.'

class ResetMinuteSelect(_ResetTimeSelectBase):
    def make_updates(
        self, manager: rotational.ConfiguredResetTimeManager, selection: int
    ) -> str:
        manager.update(lib.rotational_stats.ResetTime(reset_minute=selection))
        fmted_time = lib.format_12hr_time(manager.get().reset_hour, selection)
        return f'Reset time updated to **{fmted_time}**.'


class SettingsSelectView(lib.shared_views.CustomBaseView):
    def __init__(
        self,
        interaction: discord.Interaction,
        *,
        timeout=300
    ) -> None:
        super().__init__(timeout=timeout)
        self.interaction = interaction


    async def on_timeout(self) -> None:
        for child in self.children:
            child.disabled = True

        try:
            await self.interaction.edit_original_response(view=self)
        except discord.errors.NotFound:
            pass


class LinkAccountModal(lib.shared_views.CustomBaseModal, title='Link Account'):
    player = discord.ui.TextInput(
        label='Player',
        placeholder='Statalytics',
        style=discord.TextStyle.short
    )

    async def on_submit(self, interaction: discord.Interaction):
        await helper.interactions.linking_interaction(interaction, str(self.player))


class SettingsButtons(lib.shared_views.CustomBaseView):
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
        label="Active Theme", style=discord.ButtonStyle.gray,
        custom_id="active_theme", row=1)
    async def active_theme(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        await helper.interactions.run_interaction_checks(interaction)

        embeds = lib.load_embeds('active_theme', color='primary')

        owned_themes = lib.get_owned_themes(interaction.user.id)
        theme_packs: dict = lib.config('global.theme_packs')

        # themes available to anyone through voting
        available_themes: dict = theme_packs['voter_themes']

        # owned exclusive themes
        for owned_theme in owned_themes:
            available_themes[owned_theme] = theme_packs['exclusive_themes'][owned_theme]

        options = [
            discord.SelectOption(label=properties.get('display_name'), value=name)
            for name, properties in available_themes.items()
        ]

        view = SettingsSelectView(interaction=interaction)
        view.add_item(ActiveThemeSelect(options))

        await interaction.response.send_message(
            embeds=embeds, view=view, ephemeral=True)


    @discord.ui.button(
        label="Reset Time", style=discord.ButtonStyle.gray,
        custom_id="reset_time", row=1)
    async def reset_time(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        await helper.interactions.run_interaction_checks(interaction)

        embeds = lib.load_embeds('reset_time', color='primary')

        timezone_options = [
            discord.SelectOption(label=f'GMT{lib.prefix_int(i-12)}', value=i-12)
            for i in reversed(range(25))
        ]
        reset_hour_options = [
            discord.SelectOption(label=hour, value=i) for i, hour in enumerate(HOURS)
        ]
        reset_minute_options = [
            discord.SelectOption(label=f"{min:02d}", value=min) for min in MINUTES
        ]

        view = SettingsSelectView(interaction=interaction)
        view.add_item(UTCOffsetSelect(timezone_options, "Select a GMT offset"))
        view.add_item(ResetHourSelect(reset_hour_options, "Select a reset hour"))
        view.add_item(ResetMinuteSelect(reset_minute_options, "Select a reset minute"))

        await interaction.response.send_message(
            embeds=embeds,
            view=view,
            ephemeral=True
        )

    @discord.ui.button(
        label="Linked Account",
        style=discord.ButtonStyle.gray,
        custom_id="linked_account", row=1)
    async def linked_account(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        await helper.interactions.run_interaction_checks(interaction)
        await interaction.response.send_modal(LinkAccountModal())


class Settings(commands.Cog):
    def __init__(self, client):
        self.client: commands.Bot = client

    @app_commands.command(
        name="settings",
        description="Edit your configuration for statalytics")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    async def settings(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await helper.interactions.run_interaction_checks(interaction)

        embeds = lib.load_embeds('settings', color='primary')
        await interaction.followup.send(
            embeds=embeds, view=SettingsButtons(interaction=interaction))

        lib.update_command_stats(interaction.user.id, 'settings')


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Settings(client))
