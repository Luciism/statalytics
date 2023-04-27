import sqlite3
from mcuuid import MCUUID

def update_autofill(discord_id, uuid, username):
    with sqlite3.connect('./database/subscriptions.db') as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM subscriptions WHERE discord_id = {discord_id}")
        subscription = cursor.fetchone()

    if subscription:
        with sqlite3.connect('../bot/database/autofill.db') as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM autofill WHERE discord_id = {discord_id}")
            autofill_data = cursor.fetchone()

            if not autofill_data:
                query = "INSERT INTO autofill (discord_id, uuid, username) VALUES (?, ?, ?)"
                cursor.execute(query, (discord_id, uuid, username))
            elif autofill_data[2] != username:
                query = "UPDATE autofill SET uuid = ?, username = ? WHERE discord_id = ?"
                cursor.execute(query, (uuid, username, discord_id))

async def authenticate_user(username, interaction):
    if username is None:
        with sqlite3.connect('./database/linked_accounts.db') as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM linked_accounts WHERE discord_id = {interaction.user.id}")
            linked_data = cursor.fetchone()
        if linked_data:
            uuid = linked_data[1]
            name = MCUUID(uuid=uuid).name
            update_autofill(interaction.user.id, uuid, name)
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
