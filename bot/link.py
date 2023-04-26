import random
import json
import sqlite3
import requests

class AccountLink:
    def __init__(self, discordtag, discordid, name, uuid) -> None:
        self.discordtag, self.discordid, self.name, self.uuid = discordtag, discordid, name, uuid

    def account_link(self):
        with open('./database/apikeys.json', 'r') as datafile:
            allkeys = json.load(datafile)['keys']
        key = random.choice(list(allkeys))
        response = requests.get(f"https://api.hypixel.net/player?key={allkeys[key]}&uuid={self.uuid}", timeout=10)
        data = response.json()
        social_media = data.get('player', {}).get('socialMedia', {})
        links = social_media.get('links', {})
        discordtag_hypixel = links.get('DISCORD', 'none')

        # Linking Logic
        if self.discordtag == discordtag_hypixel:
            # Update it in the linked accounts database
            with sqlite3.connect('./database/linked_accounts.db') as conn:
                cursor = conn.cursor()
                cursor.execute(f"SELECT * FROM linked_accounts WHERE discord_id = {self.discordid}")
                linked_data = cursor.fetchone()

                if not linked_data:
                    query = "INSERT INTO linked_accounts (discord_id, uuid) VALUES (?, ?)"
                    cursor.execute(query, (self.discordid, self.uuid))
                else:
                    query = "UPDATE linked_accounts SET uuid = ? WHERE discord_id = ?"
                    cursor.execute(query, (self.uuid, self.discordid))

            # Update autofill
            with sqlite3.connect('./database/subscriptions.db') as conn:
                cursor = conn.cursor()
                cursor.execute(f"SELECT * FROM subscriptions WHERE discord_id = {self.discordid}")
                subscription = cursor.fetchone()

            if subscription:
                with sqlite3.connect('./database/autofill.db') as conn:
                    cursor = conn.cursor()
                    query = f"SELECT * FROM autofill WHERE discord_id = {self.discordid}"
                    cursor.execute(query)
                    autofill_data = cursor.fetchone()

                    if not autofill_data:
                        query = "INSERT INTO autofill (discord_id, uuid, username) VALUES (?, ?, ?)"
                        cursor.execute(query, (self.discordid, self.uuid, self.name))
                    else:
                        query = "UPDATE autofill SET uuid = ?, username = ? WHERE discord_id = ?"
                        cursor.execute(query, (self.uuid, self.name, self.discordid))
            return True
        return None if not discordtag_hypixel else False
