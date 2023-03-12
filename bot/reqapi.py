import os
import json
import random
import sqlite3
from datetime import datetime
import requests

def startsession(uuid, session):
    with open('./database/apikeys.json', 'r') as datafile:
        allkeys = json.load(datafile)['keys']
    key = random.choice(list(allkeys))
    response = requests.get(f"https://api.hypixel.net/player?key={allkeys[key]}&uuid={uuid}", timeout=10)
    data = response.json()
    if data['player'] is None:
        return False
    stat_keys = ["Experience", "wins_bedwars", "losses_bedwars", "final_kills_bedwars", "final_deaths_bedwars", "kills_bedwars", "deaths_bedwars", "beds_broken_bedwars", "beds_lost_bedwars", "games_played_bedwars", "eight_one_wins_bedwars", "eight_one_losses_bedwars", "eight_one_final_kills_bedwars", "eight_one_final_deaths_bedwars", "eight_one_kills_bedwars", "eight_one_deaths_bedwars", "eight_one_beds_broken_bedwars", "eight_one_beds_lost_bedwars", "eight_one_games_played_bedwars", "eight_two_wins_bedwars", "eight_two_losses_bedwars", "eight_two_final_kills_bedwars", "eight_two_final_deaths_bedwars", "eight_two_kills_bedwars", "eight_two_deaths_bedwars", "eight_two_beds_broken_bedwars", "eight_two_beds_lost_bedwars", "eight_two_games_played_bedwars", "four_three_wins_bedwars", "four_three_losses_bedwars", "four_three_final_kills_bedwars", "four_three_final_deaths_bedwars", "four_three_kills_bedwars", "four_three_deaths_bedwars", "four_three_beds_broken_bedwars", "four_three_beds_lost_bedwars", "four_three_games_played_bedwars", "four_four_wins_bedwars", "four_four_losses_bedwars", "four_four_final_kills_bedwars", "four_four_final_deaths_bedwars", "four_four_kills_bedwars", "four_four_deaths_bedwars", "four_four_beds_broken_bedwars", "four_four_beds_lost_bedwars", "four_four_games_played_bedwars"]
    stat_values = {
    "session": session,
    "uuid": uuid,
    "date": datetime.now().strftime("%Y-%m-%d"),
    "level": data["player"].get("achievements", {}).get("bedwars_level", 0),
    }
    for key in stat_keys:
        stat_values[key] = data["player"].get("stats", {}).get("Bedwars", {}).get(key, 0)

    with sqlite3.connect('./database/sessions.db') as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM sessions WHERE session=? AND uuid=?", (session, uuid))
        row = cursor.fetchone()

        if not row:
            columns = ', '.join(stat_values.keys())
            values = ', '.join(['?' for _ in stat_values.values()])
            query = f"INSERT INTO sessions ({columns}) VALUES ({values})"
            cursor.execute(query, tuple(stat_values.values()))
        else:
            set_clause = ', '.join([f"{column} = ?" for column in stat_values.keys()])
            query = f"UPDATE sessions SET {set_clause} WHERE session=? AND uuid=?"
            values = list(stat_values.values()) + [session, uuid]
            cursor.execute(query, tuple(values))
        conn.commit()
    return True
