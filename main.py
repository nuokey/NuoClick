import telebot
from telebot import types
import sqlite3
import time

import config

bot = telebot.TeleBot(config.token)

print('Bot started')

@bot.message_handler(commands=['start'])
def start_message(message):
	db = sqlite3.connect('data.db')
	cursor = db.cursor()
	user_balance = None

	keyboard = types.ReplyKeyboardMarkup()
	keyboard.row('Click', 'Balance')

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

		if user_balance != None:
			if message.text == 'Click':
				cursor.execute(f"UPDATE users SET balance = {user_balance + 1} WHERE user_id = {message.from_user.id}")
				db.commit()
			elif message.text == 'Balance':
				bot.send_message(message.from_user.id, str(user_balance))
		else:
			bot.send_message(message.from_user.id, 'Вы не зарегистрированы, напишите команду /start')

		user_balance = None
	except Exception as e:
		print(e)

try:
	bot.polling()
except Exception as e:
	print(e)