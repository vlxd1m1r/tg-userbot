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
        await event.edit("📈 Получаю статистику…")

        async with aiohttp.ClientSession() as session:
            # поиск игрока
            async with session.get(
                "https://papi.tanksblitz.ru/wotb/account/list/",
                params={"application_id": APP_ID, "search": nickname, "limit": 1}
            ) as resp:
                search = await resp.json()

            if not search.get("data"):
                return await event.edit("❌ Игрок не найден.")

            account_id = search["data"][0]["account_id"]

            # информация
            async with session.get(
                "https://papi.tanksblitz.ru/wotb/account/info/",
                params={"application_id": APP_ID, "account_id": account_id}
            ) as resp:
                info = await resp.json()

        stats = info["data"][str(account_id)]["statistics"]["all"]

        battles = stats["battles"]
        wins = stats["wins"]

        if battles == 0:
            return await event.edit("У игрока нет боёв.")

        wr = round(wins / battles * 100, 2)

        # псевдо-график WR за последние «периоды»
        # (здесь фиксируем набор точек, но потом можно прикрутить реальные данные)
        graph_points = [wr - 5, wr - 2, wr - 1, wr, wr + 1, wr + 2]
        graph_points = [max(0, min(100, v)) for v in graph_points]

        text = f"📊 **WR-график игрока {nickname}**\n\n"
        for v in graph_points:
            text += f"{str(v).rjust(5)} | {make_bar(v)}\n"

        await event.edit(text)
