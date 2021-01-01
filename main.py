import telebot
from telebot import types
import sqlite3
import time

import config

bot = telebot.TeleBot(config.test_token)

print('ClickBot started')

@bot.message_handler(commands=['start'])
def start_message(message):
	db = sqlite3.connect('data.db')
	cursor = db.cursor()
	user_balance = None

	keyboard = types.ReplyKeyboardMarkup()
	keyboard.row('Click', 'Shop')

	bot.send_message(message.from_user.id, 'ClickBot\nVersion: 0.1', reply_markup=keyboard)

	for i in cursor.execute(f"SELECT balance FROM users WHERE user_id = {message.from_user.id}"):
		user_balance = i[0]

	if user_balance == None:
		cursor.execute(f"INSERT INTO users VALUES ({message.from_user.id}, 0)")
		db.commit()
		bot.send_message(message.from_user.id, 'Вы зарегистрированы успешно')

@bot.message_handler(content_types=['text'])
def text_message(message):
	try:
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
				shop_keyboard = types.InlineKeyboardMarkup()

				key_click_plus1 = types.InlineKeyboardButton(text="Click upgrade +1", callback_data="shop_click_plus1")
				key_click_plus2 = types.InlineKeyboardButton(text="Click upgrade +2", callback_data="shop_click_plus2")
				key_click_plus5 = types.InlineKeyboardButton(text="Click upgrade +5", callback_data="shop_click_plus5")
				key_click_plus10 = types.InlineKeyboardButton(text="Click upgrade +10", callback_data="shop_click_plus10")
				key_click_plus100 = types.InlineKeyboardButton(text="Click upgrade +100", callback_data="shop_click_plus100")

				shop_keyboard.add(key_click_plus1)
				shop_keyboard.add(key_click_plus1)
				shop_keyboard.add(key_click_plus1)
				shop_keyboard.add(key_click_plus1)
				shop_keyboard.add(key_click_plus1)

				bot.send_message(message.from_user.id, f'МАГАЗИН\nВаш баланс: {user_balance}', reply_markup=shop_keyboard)

		else:
			bot.send_message(message.from_user.id, 'Вы не зарегистрированы, напишите команду /start')

		user_balance = None
	except Exception as e:
		print(e)

@bot.callback_query_handler(func=lambda call: True)
def callback_answer(call):
	if call.data[0:15] == "shop_click_plus":
		db = sqlite3.connect('data.db')
		cursor = db.cursor()

		for i in cursor.execute(f"SELECT click FROM users WHERE user_id = {call.from_user.id}"):
			click = i[0]

		for i in cursor.execute(f"SELECT balance FROM users WHERE user_id = {call.from_user.id}"):
			balance = i[0]

		if int(call.data[15]) == 1 and balance >= 100:
			cursor.execute(f'UPDATE users SET click = {click + int(call.data[15])} WHERE user_id = {call.from_user.id}')
			cursor.execute(f'UPDATE users SET balance = {balance - 100} WHERE user_id = {call.from_user.id}')
			bot.edit_message_text(f'МАГАЗИН\nВаш баланс: {balance - 100}', chat_id=call.from_user.id, message_id=call.message.id)

		db.commit()

# try:
bot.polling()
# except Exception as e:
# 	print(e)