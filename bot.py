# https://docs.aiogram.dev/en/dev-3.x/
# https://core.telegram.org/

# Bot определяет, на какие команды от пользователя и каким способом отвечать.
# Dispatcher позволяет отслеживать обновления.
# types позволит использовать базовые классы для аннотирования, то есть восприятия сообщений. 
# Например, будем использовать types.Message, позволяющий работать с приёмом текстовых сообщений пользователя
from transformers import pipeline
import asyncio
import configparser
from multiprocessing.connection import Client
import os
#from typing import Self
from aiogram import F, Bot, Dispatcher, types
from aiogram.fsm.context import FSMContext
#from aiogram.fsm import state
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import CommandStart, Command, or_f
from aiogram.types import BotCommand, ReplyKeyboardRemove #, KeyboardButtonPollType, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
#from aiogram.utils.keyboard import ReplyKeyboardBuilder
#from datetime import datetime, timedelta
from dotenv import find_dotenv, load_dotenv

# Считываем переменные окруждения
load_dotenv(find_dotenv())

# Инициализируем объекты bot и Dispatcher, передав первому токен
bot = Bot(token=os.getenv('TOKEN'))
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Определение состояний
class Form(StatesGroup):
    waiting_for_text = State()


# Загружаем модель для суммаризации
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

ALLOWED_UPDATES = ['message, edited_message']

private = [
    BotCommand(command='start', description='Старт'),
    BotCommand(command='help', description='Вывести список доступных команд'),
    BotCommand(command='load', description='Загрузить диалог'),
    BotCommand(command='summarize', description='Пересказать диалог'),
    BotCommand(command='about', description='Для чего нужен этот бот'),
    BotCommand(command='checkmodel', description='Посмотреть, какая модель сейчас загружена'),
    BotCommand(command='model', description='Выбор модели')
]

@dp.message(F.text.lower() == "старт")
@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer('Привет! Я виртуальный помощник. Моей основной функцией является суммаризация диалогов на английском языке.')


@dp.message(F.text.lower() == "что ты умеешь")
@dp.message(Command('about'))
async def about_cmd(message: types.Message):
    await message.answer("Данный бот предназначен для пересказа диалогов.")


@dp.message(F.text.lower() == "выбрать модель")
@dp.message(Command('model'))
async def model_cmd(message: types.Message):
    await message.answer("Здесь будет выбор модели. Функция находится в разработке.")


@dp.message(F.text.lower() == "текущая модель")
@dp.message(Command('checkmodel'))
async def check_cmd(message: types.Message):
    await message.answer("facebook/bart-large-cnn")


@dp.message((F.text.lower() == "пересказ") | (F.text.lower() == "суммаризация"))
@dp.message(Command('summarize'))
async def summarize_cmd(message: types.Message, state: FSMContext):
    data = await state.get_data()  # Получаем данные состояния
    user_input = data.get('user_input')

    if user_input:
        summary = summarizer(user_input, max_length=150, min_length=25, do_sample=False)
        await message.answer("Суммаризация: \n" + summary[0]['summary_text'])   
    else:
        await message.answer("Пожалуйста, сначала загрузите текст для суммаризации с помощью команды /load.")


@dp.message(F.text.lower() == "помощь")
@dp.message(Command('help'))
async def help_cmd(message: types.Message):
    commands_list = "\n".join([f"/{cmd.command} - {cmd.description}" for cmd in private])
    await message.answer(f"Доступные команды:\n{commands_list}")


@dp.message((F.text.lower() == "загрузить"))
@dp.message(Command('load'))
async def load_cmd(message: types.Message, state: FSMContext):
    await state.set_state(Form.waiting_for_text) # Устанавливаем состояние ожидания текста
    await message.answer("Пожалуйста, введите текст для суммаризации.", reply_markup=ReplyKeyboardRemove())


@dp.message(Form.waiting_for_text)
async def process_text(message: types.Message, state: FSMContext):
    user_input = message.text
    await state.update_data(user_input=message.text)  # Сохраняем текст в состоянии
    #await message.answer(user_input)
    await message.answer("Текст загружен. Теперь используйте команду /summarize для получения суммаризации.")


# Метод start_polling опрашивает сервер, проверяя на нём обновления. 
# Если они есть, то они приходят в Telegram.
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    #await bot.delete_my_commands(scope=types.BotCommandScopeAllPrivateChats) # Если понадобится удалить все меню
    await bot.set_my_commands(commands=private, scope=types.BotCommandScopeAllPrivateChats())
    await dp.start_polling(bot, allowed_updates=ALLOWED_UPDATES)

# Запускаем бота
if __name__ == '__main__':
    asyncio.run(main())
