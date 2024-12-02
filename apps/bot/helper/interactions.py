import asyncio
import os
import logging
from typing import Callable

import discord
from discord import Interaction, Embed
from aiohttp import ContentTypeError, ClientConnectionError

import statalib as lib
from statalib.accounts import Account
from .tips import random_tip_message
from .views import ModesView


logger = logging.getLogger('statalytics')


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
    player: lib.aliases.PlayerDynamic,
    interaction: Interaction,
    eph=False
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
                name = await lib.mcfetch.AsyncFetchPlayer2(
                    uuid, cache_backend=lib.network.mojang_session).name
            except (ContentTypeError, ClientConnectionError) as exc:
                raise lib.errors.MojangInvalidResponseError from exc

            Account(interaction.user.id).linking.update_autofill(uuid, name)
        else:
            msg = ("You are not linked! Either specify "
                   "a player or link your account using `/link`!")

            if interaction.response.is_done():
                await interaction.followup.send(msg)
            else:
                await interaction.response.send_message(msg, ephemeral=eph)
            raise lib.errors.PlayerNotFoundError
    else:
        # allow for linked discord ids
        if player.isnumeric() and len(player) >= 16:
            player = Account(int(player)).linking.get_linked_player_uuid() or ''

        player_data = lib.mcfetch.AsyncFetchPlayer2(
            player, cache_backend=lib.network.mojang_session)

        try:
            name = await player_data.name
            uuid = await player_data.uuid
        except (ContentTypeError, ClientConnectionError) as exc:
            raise lib.errors.MojangInvalidResponseError from exc

        if name is None:
            await interaction_send_object(interaction)(
                "That player does not exist!", ephemeral=eph)
            raise lib.errors.PlayerNotFoundError
    return name, uuid


async def linking_interaction(
    interaction: Interaction,
    username: lib.aliases.PlayerName
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
    response = await Account(interaction.user.id).linking.link_account(
        str(interaction.user), hypixel_data, name, uuid)

    if response == 1:
        await interaction.followup.send(f"Successfully linked to **{lib.fname(name)}**")
        return

    if response == 2:
        await interaction.followup.send(
            f"Successfully linked to **{lib.fname(name)}**\n"
            "No sessions where found for this player so one was created.",
            view=lib.shared_views.SessionInfoButton())
        return

    # Player not linked embed
    embeds = lib.load_embeds('linking', color='primary')
    await interaction.followup.send(embeds=embeds)


async def find_dynamic_session_interaction(
    interaction_callback: Callable[[str], None],
    username: lib.aliases.PlayerName,
    uuid: lib.aliases.PlayerUUID,
    hypixel_data: dict,
    session: int | None=None
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
                content=f"**{lib.fname(username)}** has no active sessions so one was created!"
            )
            raise lib.errors.SessionNotFoundError

        await interaction_callback(
            content=
                f"**{lib.fname(username)}** doesn't have an active session with ID: `{session}`!"
        )
        raise lib.errors.SessionNotFoundError

    return session_info


async def _send_interaction_check_response(
    interaction: Interaction,
    embeds: list[Embed]
):
    if interaction.response.is_done():
        await interaction.edit_original_response(
            embeds=embeds, content=None, attachments=[])
    else:
        await interaction.response.send_message(
            embeds=embeds, content=None, files=[])


async def run_interaction_checks(
    interaction: Interaction,
    check_blacklisted: bool=True,
    permissions: list | str=None,
    allow_star: bool=True
):
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

    # User is blacklisted
    if check_blacklisted and account_data.blacklisted:
        embeds = lib.load_embeds('blacklisted', color='danger')
        await _send_interaction_check_response(interaction, embeds)

        logger.debug(
            f'`Blacklisted User`: Denied {interaction.user} '
            f'({interaction.user.id}) access to an interaction')
        raise lib.errors.UserBlacklistedError

    if permissions:
        # User doesn't have at least one of the required permissions
        if not (allow_star and '*' in account_data.permissions):
            if not set(permissions) & set(account_data.permissions):
                embeds = lib.load_embeds('missing_permissions', color='danger')
                await _send_interaction_check_response(interaction, embeds)

                logger.debug(
                    f'`Missing permissions`: Denied {interaction.user} '
                    f'({interaction.user.id}) access to an interaction.')
                raise lib.errors.MissingPermissionsError


async def handle_modes_renders(
    interaction: discord.Interaction,
    func: object,
    kwargs: dict,
    message=None,
    custom_view: discord.ui.View=None
) -> None:
    """
    Renders and sends all modes to discord for the selected render
    :param interaction: the relative discord interaction object
    :param func: the function object to render with
    :param kwargs: the keyword arguments needed to render the image
    :param message: the message to send to discord with the image
    :param view: a discord view to merge with the sent view
    """
    if not message:
        message = random_tip_message(interaction.user.id)

    os.makedirs(f'{lib.REL_PATH}/database/rendered/{interaction.id}')
    await func(mode="Overall", **kwargs)
    view = ModesView(
        interaction_origin=interaction,
        placeholder='Select a mode'
    )

    if custom_view is not None:
        for child in custom_view.children:
            view.add_item(child)

    image = discord.File(
        f"{lib.REL_PATH}/database/rendered/{interaction.id}/overall.png")
    try:
        await interaction.edit_original_response(
            content=message, attachments=[image], view=view
        )
    except discord.errors.NotFound:
        return

    await asyncio.gather(
        func(mode="Solos", **kwargs),
        func(mode="Doubles", **kwargs),
        func(mode="Threes", **kwargs),
        func(mode="Fours", **kwargs),
        func(mode="4v4", **kwargs),
    )
