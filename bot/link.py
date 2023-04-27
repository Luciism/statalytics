import random
import json
import sqlite3
import requests

def link_account(discord_tag, discord_id, name, uuid):
    with open('./database/apikeys.json', 'r') as datafile:
        allkeys = json.load(datafile)['keys']
    key = random.choice(list(allkeys))

    data = requests.get(f"https://api.hypixel.net/player?key={allkeys[key]}&uuid={uuid}", timeout=10).json()
    if not data['player']: return None
    hypixel_discord_tag = data.get('player', {}).get('socialMedia', {}).get('links', {}).get('DISCORD', None)

    # Linking Logic
    if hypixel_discord_tag:
        if discord_tag == hypixel_discord_tag:
            # Update it in the linked accounts database
            with sqlite3.connect('./database/linked_accounts.db') as conn:
                cursor = conn.cursor()
                cursor.execute(f"SELECT * FROM linked_accounts WHERE discord_id = {discord_id}")
                linked_data = cursor.fetchone()

                if not linked_data: cursor.execute("INSERT INTO linked_accounts (discord_id, uuid) VALUES (?, ?)", (discord_id, uuid))
                else: cursor.execute("UPDATE linked_accounts SET uuid = ? WHERE discord_id = ?", (uuid, discord_id))
            

            # Update autofill
            with sqlite3.connect('./database/subscriptions.db') as conn:
                cursor = conn.cursor()
                cursor.execute(f"SELECT * FROM subscriptions WHERE discord_id = {discord_id}")
                subscription = cursor.fetchone()

            if subscription:
                with sqlite3.connect('./database/autofill.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute(f"SELECT * FROM autofill WHERE discord_id = {discord_id}")
                    autofill_data = cursor.fetchone()

                    if not autofill_data:
                        query = "INSERT INTO autofill (discord_id, uuid, username) VALUES (?, ?, ?)"
                        cursor.execute(query, (discord_id, uuid, name))
                    else:
                        query = "UPDATE autofill SET uuid = ?, username = ? WHERE discord_id = ?"
                        cursor.execute(query, (uuid, name, discord_id))
            return True
        return False
    return None
