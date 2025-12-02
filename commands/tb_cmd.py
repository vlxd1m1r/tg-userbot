from telethon import events
import aiohttp
import os

APP_ID = os.getenv("TB_APPLICATION_ID")

def register(client):
    @client.on(events.NewMessage(pattern=r"\.tb (.+)"))
    async def tb_handler(event):
        search_input = event.pattern_match.group(1).strip()

        # Разделяем имена через запятую и убираем лишние пробелы
        nicknames_list = [n.strip() for n in search_input.split(",") if n.strip()]

        if not nicknames_list:
            return await event.edit("❌ Не указаны имена для поиска.")

        await event.edit("🔍 Ищу игрока...")

        found_players = {}

        async with aiohttp.ClientSession() as session:
            # --- Поиск exact ---
            if len(nicknames_list) <= 100:
                exact_param = ",".join(nicknames_list)
                params = {
                    "application_id": APP_ID,
                    "search": exact_param,
                    "type": "exact",
                    "limit": 100,
                    "language": "ru",
                    "fields": "account_id,nickname"
                }
                async with session.get(
                    "https://papi.tanksblitz.ru/wotb/account/list/",
                    params=params
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        for player in data.get("data", []):
                            found_players[player['account_id']] = player

            # --- Поиск startswith ---
            for nickname in nicknames_list:
                if len(nickname) < 3:
                    continue  # пропускаем короткие имена для startswith
                params = {
                    "application_id": APP_ID,
                    "search": nickname,
                    "type": "startswith",
                    "limit": 100,
                    "language": "ru",
                    "fields": "account_id,nickname"
                }
                async with session.get(
                    "https://papi.tanksblitz.ru/wotb/account/list/",
                    params=params
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        for player in data.get("data", []):
                            found_players[player['account_id']] = player  # убираем дубликаты по account_id

        if not found_players:
            return await event.edit("❌ Игроки не найдены.")

        # Формируем сообщение
        message = "Найденные игроки:\n\n"
        for player in found_players.values():
            message += f"**{player['nickname']}** — ID: `{player['account_id']}`\n"

        await event.edit(message)
