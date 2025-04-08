from telebot import types
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
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
        return bot.send_message(message.chat.id, "Произошла ошибка. Пожалуйста, начните заново, отправив команду /start.")

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
        bot.send_message(message.chat.id, "Благодарим! Регистрация успешно завершена. Теперь Вы можете воспользоваться нашей платформой.")
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

    bot.send_message(message.chat.id, "Привет! Какой тип помощи Вам нужн? (пока без клавиатури)")
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
    USER = send_sql('select 1 from main_user where telegram_id = (%s)', (message.from_user.id))
    if not USER:
        bot.send_message(message.chat.id, "Вы еще не зарегистрированы!")
        return
    send_sql('delete from main_user where telegram_id = (%s)', (message.from_user.id))
    bot.send_message(message.chat.id, "Ваш аккаунт удален из системы.")

def process_task_type(message):
    task_type = message.text
    bot.send_message(message.chat.id, "Опишите проблемю")
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
        f"📥 Новая форма #{order_id}!\n\n"
        f"🔧 Тип: {task_type}\n"
        f"📝 Описание: {description}\n"
        f"👤 Пользователь: @{message.from_user.username or message.from_user.full_name}"
    )

    bot.send_message(chat_id=TEAM_CHAT_ID, text=order_info, reply_markup=keyboard)
    bot.send_message(message.chat.id, "Форма отправлена <|-_-|>")


@bot.message_handler(commands=['verify'])
def verify(message):
    conn = sqlite3.connect('db.sqlite3')
    curs = conn.cursor()

    curs.execute('select * from main_user where telegram_id = ?', (message.from_user.id,))
    user = curs.fetchone()

    if not user:
        bot.send_message(message.chat.id, "Вам нужно зарегистрироваться на платформе!")
        return
    else: print('пользователь найден')

    bot.send_message(message.chat.id, "Отправьте документ, удостоверяющий личность.")

    time.sleep(3)
    bot.send_message(message.chat.id, reply)
    bot.register_next_step_handler(message, process_task_type)

    conn.close()

@bot.callback_query_handler(func=lambda call: call.data.startswith("accept_"))
def accept_order(call):
    global curs, conn
    order_id = int(call.data.split("_")[1])
    curs.execute('select * from orders where id = %s', (order_id))
    # order = orders.get(order_id)

    order = curs.fetchall()[0]

    if not order:
        bot.answer_callback_query(call.id, "Заказ не найден.")
        return

    order["status"] = "В работе"
    order["executor"] = call.from_user.username or call.from_user.full_name

    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text="✅ Завершить", callback_data=f"finish_{order_id}"),
                 InlineKeyboardButton(text="⚙️ Настройка", callback_data=f"setup_{order_id}"),
                 InlineKeyboardButton(text="❌ Отменить", callback_data=f"reject_{order_id}"))

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=call.message.text + f"\n\n✅ Взято в работу: {order['executor']}",
        reply_markup=keyboard
    )

    bot.send_message(
        chat_id=order["user_id"],
        text=f"Твой заказ #{order_id} принят в работу! 🚀 Исполнитель: @{order['executor']}"
    )

    curs.execute("update orders "
                 f"SET status = 'В работе', executor = %s "
                 "where id = %s ",
                 (order['executor'], order_id)
                 )

    conn.commit()

    bot.answer_callback_query(call.id, "Ты взял заказ!")


@bot.callback_query_handler(func=lambda call: call.data.startswith("finish_"))
def finish_order(call):
    global curs, conn
    order_id = int(call.data.split("_")[1])
    curs.execute('select * from orders where id = %s', (order_id))
    # order = orders.get(order_id)

    order = curs.fetchall()[0]



    if not order:
        bot.answer_callback_query(call.id, "Заказ не найден.")
        return
    if not order['executor']:
        order['executor'] = call.from_user.username

    if order['executor'] != call.from_user.username:
        print(f'{call.from_user.username}!={order["executor"]}')
        return
    order["status"] = "Завершён"
    order["executor"] = call.from_user.username or call.from_user.full_name

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=call.message.text + f"\n\n✅ Завершён",

    )

    bot.send_message(
        chat_id=order["user_id"],
        text=f"Твой заказ #{order_id} ({order['task_type']}) завершён! Связаться: @{order['executor']}"
    )

    curs.execute("update orders "
                 f"SET status = 'В работе', executor = %s "
                 "where id = %s ",
                 (order['executor'], order_id)
                 )

    conn.commit()

    bot.answer_callback_query(call.id, "Ты взял заказ!")

@bot.callback_query_handler(func=lambda call: call.data.startswith("reject_"))
def reject_order(call):
    # try:
        order_id = int(call.data.split("_")[1])
        order = send_sql('select * from main_helprequest where id = %s', (order_id))[0]

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

        bot.send_message(
            chat_id=order["user_id"],
            text=f"Твой заказ #{order_id} был отклонён ❌ {order['executor']}"
        )

        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=call.message.text + "\n\n❌ Заказ отклонён"
        )
        send_sql("update main_helprequest "
                     f"SET status = 'Отклонён', assigned_volunteer_id = %s "
                     "where id = %s",
                     (order['assigned_volunteer_id'], order_id)
                     )

        bot.answer_callback_query(call.id, "Заказ отклонён.")
    # except:
    #     print('Не удалось отклонить :(')



bot.infinity_polling()
