from telebot import types
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from telebot.types import ReactionTypeEmoji

from dotenv import load_dotenv
import os, json, sqlite3, telebot, time, requests

load_dotenv()

API_TOKEN = os.getenv('TELEGRAM_BOT_API_TOKEN')
print(f'Апи токен: {API_TOKEN}')

TEAM_CHAT_ID = '-1002275808520'
#TEAM_CHAT_ID=

user_states = {}

bot = telebot.TeleBot(API_TOKEN)

def send_sql(sql, params=None, url='http://localhost:8000/api/sql/'):
    headers = {'Content-Type': 'application/json'}
    payload = {'sql': sql}
    if params is not None:
        payload['params'] = params
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        try:
            return response.json()
        except:
            return {'error': str(e)}


def delete_message(message):
    print(f'\n\n{message=}\n\n')
    bot.delete_message(message['chat']['id'], message['message_id'])


def registration_handler(message):
    global user_states
    user_id = message.from_user.id
    state = user_states.get(user_id)

    if not state:
        bot.register_next_step_handler(message, registration_handler)
        return


    step = state['step']
    data = state['data']

    if step == 0:
        data['city'] = message.text
        bot.send_message(message.chat.id, "Укажите, пожалуйста, Ваш адрес электронной почты:")
    elif step == 1:
        data['email'] = message.text
        bot.send_message(message.chat.id, "Пожалуйста, введите Ваше имя:")
    elif step == 2:
        data['first_name'] = message.text
        bot.send_message(message.chat.id, "Теперь введите фамилию:")
    elif step == 3:
        data['last_name'] = message.text
        bot.send_message(message.chat.id, "Укажите Ваш возраст:")
    elif step == 4:
        try:
            data['age'] = int(message.text)
        except ValueError:
            bot.send_message(message.chat.id, "Пожалуйста, введите возраст цифрами.")
            return bot.register_next_step_handler(message, registration_handler)

        data['telegram_id'] = user_id
        data['username'] = message.from_user.username or message.from_user.full_name

        response = send_sql(
            "INSERT INTO main_user (telegram_id, username, city, email, first_name, last_name, age, password, is_superuser, is_staff, is_active, date_joined, role, verified) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, false, false, true, CURRENT_TIMESTAMP, 'user', false);",
            [
                data['telegram_id'],
                data['username'],
                data['city'],
                data['email'],
                data['first_name'],
                data['last_name'],
                data['age'],
                'pbkdf2_sha256$870000$xJJhbjEK4sgsdOWgmNzYjb$DyUBZpxdWO5y2LUbKIiqYomp0nUSP04FhyeSE1OF+Ds='
            ]
        )
        print(f'{response=}')
        bot.send_message(message.chat.id, "Теперь вам нужно подтвердить личность командой /verify !")
        user_states.pop(user_id, None)
        return

    state['step'] += 1
    bot.register_next_step_handler(message, registration_handler)

@bot.message_handler(commands=['start'])
def cmd_start(message):
    global user_states
    USER = send_sql('select * from main_user where telegram_id = %s', ([message.from_user.id]))['result']
    print(f'{USER=}')
    print(f'{message.from_user.id=}')
    if not USER:
        bot.send_message(message.chat.id, "Сначала нужно пройти опрос для регистрации!")
        bot.send_message(message.chat.id, "Пожалуйста, укажите регион и населённый пункт проживания:")
        user_states[message.from_user.id] = {'step':0, 'data':{}}
        bot.register_next_step_handler(message, registration_handler)
        return

    USER = USER[0]

    bot.send_message(message.chat.id, "Привет! Придумайте название своей проблеме.")
    bot.register_next_step_handler(message, process_task_type)

@bot.message_handler(commands=['users'])
def users(message):
    global user_states
    USER = send_sql('select * from main_user')
    print(f'{USER=}')
    print(f'{message.from_user.id=}')

    bot.send_message(message.chat.id, str(USER))

@bot.message_handler(commands=['deleteaccount'])
def delete_account(message):
    USER = send_sql('select * from main_user where telegram_id = %s', [message.from_user.id])['result']

    if not USER:
        bot.send_message(message.chat.id, "Вы еще не зарегистрированы!")
        return
    USER = USER[0]
    print(f'{USER=}')
    send_sql('delete from main_helprequest where user_id = %s', [USER['id']])
    print(f"{send_sql('delete from main_user where telegram_id = %s', [message.from_user.id])=}")
    bot.send_message(message.chat.id, "Ваш аккаунт удален из системы.")

@bot.message_handler(commands=['me'])
def delete_account(message):
    USER = send_sql('select * from main_user where telegram_id = %s', [message.from_user.id])['result']

    if not USER:
        bot.send_message(message.chat.id, "Вы еще не зарегистрированы!")
        return
    USER = USER[0]
    print(f'{USER=}')
    bot.send_message(message.chat.id, "Сведения об аккаунте: \n\n"
                                  f"Имя:               {USER['first_name']}\n"
                                  f"Фамилия:      {USER['last_name']}\n"
                                  f"Возраст:         {USER['age']}\n"
                                  f"Город:             {USER['city']}\n"
                                  f"Верифицирован: {'да' if USER['verified'] else 'нет (/verify)'}\n\n"
                                  f"🛑 Удалить аккаунт - /deleteaccount 🛑")

