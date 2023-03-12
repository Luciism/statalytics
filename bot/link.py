import random
import json
import os
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
            with sqlite3.connect('./database/linkedaccounts.db') as conn:
                cursor = conn.cursor()
                cursor.execute(f"SELECT * FROM linkedaccounts WHERE discordid = '{self.discordid}'")
                linked_data = cursor.fetchone()

                if not linked_data:
                    query = "INSERT INTO linkedaccounts (discordtag, discordid, username, uuid) VALUES (?, ?, ?, ?)"
                    cursor.execute(query, (self.discordtag, str(self.discordid), self.name, self.uuid))
                else:
                    query = "UPDATE linkedaccounts SET discordtag = ?, username = ?, uuid = ? WHERE discordid = ?"
                    cursor.execute(query, (self.discordtag, self.name, self.uuid, str(self.discordid)))
                conn.commit()

            # Update autofill
            with sqlite3.connect('./database/subscriptions.db') as conn:
                cursor = conn.cursor()
                cursor.execute(f"SELECT * FROM subscriptions WHERE discordid = '{self.discordid}'")
                subscription = cursor.fetchone()

            if subscription:
                with sqlite3.connect('./database/autofill.db') as conn:
                    cursor = conn.cursor()
                    query = f"SELECT * FROM autofill WHERE discordid = '{self.discordid}'"
                    cursor.execute(query)
                    autofill_data = cursor.fetchone()

                    if not autofill_data:
                        query = "INSERT INTO autofill (username, uuid, discordid) VALUES (?, ?, ?)"
                        cursor.execute(query, (self.name, self.uuid, str(self.discordid)))
                    else:
                        query = "UPDATE autofill SET username = ?, uuid = ? WHERE discordid = ?"
                        cursor.execute(query, (self.name, self.uuid, str(self.discordid)))
                    conn.commit()
            return True
        return None if not discordtag_hypixel else False
