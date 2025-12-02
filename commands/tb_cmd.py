import os
from telethon import TelegramClient
from dotenv import load_dotenv

load_dotenv()
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")

client = TelegramClient('userbot_session', api_id, api_hash)

from commands import help_cmd, ping_cmd, tb_cmd

help_cmd.register(client)
ping_cmd.register(client)
tb_cmd.register(client)

print("Userbot запущен. Ожидание команд...")

client.start()
client.run_until_disconnected()