import os
import sqlite3
from mcuuid import MCUUID

async def authenticate_user(username, interaction):
    if username is None:
        with sqlite3.connect('./database/linkedaccounts.db') as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM linkedaccounts WHERE discordid = '{interaction.user.id}'")
            linked_data = cursor.fetchone()
        if linked_data:
            uuid = linked_data[3]
            try:
                name = MCUUID(uuid=uuid).name
            except Exception as error:
                print(error)
                await interaction.response.send_message(f"An internal error occured: {error}")
                return
        else:
            await interaction.response.send_message("You are not linked! Either specify a player or link your account using `/link`!")
            return
    else:
        try:
            uuid = MCUUID(name=username).uuid
            name = MCUUID(name=username).name
        except KeyError:
            await interaction.response.send_message("That player does not exist!")
            return
    return name, uuid
