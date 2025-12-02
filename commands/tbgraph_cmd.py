from telethon import events
import aiohttp
import os

APP_ID = os.getenv("TB_APPLICATION_ID")

def make_bar(value, max_value=100, width=20):
    filled = int((value / max_value) * width)
    return "█" * filled + "·" * (width - filled)

def register(client):
    @client.on(events.NewMessage(pattern=r"\.tbgraph (.+)"))
    async def tbgraph_handler(event):
        nickname = event.pattern_match.group(1).strip()
        if not nickname:
            return await event.edit("❌ Укажите никнейм игрока.")

        await event.edit("📈 Получаю статистику…")

        async with aiohttp.ClientSession() as session:
            found_player = None

            # --- Поиск exact ---
            params_exact = {
                "application_id": APP_ID,
                "search": nickname,
                "type": "exact",
                "limit": 1,
                "fields": "account_id,nickname"
            }
            async with session.get(
                "https://papi.tanksblitz.ru/wotb/account/list/",
                params=params_exact
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data.get("data"):
                        found_player = data["data"][0]

            # --- Поиск startswith (если exact не нашёл) ---
            if not found_player and len(nickname) >= 3:
                params_starts = {
                    "application_id": APP_ID,
                    "search": nickname,
                    "type": "startswith",
                    "limit": 1,
                    "fields": "account_id,nickname"
                }
                async with session.get(
                    "https://papi.tanksblitz.ru/wotb/account/list/",
                    params=params_starts
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if data.get("data"):
                            found_player = data["data"][0]

            if not found_player:
                return await event.edit("❌ Игрок не найден.")

            account_id = found_player["account_id"]
            nickname = found_player["nickname"]

            # --- Получаем статистику ---
            params_info = {
                "application_id": APP_ID,
                "account_id": account_id
            }
            async with session.get(
                "https://papi.tanksblitz.ru/wotb/account/info/",
                params=params_info
            ) as resp:
                if resp.status != 200:
                    return await event.edit(f"❌ Ошибка запроса статистики: {resp.status}")
                info = await resp.json()

        stats = info["data"][str(account_id)]["statistics"]["all"]
        battles = stats.get("battles", 0)
        wins = stats.get("wins", 0)

        if battles == 0:
            return await event.edit("У игрока нет боёв.")

        wr = round(wins / battles * 100, 2)

        # --- Симуляция графика WR ---
        graph_points = [wr - 5, wr - 2, wr - 1, wr, wr + 1, wr + 2]
        graph_points = [max(0, min(100, v)) for v in graph_points]

        text = f"📊 **WR-график игрока {nickname}**\n\n"
        for v in graph_points:
            text += f"{str(v).rjust(5)} | {make_bar(v)}\n"

        await event.edit(text)
