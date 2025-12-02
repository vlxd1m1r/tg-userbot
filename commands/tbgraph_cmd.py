import aiohttp
import os
import matplotlib.pyplot as plt
from telethon import events
from dotenv import load_dotenv

load_dotenv()

APP_ID = os.getenv("TB_APPLICATION_ID")

SEARCH_URL = "https://papi.tanksblitz.ru/wotb/account/list"
INFO_URL   = "https://papi.tanksblitz.ru/wotb/account/info"

def register(client):
    @client.on(events.NewMessage(pattern=r"\.tbgraph (.+)"))
    async def tbgraph(event):
        nickname = event.pattern_match.group(1).strip()
        await event.edit(f"🔍 Ищу игрока **{nickname}**...")

        # Поиск
        async with aiohttp.ClientSession() as session:
            async with session.get(SEARCH_URL, params={
                "application_id": APP_ID,
                "search": nickname,
                "limit": 1
            }) as resp:
                data = await resp.json()

        if not data["data"]:
            await event.edit("❌ Игрок не найден.")
            return

        acc = data["data"][0]
        acc_id = str(acc["account_id"])

        # Стата
        async with aiohttp.ClientSession() as session:
            async with session.get(INFO_URL, params={
                "application_id": APP_ID,
                "account_id": acc_id
            }) as resp:
                info = await resp.json()

        stats = info["data"][acc_id]["statistics"]["all"]

        # берем 5 приближённых метрик как динамику
        graph_values = [
            stats.get("damage_dealt", 0),
            stats.get("frags", 0),
            stats.get("spotted", 0),
            stats.get("dropped_capture_points", 0),
            stats.get("xp", 0)
        ]

        plt.figure(figsize=(7, 4))
        plt.plot(graph_values)
        plt.title(f"Progress graph: {acc['nickname']}")
        plt.xlabel("Metric")
        plt.ylabel("Value")
        plt.tight_layout()

        filepath = "/mnt/data/tbgraph.png"
        plt.savefig(filepath)
        plt.close()

        await client.send_file(event.chat_id, filepath, caption=f"📈 График {acc['nickname']}")
        await event.delete()