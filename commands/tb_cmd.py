from telethon import events
import aiohttp
import os

APP_ID = os.getenv("TB_APPLICATION_ID")

def register(client):
    @client.on(events.NewMessage(pattern=r"\.tb (.+)"))
    async def tb_handler(event):
        nickname = event.pattern_match.group(1)

        await event.edit("🔍 Ищу игрока...")

        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://papi.tanksblitz.ru/wotb/account/list/",
                params={"application_id": APP_ID, "search": nickname, "limit": 1}
            ) as resp:
                data = await resp.json()

        if not data["data"]:
            return await event.edit("❌ Игрок не найден.")

        player = data["data"][0]
        await event.edit(f"Игрок найден: **{player['nickname']}**\nID: `{player['account_id']}`")
