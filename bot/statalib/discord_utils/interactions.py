from aiohttp import ContentTypeError
from typing import Callable

from discord import Interaction

from .responses import interaction_send_object
from ..aliases import PlayerName, PlayerUUID, PlayerDynamic
from ..functions import fname, load_embeds
from ..views.info import SessionInfoButton
from ..network import fetch_hypixel_data, mojang_session
from ..mcfetch import AsyncFetchPlayer2
from ..sessions import find_dynamic_session, start_session
from ..errors import (
    PlayerNotFoundError,
    SessionNotFoundError,
    MojangInvalidResponseError
)
from ..linking import (
    link_account,
    get_linked_player,
    update_autofill
)


async def fetch_player_info(
    player: PlayerDynamic,
    interaction: Interaction,
    eph=False
) -> tuple[PlayerName, PlayerUUID]:
    """
    Get formatted username & uuid of a user from their minecraft ign / uuid
    :param player: Username, uuid, or linked discord id of the player
    :param interaction: The discord interaction object used
    :param eph: whether or not to respond with an ephemeral message (default false)
    """
    if player is None:
        uuid = get_linked_player(interaction.user.id)

        if uuid:
            try:
                name = await AsyncFetchPlayer2(uuid, cache_backend=mojang_session).name
            except ContentTypeError as exc:
                raise MojangInvalidResponseError from exc

            update_autofill(interaction.user.id, uuid, name)
        else:
            msg = ("You are not linked! Either specify "
                   "a player or link your account using `/link`!")

            if interaction.response.is_done():
                await interaction.followup.send(msg)
            else:
                await interaction.response.send_message(msg, ephemeral=eph)
            raise PlayerNotFoundError
    else:
        # allow for linked discord ids
        if player.isnumeric() and len(player) >= 16:
            player = get_linked_player(int(player)) or ''

        player_data = AsyncFetchPlayer2(player, cache_backend=mojang_session)

        try:
            name = await player_data.name
            uuid = await player_data.uuid
        except ContentTypeError as exc:
            raise MojangInvalidResponseError from exc

        if name is None:
            await interaction_send_object(interaction)(
                "That player does not exist!", ephemeral=eph)
            raise PlayerNotFoundError
    return name, uuid


async def linking_interaction(
    interaction: Interaction,
    username: PlayerName
):
    """
    discord.py interaction for account linking
    :param interaction: the discord interaction to be used
    :param username: the username of the respective player
    """
    await interaction.response.defer()
    name, uuid = await fetch_player_info(username, interaction)

    hypixel_data = await fetch_hypixel_data(uuid, cache=False)

    # Linking Logic
    discord_tag = str(interaction.user)
    response = await link_account(
        discord_tag, interaction.user.id, hypixel_data, uuid, name)

    if response == 1:
        await interaction.followup.send(f"Successfully linked to **{fname(name)}**")
        return

    if response == 2:
        await interaction.followup.send(
            f"Successfully linked to **{fname(name)}**\n"
            "No sessions where found for this player so one was created.",
            view=SessionInfoButton())
        return

    # Player not linked embed
    embeds = load_embeds('linking', color='primary')
    await interaction.followup.send(embeds=embeds)


async def find_dynamic_session_interaction(
    interaction_response: Callable[[str], None],
    username: PlayerName,
    uuid: PlayerUUID,
    hypixel_data: dict,
    session: int | None=None
) -> tuple | bool:
    """
    Dynamically gets a session of a user\n
    If session is 100, the first session to exist will be returned
    :param interaction_response: The discord interaction response object
    to reply with.
    :param username: The username of the session owner
    :param uuid: The uuid of the session owner
    :param hypixel_data: the current hypixel data of the session owner
    :param session: The session to attempt to be retrieved
    :param eph: whether or not to respond ephemerally
    """
    returned_session = find_dynamic_session(uuid, session)

    # no sessions exist because... i forgot to finish this comment now idk
    if not returned_session and not session:
        await start_session(uuid, session=1, hypixel_data=hypixel_data)
        await interaction_response(
            content=f"**{fname(username)}** has no active sessions so one was created!"
        )
        raise SessionNotFoundError

    if not returned_session:
        await interaction_response(
            content=f"**{fname(username)}** doesn't have an"
                    f" active session with ID: `{session}`!"
        )
        raise SessionNotFoundError

    return returned_session
