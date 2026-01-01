import asyncio
import logging
import os
from typing import Any, Callable, Coroutine

import discord
import mcfetch
import statalib as lib
from aiohttp import ClientConnectionError, ContentTypeError
from discord import Embed, Interaction
from statalib.accounts import Account
from statalib.accounts.linking import LinkingOutcomeEnum
from statalib.common import Mode, ModesEnum

from .embeds import Embeds
from .tips import random_tip_message
from .views import ModesView
from .views.info import SessionInfoButton

logger = logging.getLogger("statalytics")


def interaction_send_object(interaction: Interaction) -> Callable:
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


async def fetch_player_info(
    player: lib.aliases.PlayerDynamic, interaction: Interaction, eph=False
) -> tuple[lib.aliases.PlayerName, lib.aliases.PlayerUUID]:
    """
    Get formatted username & uuid of a user from their minecraft ign / uuid
    :param player: Username, uuid, or linked discord id of the player
    :param interaction: The discord interaction object used
    :param eph: whether or not to respond with an ephemeral message (default false)
    """
    if player is None:
        uuid = Account(interaction.user.id).linking.get_linked_player_uuid()

        if uuid:
            try:
                name = await mcfetch.AsyncPlayer(
                    uuid, cache_backend=lib.network.mojang_session
                ).name
            except (ContentTypeError, ClientConnectionError) as exc:
                raise lib.errors.MojangInvalidResponseError from exc

            Account(interaction.user.id).linking.update_autofill(uuid, name)
        else:
            msg = (
                "You are not linked! Either specify "
                "a player or link your account using `/link`!"
            )

            if interaction.response.is_done():
                await interaction.followup.send(msg)
            else:
                await interaction.response.send_message(msg, ephemeral=eph)
            raise lib.errors.PlayerNotFoundError
    else:
        # allow for linked discord ids
        if player.isnumeric() and len(player) >= 16:
            player = Account(int(player)).linking.get_linked_player_uuid() or ""

        player_data = mcfetch.AsyncPlayer(
            player, cache_backend=lib.network.mojang_session
        )

        try:
            name = await player_data.name
            uuid = await player_data.uuid
        except (ContentTypeError, ClientConnectionError) as exc:
            raise lib.errors.MojangInvalidResponseError from exc

        if name is None:
            await interaction_send_object(interaction)(
                "That player does not exist!", ephemeral=eph
            )
            raise lib.errors.PlayerNotFoundError
    return name, uuid


async def linking_interaction(
    interaction: Interaction, username: lib.aliases.PlayerName
):
    """
    discord.py interaction for account linking
    :param interaction: the discord interaction to be used
    :param username: the username of the respective player
    """
    await interaction.response.defer()
    await run_interaction_checks(interaction)

    name, uuid = await fetch_player_info(username, interaction)

    hypixel_data = await lib.network.fetch_hypixel_data(uuid, cache=False)

    # Linking Logic
    response = Account(interaction.user.id).linking.link_account(
        str(interaction.user), hypixel_data, name, uuid
    )

    if response == LinkingOutcomeEnum.SUCCESS:
        return await interaction.followup.send(
            f"Successfully linked to **{lib.fmt.fname(name)}**"
        )

    if response == LinkingOutcomeEnum.SUCCESS_AND_SESSION_CREATED:
        return await interaction.followup.send(
            f"Successfully linked to **{lib.fmt.fname(name)}**\n"
            + "No sessions where found for this player so one was created.",
            view=SessionInfoButton(),
        )

    # Player not linked embed
    await interaction.followup.send(embed=Embeds.problems.linking_error())


