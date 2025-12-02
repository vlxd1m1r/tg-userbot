import os
from telethon import TelegramClient
from dotenv import load_dotenv

# загружаем переменные окружения
load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")

# создаем telethon-клиент
client = TelegramClient("userbot_session", API_ID, API_HASH)

# импорт и регистрация команд
from commands import (
    help_cmd,
    ping_cmd,
    tb_cmd,
    tbinfo_cmd,
    tbwn_cmd,
    tblast_cmd,
    tbgraph_cmd,
)

help_cmd.register(client)
ping_cmd.register(client)
tb_cmd.register(client)
tbinfo_cmd.register(client)
tbwn_cmd.register(client)
tblast_cmd.register(client)
tbgraph_cmd.register(client)

print("Userbot запущен. Ожидание команд...")

# запуск клиента
client.start()
client.run_until_disconnected()