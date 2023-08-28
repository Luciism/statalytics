from typing import Callable
import discord


def interaction_send_object(interaction: discord.Interaction) -> Callable:
    """
    Returns `followup.send` or `response.send_message`
    depending on if the interation is done or not.

    :param interaction: the interaction object to get the send object for
    """
    if interaction.response.is_done():
        response_obj = interaction.followup.send
    else:
        response_obj = interaction.response.send_message
    return response_obj
