import aiohttp
import os
from telethon import events
from dotenv import load_dotenv

load_dotenv()

APP_ID = os.getenv("TB_APPLICATION_ID")

SEARCH_URL = "https://papi.tanksblitz.ru/wotb/account/list"
ACH_URL    = "https://papi.tanksblitz.ru/wotb/account/achievements"

def register(client):
    @client.on(events.NewMessage(pattern=r"\.tblastbattles (.+)"))
    async def tblast(event):
        nickname = event.pattern_match.group(1).strip()
        await event.edit(f"🔍 Ищу игрока **{nickname}**...")

        # Поиск аккаунта
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

        await event.edit(f"🔄 Получаю последние достижения игрока **{acc['nickname']}**...")

        async with aiohttp.ClientSession() as session:
            async with session.get(ACH_URL, params={
                "application_id": APP_ID,
                "account_id": acc_id
            }) as resp:
                ach = await resp.json()

        ach_data = ach["data"].get(acc_id, {})
        if not ach_data:
            await event.edit("❌ Не удалось получить достижения.")
            return

        text = f"📌 **Последние достижения {acc['nickname']}:**\n\n"

        for k, v in list(ach_data.items())[:10]:
            text += f"• {k}: {v}\n"

        await event.edit(text)