def process_task_type(message):
    task_type = message.text
    bot.send_message(message.chat.id, "Опишите проблему.")
    bot.register_next_step_handler(message, process_description, task_type)

def process_description(message, task_type):
    description = message.text
    bot.send_message(message.chat.id, 'Подтвердите отправку формы, написав "ДА"')
    bot.register_next_step_handler(message, process_wishes, task_type, description)

def process_wishes(message, task_type, description):
    acception = message.text

    if acception.lower() != 'да':
        bot.send_message(message.chat.id, f'Отправка отменена')
        return

    user = send_sql('select * from main_user where telegram_id = %s', (message.from_user.id,))['result'][0]
    response = send_sql(
        "insert into main_helprequest (user_id, title, description, created_at, status, location, telegram_notified)"
        "values"    
        "(%s, (%s), (%s), CURRENT_TIMESTAMP, 'В ожидании', (%s), false);",
        (user['id'],
         task_type,
         description,
         user['city'])
    )

    print(f'{response=}')
    order_id = response['lastrowid']

    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text="✅ Принять", callback_data=f"accept_{order_id}"),
                 InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_{order_id}"))
    order_info = (
        f"Новая форма #{order_id}!\n\n"
        f""
        f"Название: {task_type}\n"
        f"Проблема: {description}\n\n"
        f"Город: {user['city']}\n"
        f"{'Личность подтверждена' if user['verified'] else 'Не подтверждённый пользователь'}\n"
        f"Контакт: @{message.from_user.username or message.from_user.full_name}"
    )

    bot.send_message(chat_id=TEAM_CHAT_ID, text=order_info, reply_markup=keyboard)
    bot.send_message(message.chat.id, "Форма отправлена <|-_-|>")

@bot.message_handler(commands=['verify'])
def verify(message):
    user = send_sql('select * from main_user where telegram_id = %s', (message.from_user.id,))['result']
    if not user:
        bot.send_message(message.chat.id, "Вам необходимо зарегистрироваться на платформе перед верификацией.")
        return
    bot.send_message(message.chat.id, "Пожалуйста, отправьте одну или несколько фотографий документа, удостоверяющего личность.")
    bot.register_next_step_handler(message, collect_verification_photos)

def collect_verification_photos(message):
    user_id = message.from_user.id
    if message.content_type != 'photo':
        bot.send_message(message.chat.id, "Пожалуйста, отправьте именно фотографии.")
        return bot.register_next_step_handler(message, collect_verification_photos)
    if user_id not in user_states:
        user_states[user_id] = {'docs': []}
    file_id = message.photo[-1].file_id
    user_states[user_id]['docs'].append(file_id)
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("Отправить", "Ещё")
    bot.send_message(message.chat.id, "Фото получено. Хотите отправить заявку или добавить ещё?", reply_markup=markup)
    bot.register_next_step_handler(message, handle_verify_decision)

def handle_verify_decision(message):
    if message.text == "Ещё":
        bot.send_message(message.chat.id, "Отправьте следующее фото.")
        return bot.register_next_step_handler(message, collect_verification_photos)
    elif message.text == "Отправить":
        user_id = message.from_user.id
        photos = user_states.get(user_id, {}).get('docs', [])
        if not photos:
            bot.send_message(message.chat.id, "Нет загруженных фотографий. Начните заново с /verify", reply_markup=ReplyKeyboardRemove())
            return
        USER = send_sql('select * from main_user where telegram_id = %s', ([message.from_user.id]))['result']

        if USER: user = USER[0]

        caption = f"Заявка на верификацию от @{message.from_user.username or message.from_user.full_name}\nИмя, фамилия: {user['first_name']} {user['last_name']}. Возраст: {user['age']}, место жительства: {user['city']}\nTelegram ID: {user_id}"
        inline_markup = InlineKeyboardMarkup()
        inline_markup.add(
            InlineKeyboardButton("Подтвердить", callback_data=f"verify_accept_{user_id}"),
            InlineKeyboardButton("Отклонить", callback_data=f"verify_reject_{user_id}")
        )
        for i, photo in enumerate(photos):
            if i == 0:
                bot.send_photo(chat_id=TEAM_CHAT_ID, photo=photo, caption=caption, reply_markup=inline_markup)
            else:
                bot.send_photo(chat_id=TEAM_CHAT_ID, photo=photo)
        bot.send_message(message.chat.id, "Документы отправлены на проверку. Ожидайте результата.", reply_markup=ReplyKeyboardRemove())
        del user_states[user_id]
    else:
        bot.send_message(message.chat.id, "Ответ не распознан. Пожалуйста, повторите команду /verify")