async def find_dynamic_session_interaction(
    interaction_callback: Callable[[str], None],
    username: lib.aliases.PlayerName,
    uuid: lib.aliases.PlayerUUID,
    hypixel_data: dict,
    session: int | None = None,
) -> lib.sessions.BedwarsSession:
    """
    Dynamically gets a session of a user\n
    If session is None, the first session to exist will be returned
    :param interaction_callback: The discord interaction response object
    to reply with.
    :param username: The username of the session owner
    :param uuid: The uuid of the session owner
    :param hypixel_data: the current hypixel data of the session owner
    :param session: The session to attempt to be retrieved
    :param eph: whether or not to respond ephemerally
    """
    session_manager = lib.sessions.SessionManager(uuid)
    session_info = session_manager.get_session(session)

    # no sessions exist because... i forgot to finish this comment now idk
    if not session_info:
        session_count = session_manager.session_count()

        if session_count == 0:
            session_manager.create_session(session_id=1, hypixel_data=hypixel_data)

            await interaction_callback(
                content=f"**{lib.fmt.fname(username)}** has no active sessions so one was created!"
            )
            raise lib.errors.SessionNotFoundError

        await interaction_callback(
            content=f"**{lib.fmt.fname(username)}** doesn't have an active session with ID: `{session}`!"
        )
        raise lib.errors.SessionNotFoundError

    return session_info


async def _send_interaction_check_response(interaction: Interaction, embed: Embed):
    if interaction.response.is_done():
        await interaction.edit_original_response(
            embed=embed, content=None, attachments=[]
        )
    else:
        await interaction.response.send_message(embed=embed, content=None, files=[])


async def run_interaction_checks(
    interaction: Interaction,
    check_blacklisted: bool = True,
    permissions: list[str] | str | None = None,
    allow_star: bool = True,
) -> None:
    """
    Runs any checks to see if the interaction is allowed to proceed.
    Checks things such as if the user is blacklisted, or requires\
        certain permissions
    :param interaction: the `discord.Interaction` object for the interaction
    :param check_blacklisted: whether or not to check if the user is blacklisted
    :param permissions: A required list of permissions that the user must have\
        in order for the interaction to proceed. It will check if the user has\
        at least one of the permissions in the provided list.
    :param allow_star: whether or not to allow star permissions if certain\
        permissions are required
    """
    account_data = lib.accounts.Account(interaction.user.id).load(create=True)
    if not account_data:
        return

    # User is blacklisted
    if check_blacklisted and account_data.blacklisted:
        embed = Embeds.problems.user_blacklisted()
        await _send_interaction_check_response(interaction, embed)

        logger.debug(
            f"`Blacklisted User`: Denied {interaction.user} " +
            f"({interaction.user.id}) access to an interaction"
        )
        raise lib.errors.UserBlacklistedError

    if permissions:
        # User doesn't have at least one of the required permissions
        if not (allow_star and "*" in account_data.permissions):
            if not set(permissions) & set(account_data.permissions):
                embed = Embeds.problems.missing_permissions()
                await _send_interaction_check_response(interaction, embed)

                logger.debug(
                    f"`Missing permissions`: Denied {interaction.user} " +
                    f"({interaction.user.id}) access to an interaction."
                )
                raise lib.errors.MissingPermissionsError


async def handle_modes_renders(
    interaction: discord.Interaction,
    func: Callable[[Mode], Coroutine[None, None, None]],
    kwargs: dict[str, Any],
    message: str | None = None,
    custom_view: discord.ui.View | None = None,
    dreams: bool = False,
) -> None:
    """
    Renders and sends all modes to discord for the selected render.
    :param interaction: The relative discord interaction object.
    :param func: The function object to render with.
    :param kwargs: The keyword arguments needed to render the image.
    :param message: The message to send to discord with the image.
    :param custom_view: A discord view to merge with the sent view.
    :param dreams: Whether to render dream modes instead of regualar modes.
    """
    if not message:
        message = random_tip_message(interaction.user.id)

    os.makedirs(f"{lib.REL_PATH}/database/rendered/{interaction.id}")

    if not dreams:
        modes = ModesEnum.non_dream_modes()
    else:
        modes = ModesEnum.dream_modes()

    await func(mode=modes[0], **kwargs)
    view = ModesView(
        interaction_origin=interaction, placeholder="Select a mode", modes=modes
    )

    if custom_view is not None:
        for child in custom_view.children:
            _ = view.add_item(child)

    image = discord.File(
        f"{lib.REL_PATH}/database/rendered/{interaction.id}/{modes[0].id}.png"
    )
    try:
        _ = await interaction.edit_original_response(
            content=message, attachments=[image], view=view
        )
    except discord.errors.NotFound:
        return

    await asyncio.gather(*[func(mode=mode, **kwargs) for mode in modes[1:]])
