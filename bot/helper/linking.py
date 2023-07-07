import sqlite3

from mcuuid import MCUUID
from discord import Interaction

from .errors import PlayerNotFoundError
from .functions import (
    get_hypixel_data,
    get_subscription,
    load_embeds,
    REL_PATH
)


def uuid_to_discord_id(uuid: str) -> int | None:
    """
    Attempts to fetch discord id from linked database
    :param uuid: The uuid of the player to find linked data for
    """
    with sqlite3.connect(f'{REL_PATH}/database/core.db') as conn:
        cursor = conn.cursor()

        cursor.execute(f"SELECT discord_id FROM linked_accounts WHERE uuid = '{uuid}'")
        discord_id = cursor.fetchone()

    return None if not discord_id else discord_id[0]


def get_linked_data(discord_id: int) -> tuple:
    """
    Returns a users linked data from linked database
    :param discord_id: The discord id of user's linked data to be retrieved
    """
    with sqlite3.connect(f'{REL_PATH}/database/core.db') as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM linked_accounts WHERE discord_id = {discord_id}")
        return cursor.fetchone()


def set_linked_data(discord_id: int, uuid: str) -> None:
    """
    Inserts linked account data into database
    :param discord_id: the discord id of the respective user
    :param uuid: the minecraft uuid of the relvative user
    """
    with sqlite3.connect(f'{REL_PATH}/database/core.db') as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM linked_accounts WHERE discord_id = {discord_id}")
        linked_data = cursor.fetchone()

        if not linked_data:
            cursor.execute("INSERT INTO linked_accounts (discord_id, uuid) VALUES (?, ?)", (discord_id, uuid))
        else:
            cursor.execute("UPDATE linked_accounts SET uuid = ? WHERE discord_id = ?", (uuid, discord_id))


def update_autofill(discord_id: int, uuid: str, username: str) -> None:
    """
    Updates autofill for a user, this will be helpful if a user has changed their ign
    :param discord_id: The discord id of the target linked user
    :param uuid: The uuid of the target linked user
    :param username: The updated username of the target linked user
    """
    subscription: tuple = get_subscription(discord_id)
    if subscription:
        with sqlite3.connect(f'{REL_PATH}/database/core.db') as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM autofill WHERE discord_id = {discord_id}")
            autofill_data: tuple = cursor.fetchone()

            if not autofill_data:
                query = "INSERT INTO autofill (discord_id, uuid, username) VALUES (?, ?, ?)"
                cursor.execute(query, (discord_id, uuid, username))
            elif autofill_data[2] != username:
                query = "UPDATE autofill SET uuid = ?, username = ? WHERE discord_id = ?"
                cursor.execute(query, (uuid, username, discord_id))


async def link_account(discord_tag: str, discord_id: int, name: str, uuid: str) -> bool | None:
    """
    Attempt to link an discord account to a hypixel account
    :param discord_tag: The discord user's full tag eg: Example#1234
    :param discord_id: The discord user's id
    :param name: The username of the hypixel account being linked
    :param uuid: The uuid of the hypixel account being linked

    #### Returns:
        1 if linking was a success\n
        0 if discord tags don't match\n
        -1 if discord tag isn't set\n
    """
    hypixel_data = await get_hypixel_data(uuid=uuid, cache=False)
    if not hypixel_data['player']:
        return -1

    hypixel_discord_tag: str = hypixel_data.get('player', {}).get(
        'socialMedia', {}).get('links', {}).get('DISCORD', None)

    # Linking Logic
    if hypixel_discord_tag:
        if discord_tag == hypixel_discord_tag:
            set_linked_data(discord_id, uuid)
            update_autofill(discord_id, uuid, name)
            return 1
        return 0
    return -1


async def fetch_player_info(username: str, interaction: Interaction,
                            eph=False) -> tuple[str, str]:
    """
    Get formatted username & uuid of a user from their minecraft ign / uuid
    :param username: The minecraft ign of the player to return (can also take a uuid)
    :param interaction: The discord interaction object used
    :param eph: whether or not to respond with an ephemeral message (default false)
    """
    if username is None:
        linked_data = get_linked_data(interaction.user.id)
        if linked_data:
            uuid: str = linked_data[1]
            name: str = MCUUID(uuid=uuid).name
            update_autofill(interaction.user.id, uuid, name)
        else:
            msg = "You are not linked! Either specify a player or link your account using `/link`!"
            if interaction.response.is_done():
                await interaction.followup.send(msg)
            else:
                await interaction.response.send_message(msg, ephemeral=eph)
            raise PlayerNotFoundError
    else:
        try:
            if len(username) <= 16:
                uuid: str = MCUUID(name=username).uuid
                name: str = MCUUID(name=username).name
            else:
                name: str = MCUUID(uuid=username).name
                uuid: str = username
                if not name:
                    raise KeyError
        except KeyError:
            if interaction.response.is_done():
                await interaction.followup.send("That player does not exist!")
            else:
                await interaction.response.send_message("That player does not exist!", ephemeral=eph)
            raise PlayerNotFoundError
    return name, uuid


async def linking_interaction(interaction: Interaction, username: str):
    """
    discord.py interaction for account linking
    :param interaction: the discord interaction to be used
    :param username: the username of the respective player
    """
    await interaction.response.defer()
    name, uuid = await fetch_player_info(username, interaction)

    # Linking Logic
    discord_tag = str(interaction.user)
    if discord_tag.endswith('#0'):
        discord_tag = discord_tag[:-2]

    response = await link_account(discord_tag, interaction.user.id, name, uuid)
    refined = name.replace('_', r'\_')

    if response == 1:
        await interaction.followup.send(f"Successfully linked to **{refined}** ({discord_tag})")
        return

    # Player not linked embed
    embeds = load_embeds('linking', color='primary')
    await interaction.followup.send(embeds=embeds)


class LinkingManager:
    def __init__(self, discord_id: int):
        self._discord_id = discord_id


    def get_linked_data(self):
        """
        Returns a users linked data from linked database
        """
        return get_linked_data(self._discord_id)


    def set_linked_data(self, uuid: str):
        """
        Inserts linked account data into database
        :param uuid: the minecraft uuid of the relvative user
        """
        set_linked_data(self._discord_id, uuid)


    def uuid_to_discord_id(self, uuid: str):
        """
        Attempts to fetch discord id from linked database
        :param uuid: The uuid of the player to find linked data for
        """
        return uuid_to_discord_id(uuid)


    def update_autofill(self, uuid: str, username: str):
        """
        Updates autofill for a user, this will be helpful if a user has changed their ign
        :param uuid: The uuid of the target linked user
        :param username: The updated username of the target linked user
        """
        update_autofill(self._discord_id, uuid, username)


    async def link_account(self, discord_tag: str, name: str, uuid: str):
        """
        Attempt to link an discord account to a hypixel account
        :param discord_tag: The discord user's full tag eg: Example#1234
        :param name: The username of the hypixel account being linked
        :param uuid: The uuid of the hypixel account being linked

        #### Returns:
            1 if linking was a success\n
            0 if discord tags don't match\n
            -1 if discord tag isn't set\n
        """
        response = await link_account(discord_tag, self._discord_id, name, uuid)
        return response


    async def fetch_player_info(self, username, interaction: Interaction, eph=False):
        """
        Get formatted username & uuid of a user from their minecraft ign / uuid
        :param username: The minecraft ign of the player to return (can also take a uuid)
        :param interaction: The discord interaction object used
        :param eph: whether or not to respond with an ephemeral message (default false)
        """
        name, uuid = await fetch_player_info(username, interaction, eph)
        return name, uuid
