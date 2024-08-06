import os
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty
from telethon.tl.functions.messages import GetHistoryRequest
import csv
from datetime import datetime, timedelta
from dotenv import find_dotenv, load_dotenv

# Считываем переменные окруждения из файла .env
load_dotenv(find_dotenv())

# Получаем API ID, API Hash и номер телефона из переменных окружения
api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
phone = os.getenv('PHONE')

# Создаем экземпляр клиента Telegram
client = TelegramClient(phone, api_id, api_hash)
client.start()

# Инициализируем переменные
chats = []
last_date = None
chunk_size = 200
groups = []

# Получаем список диалогов (чатов)
result = client(GetDialogsRequest(
    offset_date=last_date,
    offset_id=0,
    offset_peer=InputPeerEmpty(),
    limit=chunk_size,
    hash=0
))
chats.extend(result.chats)

# Выводим список групп для выбора
print("Выберите группу для парсинга сообщений:")
i = 0
for chat in chats:
    if hasattr(chat, 'title'):  # Проверяем, есть ли атрибут title
        print(f"{i} - {chat.title}") # Выводим название группы
        #if chat.title == 'Natural Language Processing':
            #target_group = chats[int(i)]
            #break
        i += 1

# Запрашиваем у пользователя номер группы
g_index = input("Введите нужную цифру: ")
# Получаем выбранную группу
target_group = chats[int(g_index)]

print(f"Выбрана группа: {target_group.title}")
print("Парсим сообщения...")

# Инициализируем переменные для парсинга сообщений
offset_id = 0
limit = 50
all_messages = []

k = 0
while True:
    # Получаем историю сообщений из выбранной группы
    history = client(GetHistoryRequest(
        peer=target_group,
        offset_id=offset_id,
        offset_date=None,
        add_offset=0,
        limit=limit,
        max_id=0,
        min_id=0,
        hash=0
    ))
    k+=1
    if (k > 1):
        break
    if not history.messages: # Если нет сообщений, выходим из цикла
        break
    

    messages = history.messages
    for message in messages:
        # Получаем информацию об отправителе
        sender = message.sender_id
        user = client.get_entity(sender) if sender else None
        username = user.username if user and user.username else "Неизвестный" # Имя пользователя
        message_time = message.date.strftime("%Y-%m-%d %H:%M:%S")  # Форматируем время

        # Добавляем сообщение в список
        all_messages.append([message_time, username, message.message])
    
    # Обновляем offset_id для следующей итерации
    offset_id = messages[len(messages) - 1].id

print("Сохраняем данные в файл...")

# Сохраняем собранные данные в CSV файл
with open("messages.csv", "w", encoding="UTF-8") as f:
    writer = csv.writer(f, delimiter=",", lineterminator="\n")
    writer.writerow(["Время", "Имя пользователя", "Сообщение"])  # Заголовки
    for message in all_messages:
        writer.writerow(message) # Записываем каждое сообщение

print('Парсинг сообщений группы успешно выполнен.')
