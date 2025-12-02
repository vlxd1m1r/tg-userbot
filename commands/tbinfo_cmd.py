import aiohttp
import os
from telethon import events
from dotenv import load_dotenv
from .cache import cache_get, cache_set

load_dotenv()

APP_ID = os.getenv("TB_APPLICATION_ID")

SEARCH_URL = "https://papi.tanksblitz.ru/wotb/account/list"
INFO_URL   = "https://papi.tanksblitz.ru/wotb/account/info"


def register(client):
    @client.on(events.NewMessage(pattern=r"\.tbinfo (.+)"))
    async def tbinfo_handler(event):
        nickname = event.pattern_match.group(1).strip()

        await event.edit(f"🔍 Ищу игрока **{nickname}**...")

        # КЭШ
        cache_key = f"tbinfo:{nickname.lower()}"
        cached = cache_get(cache_key)
        if cached:
            await event.edit(cached)
            return

        try:
            # 1) Поиск игрока по нику
            params = {
                "application_id": APP_ID,
                "search": nickname,
                "limit": 1
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(SEARCH_URL, params=params) as resp:
                    data = await resp.json()

            results = data.get("data", [])
            if not results:
                await event.edit(f"❌ Игрок **{nickname}** не найден.")
                return

            player = results[0]
            account_id = str(player["account_id"])
            real_nick = player["nickname"]

            await event.edit(f"📊 Нашел игрока **{real_nick}** (ID `{account_id}`)\nПолучаю статистику...")

            # 2) Запрос статистики по ID
            params = {
                "application_id": APP_ID,
                "account_id": account_id
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(INFO_URL, params=params) as resp:
                    data = await resp.json()

            player_info = data.get("data", {}).get(account_id)
            if not player_info:
                await event.edit("❌ Не удалось получить статистику.")
                return

            stats = player_info.get("statistics", {}).get("all", {})

            battles = stats.get("battles", 0)
            wins = stats.get("wins", 0)
            winrate = round(wins / battles * 100, 2) if battles else 0

            text = (
                f"📌 **Информация об игроке:**\n"
                f"👤 Ник: **{real_nick}**\n"
                f"🆔 ID: `{account_id}`\n\n"
                f"🔥 **Бои:** {battles}\n"
                f"🎯 **Победы:** {wins}\n"
                f"📈 **Процент побед:** {winrate}%\n"
                f"💥 **Средний урон:** {stats.get('damage_dealt', 0)}\n"
                f"🛡 Получено урона: {stats.get('damage_received', 0)}\n"
                f"⚡ Фраги: {stats.get('frags', 0)}\n"
            )

            cache_set(cache_key, text)
            await event.edit(text)

        except Exception as e:
            await event.edit(f"⚠️ Ошибка: `{str(e)}`")
