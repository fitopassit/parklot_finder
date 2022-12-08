from aiogram import Bot, types
from aiogram.utils import executor
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
import pandas as pd
import os
import grab
import time

import logging
import ssl

from aiohttp import web

import telebot

API_TOKEN = '<api_token>'

WEBHOOK_HOST = '<ip/host where the bot is running>'
WEBHOOK_PORT = 8443  # 443, 80, 88 or 8443 (port need to be 'open')
WEBHOOK_LISTEN = '0.0.0.0'  # In some VPS you may need to put here the IP addr

WEBHOOK_SSL_CERT = './webhook_cert.pem'  # Path to the ssl certificate
WEBHOOK_SSL_PRIV = './webhook_pkey.pem'  # Path to the ssl private key

# Quick'n'dirty SSL certificate generation:
#
# openssl genrsa -out webhook_pkey.pem 2048
# openssl req -new -x509 -days 3650 -key webhook_pkey.pem -out webhook_cert.pem
#
# When asked for "Common Name (e.g. server FQDN or YOUR name)" you should reply
# with the same value in you put in WEBHOOK_HOST

WEBHOOK_URL_BASE = "https://{}:{}".format(WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/{}/".format(API_TOKEN)

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

bot = telebot.TeleBot(API_TOKEN)

app = web.Application()


# Process webhook calls
async def handle(request):
    if request.match_info.get('token') == bot.token:
        request_body_dict = await request.json()
        update = telebot.types.Update.de_json(request_body_dict)
        bot.process_new_updates([update])
        return web.Response()
    else:
        return web.Response(status=403)


app.router.add_post('/{token}/', handle)

bot = Bot('5642015418:AAGcUyEUS0quJUNU92rKoi_U909_Zp1Dayk')
#используем простой MemoryStorage для Dispatcher.
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)



class Form(StatesGroup):
    number = State()
    park = State()


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    in_keyboard = types.InlineKeyboardMarkup(row_width=2) #наша клавиатура
    key_yes = types.InlineKeyboardButton('Да', callback_data='yes') #кнопка «Да»
    key_no= types.InlineKeyboardButton('Нет', callback_data='no')

    in_keyboard.add(key_yes, key_no) #добавляем кнопки в клавиатуру
    hello = "Привет! Я помогу тебе найти свободное место на парковке!\nТы авторизирован в системе?"
    await bot.send_message(message.chat.id, text=hello, reply_markup=in_keyboard)
    
@dp.message_handler(content_types=['contact'])
async def contact(message):
    if 'message_id' in message:
        await get_number(message)
        
@dp.message_handler(content_types=['text'])
async def guide(message):
    if 'message_id' in message:
        await give_park(message)   
    
#@dp.message_handler(state=Form.number)
async def get_number(message: types.Message):
    number = int(message.contact.phone_number)
    numbers = pd.read_csv('numbers.csv')
    if (numbers['numbers'].isin([number]).any()):
        keyboard_2 = types.ReplyKeyboardMarkup(resize_keyboard = True, one_time_keyboard = True)
        key_park = types.KeyboardButton(text = 'Парковки')
        keyboard_2.add(key_park);
        await bot.send_message(message.chat.id, text = 'Нажми кнопку \"Парковки\", чтобы увидеть список парковок', reply_markup = keyboard_2)
        
    else:
        await bot.send_message(message.chat.id, "Твой номер не найден в системе, обратись к администратору бота")

#@dp.message_handler(state=Form.park)
async def give_park(message: types.Message):
    keyboard_3 = types.InlineKeyboardMarkup() #наша клавиатура
    key_1 = types.InlineKeyboardButton(text = 'Парковка 1', callback_data = '1') 
    keyboard_3.add(key_1) #добавляем кнопку в клавиатуру
    key_2= types.InlineKeyboardButton(text = 'Парковка 2', callback_data = '2')
    keyboard_3.add(key_2) #добавляем кнопку в клавиатуру
    key_3 = types.InlineKeyboardButton(text = 'Парковка 3', callback_data = '3')
    keyboard_3.add(key_3)
    await bot.send_message(message.chat.id, text='Информация по парковкам', reply_markup=keyboard_3)
        

@dp.callback_query_handler(lambda c: c.data)
async def callback_worker(call: types.CallbackQuery):
    
    if call.data == "yes": #call.data это callback_data, которую мы указали при объявлении кнопки
        re_keyboard = types.ReplyKeyboardMarkup(resize_keyboard = True, one_time_keyboard = True)
        key_number = types.KeyboardButton(text = 'Согласен', request_contact = True)
        re_keyboard.add(key_number);
        permission = "Для того, чтобы продолжить, мне необходимо получить разрешение на обработку данных твоего аккаунта Telegram"
        await bot.send_message(call.message.chat.id, text = permission, reply_markup = re_keyboard)
        
    elif call.data == "no":
        await bot.send_message(call.message.chat.id, "Чтобы получить доступ к системе, обратись к администратору бота")
        
    elif call.data == "1": #call.data это callback_data, которую мы указали при объявлении кнопки
        current_time = time.localtime()
        file_name =  time.strftime("%Y_%m_%d%H%M%S", current_time)
        url = 'http://91.203.177.39:85/webcapture.jpg?command=snap&channel=1?1667117757'
        grab.detect(url, file_name, call.data)
        await bot.send_photo(call.message.chat.id, open(f"./runs/detect/exp/{file_name}.png", 'rb'))
        await bot.send_message(call.message.chat.id, "Это парковка 1")


        #bot.edit_message_reply_markup(call.message.chat.id, message_id = call.message.message_id-2, reply_markup = '')# удаляем кнопки у последнего сообщения

    elif call.data == "2":
        current_time = time.localtime()
        file_name = time.strftime("%Y_%m_%d%H%M%S", current_time)
        url = 'http://37.44.45.106:8082/webcapture.jpg?command=snap&channel=1?1667117818'
        grab.detect(url, file_name,call.data)
        await bot.send_photo(call.message.chat.id, open(f"./runs/detect/exp/{file_name}.png", 'rb'))
        await bot.send_message(call.message.chat.id, "Это парковка 2")
    elif call.data == "3":
        current_time = time.localtime()
        file_name = time.strftime("%Y_%m_%d%H%M%S", current_time)
        url = 'http://89.250.150.72:90/webcapture.jpg?command=snap&channel=1?1666530319'
        grab.detect(url, file_name,call.data)
        await bot.send_photo(call.message.chat.id, open(f"./runs/detect/exp/{file_name}.png", 'rb'))
        await bot.send_message(call.message.chat.id, "Это парковка 3")


    



# Remove webhook, it fails sometimes the set if there is a previous webhook
bot.remove_webhook()

# Set webhook
bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH,
                certificate=open(WEBHOOK_SSL_CERT, 'r'))

# Build ssl context
context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
context.load_cert_chain(WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV)

# Start aiohttp server
web.run_app(
    app,
    host=WEBHOOK_LISTEN,
    port=WEBHOOK_PORT,
    ssl_context=context,
)