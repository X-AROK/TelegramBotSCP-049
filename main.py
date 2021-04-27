import telebot
import phrases
from database import Database
import pyscp
import re

bot = telebot.TeleBot('1724510257:AAG0wfkgQ-2kU4ba-1d-ihFyZ2KmfoBShpQ')
db = Database("scp49.sqlite3")
users = db.select_all()
wiki = pyscp.wikidot.Wiki('scpfoundation.net')


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    if db.select("user_id", message.from_user.id):
        key = telebot.types.KeyboardButton(text="Отписаться")
    else:
        key = telebot.types.KeyboardButton(text="Подписаться")
    keyboard.add(key)
    bot.send_message(message.from_user.id, phrases.welcome, reply_markup=keyboard)


@bot.message_handler(commands=['subscribe', ])
def command_subscribe(message):
    subscribe(message.from_user.id)


@bot.message_handler(commands=['unsubscribe', ])
def command_unsubscribe(message):
    unsubscribe(message.from_user.id)


@bot.message_handler(commands=['scp', ])
def command_scp(message):
    args = message.text.split()
    if len(args) > 1:
        scp_number = args[1]
        send_scp(message.from_user.id, scp_number)
    else:
        bot.send_message(message.from_user.id, phrases.scp_no_args)


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.from_user.id == 363876425 and message.text.lower().startswith("отправить "):
        send_admin_msg(message)
    elif message.text.lower() == 'подписаться':
        command_subscribe(message)
    elif message.text.lower() == 'отписаться':
        command_unsubscribe(message)
    elif message.text.lower().startswith("scp "):
        command_scp(message)


def send_admin_msg(message):
    msg = message.text.lower().replace("отправить ", '').capitalize()
    msg = '\"' + msg + '\"'
    for user in users:
        bot.send_message(user[1], phrases.admin_msg + msg)


def subscribe(userid):
    if db.insert(userid):
        global users
        users = db.select_all()
        keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        key_unsubscribe = telebot.types.KeyboardButton(text="Отписаться")
        keyboard.add(key_unsubscribe)
        bot.send_message(userid, phrases.subscribe, reply_markup=keyboard)
        print(f"[Info] Пользователь {userid} подписался.")
    else:
        bot.send_message(userid, phrases.error)


def unsubscribe(userid):
    if db.delete(userid):
        global users
        users = db.select_all()
        keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        key_subscribe = telebot.types.KeyboardButton(text="Подписаться")
        keyboard.add(key_subscribe)
        bot.send_message(userid, phrases.unsubscribe, reply_markup=keyboard)
        print(f"[Info] Пользователь {userid} отписался.")
    else:
        bot.send_message(userid, phrases.error)


def send_scp(userid, scp_number):
    [msg, images] = generate_scp_info(scp_number)
    bot.send_message(userid, msg, parse_mode="HTML")
    if len(images) > 0:
        bot.send_photo(userid, photo=images[0])
    if scp_number == "049" and msg != phrases.scp_not_found:
        bot.send_message(userid, phrases.scp49_found)


def generate_scp_info(scp_number):
    try:
        page = wiki(f'scp-{scp_number}')
        msg = f"<b>{page.title}</b>\n\n"
        msg += f"<b>{re.search(r'Класс объекта: .*', page.text).group(0)}</b>\n\n"
        msg += f"{re.search(r'Описание: .*', page.text).group(0)}\n\n"
        msg += page.url
    except Exception:
        return [phrases.scp_not_found, []]
    return [msg, page.images]


bot.polling(none_stop=True)
