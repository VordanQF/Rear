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

    hello = "Привет! Я не знаю, что тебе нужно, но вот тебе список пользователей!"
    reply = ''
    curs.execute("select * from main_user")
    result = curs.fetchall()
    for el in result:
        reply += f"\n{el}"
    bot.send_message(message.chat.id, hello)
    time.sleep(3)
    bot.send_message(message.chat.id, reply)
    bot.register_next_step_handler(message, process_task_type)

    conn.close()

bot.infinity_polling()