@bot.callback_query_handler(func=lambda call: call.data.startswith("verify_accept_"))
def process_verify_accept(call):
    telegram_id = int(call.data.split("_")[-1])
    send_sql("UPDATE main_user SET verified = true WHERE telegram_id = %s", (telegram_id,))
    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=None)
    bot.send_message(chat_id=telegram_id, text="Ваша заявка на верификацию подтверждена.")
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("verify_reject_"))
def process_verify_reject(call):
    telegram_id = int(call.data.split("_")[-1])
    send_sql("UPDATE main_user SET verified = false WHERE telegram_id = %s", (telegram_id,))
    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=None)
    bot.send_message(chat_id=telegram_id, text="Ваша заявка на верификацию отклонена.")
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith("accept_"))
def accept_order(call):
    order_id = int(call.data.split("_")[1])
    order = send_sql('select * from main_helprequest where id = %s', [order_id])['result'][0]

    if not order:
        bot.answer_callback_query(call.id, "Заказ не найден.")
        return

    order["status"] = "В работе"
    order["assigned_volunteer_id"] = call.from_user.username or call.from_user.full_name

    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text="✅ Завершить", callback_data=f"finish_{order_id}"),
                 InlineKeyboardButton(text="❌ Отменить", callback_data=f"reject_{order_id}"))

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=call.message.text + f"\n\n✅ Принято: {order['assigned_volunteer_id']}",
        reply_markup=keyboard
    )

    chatidthatorderedhelp = send_sql(f'select * from main_user where id = {order["user_id"]}')['result'][0][
        'telegram_id']

    bot.send_message(
        chat_id=chatidthatorderedhelp,
        text=f"Ваша форма #{order_id} - {order['title']}, принята на рассмотрение {order['assigned_volunteer_id']}, с Вами свяжутся."
    )

    send_sql("update main_helprequest "
                 f"SET status = 'В работе', assigned_volunteer_id = %s "
                 "where id = %s ",
                 (order['assigned_volunteer_id'], order_id)
                 )

    bot.answer_callback_query(call.id, "Вы приняли #{order_id} - {order['title']} в работу.")


@bot.callback_query_handler(func=lambda call: call.data.startswith("finish_"))
def finish_order(call):
    order_id = int(call.data.split("_")[1])
    order = send_sql('select * from main_helprequest where id = %s', [order_id])['result'][0]

    if not order:
        bot.answer_callback_query(call.id, "Заказ не найден.")
        return
    if not order['executor']:
        order['executor'] = call.from_user.username

    if order['assigned_volunteer_id'] != call.from_user.username:
        print(f'{call.from_user.username}!={order["executor"]}')
        return
    order["status"] = "Завершено"
    order["assigned_volunteer_id"] = call.from_user.username or call.from_user.full_name

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=call.message.text + f"\n\n✅ Завершён",

    )

    chatidthatorderedhelp = send_sql(f'select * from main_user where id = {order["user_id"]}')['result'][0][
        'telegram_id']

    bot.send_message(
        chat_id=chatidthatorderedhelp,
        text=f"Ваша форма #{order_id} - {order['title']} помечена как завершённая! Связаться: @{order['executor']}"
    )

    send_sql("update orders "
                 f"SET status = 'В работе', assigned_volunteer_id = %s "
                 "where id = %s ",
                 (order['assigned_volunteer_id'], order_id)
                 )

    conn.commit()

    bot.answer_callback_query(call.id, "Вы взяли форму на обработку!")

@bot.callback_query_handler(func=lambda call: call.data.startswith("reject_"))
def reject_order(call):
    # try:
        order_id = int(call.data.split("_")[1])
        order = send_sql('select * from main_helprequest where id = %s', [order_id])['result'][0]
        print(f'{order=}')
        if not order:
            bot.answer_callback_query(call.id, "Заказ не найден.")
            return
        if not order['assigned_volunteer_id']:
            order['assigned_volunteer_id'] = call.from_user.username

        if order['assigned_volunteer_id'] != call.from_user.username:
            print(f'{call.from_user.username}!={order["assigned_volunteer_id"]}')
            return

        order["status"] = "Отклонён"
        order['assigned_volunteer_id'] = call.from_user.username or call.from_user.full_name


        chatidthatorderedhelp = send_sql(f'select * from main_user where id = {order["user_id"]}')['result'][0]['telegram_id']
        print(f'''{chatidthatorderedhelp=}''')

        bot.send_message(
            chat_id=chatidthatorderedhelp,
            text=f"Ваша форма #{order_id} - {order['title']}, была отклонена ❌ {order['assigned_volunteer_id']}"
        )

        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=call.message.text + f"\n\n❌ Форма отклонена @{order['assigned_volunteer_id']}"
        )
        send_sql("update main_helprequest "
                     f"SET status = 'Отклонён', assigned_volunteer_id = %s "
                     "where id = %s",
                     (order['assigned_volunteer_id'], order_id)
                     )

        bot.answer_callback_query(call.id, "❌ Форма отклонена")
    # except:
    #     print('Не удалось отклонить :(')



bot.infinity_polling()
