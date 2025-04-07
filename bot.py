from telebot import types
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telebot.types import ReactionTypeEmoji

from dotenv import load_dotenv
import os, json, sqlite3, telebot

conn = sqlite3.connect('db.sqlite3')
curs = conn.cursor()

API_TOKEN = os.getenv('TELEGRAM_BOT_API_TOKEN')
 
def delete_message(message):
    print(f'\n\n{message=}\n\n')
    bot.delete_message(message['chat']['id'], message['message_id'])


@bot.message_handler(commands=['start'])
def cmd_start(message):
    bot.send_message(message.chat.id, "Привет! Придумай тему для заказа: ")
    bot.register_next_step_handler(message, process_task_type)

connection.close()