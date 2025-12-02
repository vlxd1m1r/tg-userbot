import aiohttp
import os
from telethon import events
from dotenv import load_dotenv

load_dotenv()
APP_ID = os.getenv("TB_APPLICATION_ID")

SEARCH_URL = "https://papi.tanksblitz.ru/wotb/account/list"
INFO_URL   = "https://papi.tanksblitz.ru/wotb/account/info"

def register(client):
    @client.on(events.NewMessage(pattern=r"\.tbwn (.+)"))
    async def tbwn(event):
        nickname = event.pattern_match.group(1).strip()
        await event.edit(f"🔍 Ищу игрока **{nickname}**...")

        # Поиск ID
        async with aiohttp.ClientSession() as session:
            async with session.get(SEARCH_URL, params={
                "application_id": APP_ID,
                "search": nickname,
                "limit": 1
            }) as resp:
                data = await resp.json()

        if not data.get("data"):
            await event.edit("❌ Игрок не найден.")
            return

        user = data["data"][0]
        user_id = str(user["account_id"])

        # Стата
        async with aiohttp.ClientSession() as session:
            async with session.get(INFO_URL, params={
                "application_id": APP_ID,
                "account_id": user_id
            }) as resp:
                info = await resp.json()

        stats = info["data"][user_id]["statistics"]["all"]
        battles = stats["battles"]
        wins = stats["wins"]
        winrate = round(wins / battles * 100, 2) if battles else 0

        await event.edit(
            f"📌 **{user['nickname']}**\n\n"
            f"🔥 Бои: {battles}\n"
            f"🎯 Победы: {wins}\n"
            f"📈 Winrate: **{winrate}%**"
        )