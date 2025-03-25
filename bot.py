import telebot
import random
import logging
import os
import sys

from database import create_db, add_user, get_all_users, get_user_list
from bot_logic import gen_pass  # Функция генерации пароля
from bot_logic import orelreshka  # Функция для игры "Орел или Решка"

create_db()

# Настройка логирования
logging.basicConfig(filename='bot.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', encoding='utf-8')

bot = telebot.TeleBot("7905314753:AAGZL7Ip5KyIpCFOKjTqrQdVymzsPi-sn_I")  # Укажи свой токен
ADMINS = [1199448870]  # Укажи свой Telegram ID
ADMIN_PASSWORD = "gydinova0610201"  # Пароль для входа в админку
kamen = ["🪨 Камень", "✂️ Ножницы", "📄 Бумага"]
users = set()  # Список пользователей
calculator_state = {}
admin_access = {}
def create_knb_keyboard():
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    keyboard.add(
        telebot.types.KeyboardButton('🪨 Камень'),
        telebot.types.KeyboardButton('✂️ Ножницы'),
        telebot.types.KeyboardButton('📄 Бумага'),
        telebot.types.KeyboardButton('🔙 Назад')
    )
    return keyboard

def create_calculator_keyboard():
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=4)
    buttons = [
        '7', '8', '9', '/',
        '4', '5', '6', '*',
        '1', '2', '3', '-',
        '0', '.', '=', '+',
        '🔙 Назад'
    ]
    keyboard.add(*[telebot.types.KeyboardButton(b) for b in buttons])
    return keyboard

def create_keyboard(user_id):
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add('🔑 Сгенерировать пароль', '🪙 Орел или Решка')
    keyboard.add('🪨 Ножницы, Камень или Бумага', '🧮 Калькулятор')
    if user_id in ADMINS:
        keyboard.add('⚙️ Админ-панель')
    return keyboard

def create_admin_keyboard():
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("📢 Рассылка", "📊 Количество пользователей")
    keyboard.add("📜 Список пользователей", "📂 Получить логи")
    keyboard.add("🔄 Перезапустить бота", "❌ Выключить бота")
    keyboard.add("🔙 Назад")
    return keyboard

@bot.message_handler(commands=['start'])
def start_message(message):
    user_id = message.chat.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name

    add_user(user_id, username, first_name, last_name)  # Записываем пользователя в БД
    bot.reply_to(message, "Привет! Добро пожаловать в бота.", reply_markup=create_keyboard(user_id))

@bot.message_handler(func=lambda message: message.text == "📊 Количество пользователей" and message.chat.id in ADMINS)
def show_user_count(message):
    count = len(get_all_users())
    bot.reply_to(message, f"👥 Всего пользователей: {count}")

@bot.message_handler(func=lambda message: message.text == "🗑 Очистить логи" and message.chat.id in ADMINS)
def clear_logs(message):
    open(bot.log, "w").close()  # Очистка файла логов
    bot.reply_to(message, "🗑 Логи успешно очищены!", reply_markup=create_admin_keyboard())
    logging.info(f"🗑 Логи были очищены админом {message.chat.id}.")

@bot.message_handler(func=lambda message: message.text == '⚙️ Админ-панель')
def admin_panel(message):
    user_id = message.from_user.id
    if user_id in admin_access and admin_access[user_id]:  # Если уже ввел пароль
        bot.reply_to(message, "Добро пожаловать в админ-панель!", reply_markup=create_admin_keyboard())
    else:
        bot.reply_to(message, "Введите пароль для доступа к админ-панели:", reply_markup=telebot.types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, check_admin_password)

def check_admin_password(message):
    user_id = message.from_user.id
    if message.text == ADMIN_PASSWORD:
        admin_access[user_id] = True
        bot.reply_to(message, "Пароль верный! Добро пожаловать в админ-панель.", reply_markup=create_admin_keyboard())
    else:
        bot.reply_to(message, "Неверный пароль! Возвращаю в главное меню.", reply_markup=create_keyboard(user_id))

@bot.message_handler(func=lambda message: message.text == "📢 Рассылка" and message.chat.id in ADMINS)
def broadcast_start(message):
    bot.reply_to(message, "Введите сообщение для рассылки:")
    bot.register_next_step_handler(message, send_broadcast)

def send_broadcast(message):
    users = get_all_users()
    success, failed = 0, 0

    for user in users:
        try:
            bot.send_message(user, f"📢 Сообщение от Администрации:\n\n{message.text}")
            success += 1
        except:
            failed += 1

    bot.reply_to(message, f"✅ Успешно отправлено: {success}\n❌ Ошибок: {failed}")

@bot.message_handler(func=lambda message: message.text == "📜 Список пользователей" and message.chat.id in ADMINS)
def list_users(message):
    users = get_user_list()
    user_text = "\n".join(users)

    if len(user_text) > 4000:
        user_text = user_text[:4000]  # Ограничение Telegram

    bot.reply_to(message, f"📜 Список пользователей:\n{user_text}")

