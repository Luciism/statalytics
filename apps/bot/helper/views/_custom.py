"""Custom base discord.py UI components."""

from typing import Any
import discord

from statalib.handlers import handle_interaction_errors


class CustomBaseView(discord.ui.View):
    """Base class with error handling for custom discord.py views."""
    async def on_error(
        self,
        interaction: discord.Interaction,
        error: Exception,
        item: discord.ui.Item[Any]
    ) -> None:
        await handle_interaction_errors(interaction, error)


class CustomBaseModal(discord.ui.Modal):
    """Base class with error handling for custom discord.py modals."""
    async def on_error(
        self,
        interaction: discord.Interaction,
        error: Exception
    ) -> None:
        await handle_interaction_errors(interaction, error)
