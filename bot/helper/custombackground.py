import os
import sqlite3

def background(path, uuid, default):
    with sqlite3.connect('./database/linked_accounts.db') as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM linked_accounts WHERE uuid = '{uuid}'")
        linked_data = cursor.fetchone()

    if not linked_data:
        return f'{path}/{default}.png'
    discordid = linked_data[0]

    with sqlite3.connect('./database/subscriptions.db') as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM subscriptions WHERE discord_id = {discordid}")
        subscription = cursor.fetchone()
    if subscription and 'premium' in subscription[1] and os.path.exists(f'{path}/custom/{discordid}.png'):
        return f'{path}/custom/{discordid}.png'
    return f'{path}/{default}.png'
