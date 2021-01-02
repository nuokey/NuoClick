import telebot
from telebot import types
import sqlite3
import time

import config

bot = telebot.TeleBot(config.token)
admins = [889696918]

shop_keyboard = types.InlineKeyboardMarkup()

key_click_plus1 = types.InlineKeyboardButton(text="Click upgrade +1 (500)", callback_data="shop_click_plus 1-500")
key_click_plus2 = types.InlineKeyboardButton(text="Click upgrade +2 (750)", callback_data="shop_click_plus 2-750")
key_click_plus5 = types.InlineKeyboardButton(text="Click upgrade +5 (2000)", callback_data="shop_click_plus 5-2000")
key_click_plus10 = types.InlineKeyboardButton(text="Click upgrade +10 (3000)", callback_data="shop_click_plus 10-3000")
key_click_plus100 = types.InlineKeyboardButton(text="Click upgrade +100 (25000)", callback_data="shop_click_plus 100-25000")

shop_keyboard.add(key_click_plus1)
shop_keyboard.add(key_click_plus2)
shop_keyboard.add(key_click_plus5)
shop_keyboard.add(key_click_plus10)
shop_keyboard.add(key_click_plus100)

print('ClickBot started')

@bot.message_handler(commands=['start'])
def start_message(message):
	db = sqlite3.connect('data.db')
	cursor = db.cursor()
	user_balance = None

	keyboard = types.ReplyKeyboardMarkup()
	keyboard.row('Click', 'Shop')

	bot.send_message(message.from_user.id, 'ClickBot\nVersion: 0.2', reply_markup=keyboard)

	for i in cursor.execute(f"SELECT balance FROM users WHERE user_id = {message.from_user.id}"):
		user_balance = i[0]

	if user_balance == None:
		cursor.execute(f"INSERT INTO users VALUES ({message.from_user.id}, 0, 1)")
		db.commit()
		bot.send_message(message.from_user.id, 'You have registered')

@bot.message_handler(content_types=['text'])
def text_message(message):
	print(message.from_user.username)
	global shop_keyboard
	db = sqlite3.connect('data.db')
	cursor = db.cursor()
	user_balance = None

	for i in cursor.execute(f"SELECT balance FROM users WHERE user_id = {message.from_user.id}"):
		user_balance = i[0]

	for i in cursor.execute(f"SELECT click FROM users WHERE user_id = {message.from_user.id}"):
		click = i[0]

	if user_balance != None:
		if message.text == 'Click':
			cursor.execute(f"UPDATE users SET balance = {user_balance + click} WHERE user_id = {message.from_user.id}")
			db.commit()

			bot.delete_message(message.from_user.id, message.message_id)

		elif message.text == 'Shop':

			bot.send_message(message.from_user.id, f'Shop\nCoins: {user_balance}\nCoins per click: {click}', reply_markup=shop_keyboard)

	else:
		bot.send_message(message.from_user.id, "You aren't registered, write /start")

	user_balance = None

@bot.callback_query_handler(func=lambda call: True)
def callback_answer(call):
	global shop_keyboard
	if call.data[0:15] == "shop_click_plus":
		db = sqlite3.connect('data.db')
		cursor = db.cursor()

		call_data = (call.data).split(' ')
		call_data = call_data[1].split('-')

		for i in cursor.execute(f"SELECT click FROM users WHERE user_id = {call.from_user.id}"):
			click = i[0]

		for i in cursor.execute(f"SELECT balance FROM users WHERE user_id = {call.from_user.id}"):
			balance = i[0]

		if balance >= int(call_data[1]):
			cursor.execute(f'UPDATE users SET click = {click + int(call_data[0])} WHERE user_id = {call.from_user.id}')
			cursor.execute(f'UPDATE users SET balance = {balance - int(call_data[1])} WHERE user_id = {call.from_user.id}')
			bot.edit_message_text(f'Shop\nCoins: {balance - int(call_data[1])}\nCoins per click: {click + int(call_data[0])}', chat_id=call.from_user.id, message_id=call.message.id)

		db.commit()

try:
	bot.polling()
except Exception as e:
	print(e)