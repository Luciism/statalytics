import asyncio
from statalib import fetch_hypixel_data
from calc.quests import QuestStats

async def main():
    uuid = ''

    hypixel_data = fetch_hypixel_data(uuid, cache=False)
    stats = QuestStats(hypixel_data)

    print(stats)


asyncio.run(main())
