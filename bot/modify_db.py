import json
import random
import sqlite3
import requests

with sqlite3.connect('./database/sessions.db') as conn:
    cursor = conn.cursor()
    cursor.execute("ALTER TABLE sessions ADD COLUMN two_four_wins_bedwars INTEGER;")
    cursor.execute("ALTER TABLE sessions ADD COLUMN two_four_losses_bedwars INTEGER;")
    cursor.execute("ALTER TABLE sessions ADD COLUMN two_four_final_kills_bedwars INTEGER;")
    cursor.execute("ALTER TABLE sessions ADD COLUMN two_four_final_deaths_bedwars INTEGER;")
    cursor.execute("ALTER TABLE sessions ADD COLUMN two_four_kills_bedwars INTEGER;")
    cursor.execute("ALTER TABLE sessions ADD COLUMN two_four_deaths_bedwars INTEGER;")
    cursor.execute("ALTER TABLE sessions ADD COLUMN two_four_beds_broken_bedwars INTEGER;")
    cursor.execute("ALTER TABLE sessions ADD COLUMN two_four_beds_lost_bedwars INTEGER;")
    cursor.execute("ALTER TABLE sessions ADD COLUMN two_four_games_played_bedwars INTEGER;")
    cursor.execute("ALTER TABLE sessions ADD COLUMN items_purchased_bedwars INTEGER;")
    cursor.execute("ALTER TABLE sessions ADD COLUMN eight_one_items_purchased_bedwars INTEGER;")
    cursor.execute("ALTER TABLE sessions ADD COLUMN eight_two_items_purchased_bedwars INTEGER;")
    cursor.execute("ALTER TABLE sessions ADD COLUMN four_three_items_purchased_bedwars INTEGER;")
    cursor.execute("ALTER TABLE sessions ADD COLUMN four_four_items_purchased_bedwars INTEGER;")
    cursor.execute("ALTER TABLE sessions ADD COLUMN two_four_items_purchased_bedwars INTEGER;")

    cursor.execute('SELECT * FROM sessions')
    sessions = cursor.fetchall()
    
    with open('./database/apikeys.json', 'r') as keyfile:
        all_keys = json.load(keyfile)['hypixel']
    key = all_keys[random.choice(list(all_keys))]

    new_values = [
        "two_four_wins_bedwars",
        "two_four_losses_bedwars",
        "two_four_final_kills_bedwars",
        "two_four_final_deaths_bedwars",
        "two_four_kills_bedwars",
        "two_four_deaths_bedwars",
        "two_four_beds_broken_bedwars",
        "two_four_beds_lost_bedwars",
        "two_four_games_played_bedwars",
        "items_purchased_bedwars",
        "eight_one_items_purchased_bedwars",
        "eight_two_items_purchased_bedwars",
        "four_three_items_purchased_bedwars",
        "four_four_items_purchased_bedwars",
        "two_four_items_purchased_bedwars"
    ]

    for session in sessions:
        uuid = session[1]

        res = requests.get(f"https://api.hypixel.net/player?key={key}&uuid={uuid}", timeout=10)
        data = res.json().get('player', {}).get('stats', {}).get('Bedwars', {})

        query = ', '.join((f'{value} = {data.get(value, 0)}' for value in new_values))
        cursor.execute(f"UPDATE sessions SET {query} WHERE uuid = '{uuid}'")
        print(f"UPDATE sessions SET {query} WHERE uuid = '{uuid}'")