@bot.message_handler(func=lambda message: message.text == "🔄 Перезапустить бота" and message.chat.id in ADMINS)
def restart_bot(message):
    bot.reply_to(message, "🔄 Перезапуск бота...", reply_markup=create_admin_keyboard())
    logging.info(f"🔄 Бот был перезапущен админом {message.chat.id}.")
    os.execl(sys.executable, sys.executable, *sys.argv)

@bot.message_handler(func=lambda message: message.text == '📂 Получить логи' and message.chat.id in ADMINS)
def get_logs(message):
    if message.from_user.id in ADMINS:
        try:
            with open('bot.log', 'rb') as log_file:
                bot.send_document(message.chat.id, log_file, reply_markup=create_admin_keyboard())
        except FileNotFoundError:
            bot.reply_to(message, "Лог-файл не найден.", reply_markup=create_admin_keyboard())

@bot.message_handler(func=lambda message: message.text == '⛔ Выключить бота' and message.chat.id in ADMINS)
def shutdown_bot(message):
    if message.from_user.id in ADMINS:
        bot.reply_to(message, "Бот выключается...", reply_markup=create_admin_keyboard())
        os._exit(0)

@bot.message_handler(func=lambda message: message.text == '🔙 Назад')
def back_to_menu(message):
    bot.reply_to(message, "Вы вернулись в главное меню.", reply_markup=create_keyboard(message.from_user.id))

@bot.message_handler(func=lambda message: message.text == '🧮 Калькулятор')
def calculator_start(message):
    bot.reply_to(message, "Введите выражение с помощью кнопок.", reply_markup=create_calculator_keyboard())
    calculator_state[message.from_user.id] = {'expression': ''}

@bot.message_handler(func=lambda message: message.text in '0123456789+-*/.')
def handle_calculator_input(message):
    user_id = message.from_user.id
    if user_id not in calculator_state:
        return
    calculator_state[user_id]['expression'] += message.text
    bot.reply_to(message, f"Текущее выражение: {calculator_state[user_id]['expression']}", reply_markup=create_calculator_keyboard())

@bot.message_handler(func=lambda message: message.text == '=')
def calculate_result(message):
    user_id = message.from_user.id
    if user_id in calculator_state:
        expression = calculator_state[user_id]['expression']
        try:
            result = eval(expression, {"__builtins__": None}, {})
            bot.reply_to(message, f"Результат: {result}", reply_markup=create_calculator_keyboard())
            calculator_state[user_id]['expression'] = ''
        except Exception:
            bot.reply_to(message, "Ошибка в выражении. Попробуйте снова.", reply_markup=create_calculator_keyboard())

@bot.message_handler(func=lambda message: message.text == '🔑 Сгенерировать пароль')
def ask_password_length(message):
    bot.reply_to(message, "Сколько символов должен содержать ваш пароль?", reply_markup=telebot.types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, get_password_length)

def get_password_length(message):
    try:
        length = int(message.text)
        if length <= 0:
            raise ValueError
        password = gen_pass(length)
        bot.reply_to(message, f"Ваш сгенерированный пароль: {password}", reply_markup=create_keyboard(message.from_user.id))
    except ValueError:
        bot.reply_to(message, "Пожалуйста, введите валидное число.", reply_markup=create_keyboard(message.from_user.id))

@bot.message_handler(func=lambda message: message.text == '🪙 Орел или Решка')
def send_or(message):
    result = orelreshka()
    bot.reply_to(message, result, reply_markup=create_keyboard(message.from_user.id))

@bot.message_handler(func=lambda message: message.text == '🪨 Ножницы, Камень или Бумага')
def knb_start(message):
    bot.reply_to(message, "Выберите: Камень, Ножницы или Бумага.", reply_markup=create_knb_keyboard())
    logging.info(f"User {message.from_user.id} started 'Камень, Ножницы, Бумага'.")

@bot.message_handler(func=lambda message: message.text in ["🪨 Камень", "✂️ Ножницы", "📄 Бумага"])
def knb_play(message):
    user_choice = message.text
    bot_choice = random.choice(kamen)
    if user_choice == bot_choice:
        result = f"Ничья! Вы оба выбрали: {user_choice}"
    elif (user_choice == "🪨 Камень" and bot_choice == "✂️ Ножницы") or \
         (user_choice == "✂️ Ножницы" and bot_choice == "📄 Бумага") or \
         (user_choice == "📄 Бумага" and bot_choice == "🪨 Камень"):
        result = f"Победа игрока! Вы выбрали: {user_choice}, Бот выбрал: {bot_choice}"
    else:
        result = f"Победа бота! Вы выбрали: {user_choice}, Бот выбрал: {bot_choice}"
    bot.reply_to(message, result, reply_markup=create_knb_keyboard())
    logging.info(f"User {message.from_user.id} played 'Камень, Ножницы, Бумага'.")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, message.text)
    logging.info(f"User {message.from_user.id} sent message: {message.text}")

bot.infinity_polling()
