from typing import Any
import discord

from ..handlers import handle_interaction_errors


class CustomBaseView(discord.ui.View):
    async def on_error(
        self,
        interaction: discord.Interaction,
        error: Exception,
        item: discord.ui.Item[Any]
    ) -> None:
        await handle_interaction_errors(interaction, error)


class CustomBaseModal(discord.ui.Modal):
    async def on_error(
        self,
        interaction: discord.Interaction,
        error: Exception
    ) -> None:
        await handle_interaction_errors(interaction, error)
