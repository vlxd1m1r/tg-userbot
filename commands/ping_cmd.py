from telethon import events
import time

def register(client):
    @client.on(events.NewMessage(pattern=r"\.ping"))
    async def ping_handler(event):
        start = time.time()
        await event.edit("Pong 🏓...")
        end = time.time()
        await event.edit(f"Pong 🏓 | Задержка: {round((end-start)*1000)}ms")
