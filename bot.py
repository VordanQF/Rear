from telebot import types
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telebot.types import ReactionTypeEmoji

from dotenv import load_dotenv
import os, json, sqlite3, telebot, time

load_dotenv()

API_TOKEN = os.getenv('TELEGRAM_BOT_API_TOKEN')
print(f'Апи токен: {API_TOKEN}')

bot = telebot.TeleBot(API_TOKEN)

def delete_message(message):
    print(f'\n\n{message=}\n\n')
    bot.delete_message(message['chat']['id'], message['message_id'])


@bot.message_handler(commands=['start'])
def cmd_start(message):
    conn = sqlite3.connect('db.sqlite3')
    curs = conn.cursor()
    bot.send_message(message.chat.id, "Привет! Что будете заказывать? Выберите снизу!")
    curs.execute("select * from main_user")
    result = curs.fetchall()
    for el in result:
        reply += f"\n{el}"

    time.sleep(3)
    bot.send_message(message.chat.id, reply)
    bot.register_next_step_handler(message, process_task_type)

    conn.close()


@bot.message_handler(commands=['verify']))
def verify(message):
    conn = sqlite3.connect('db.sqlite3')
    curs = conn.cursor()

    curs.execute('select * from main_user where telegram_id = ?', (message.from_user.id,))
    user = curs.fetchone()

    if not user:
        bot.send_message(message.chat.id, "Вам нужно зарегистрироваться на платформе привязать телеграм!")
    else: print('пользователь найден')

    bot.send_message(message.chat.id, "Привет! Пришлите документы для подтверждения личности")
    curs.execute("select * from main_user")
    result = curs.fetchall()
    for el in result:
        reply += f"\n{el}"

    time.sleep(3)
    bot.send_message(message.chat.id, reply)
    bot.register_next_step_handler(message, process_task_type)

    conn.close()

bot.infinity_polling()
