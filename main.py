import telebot
import traceback
from telebot import types
import sqlite3

import texts

token = open("token.txt").read()

def post(message):
	try:
		db = sqlite3.connect('data.db')
		cursor = db.cursor()

		main_keyboard = types.ReplyKeyboardMarkup()
		main_keyboard.row('Click')

		for i in cursor.execute('SELECT id FROM users'):
			bot.send_message(i[0], message, reply_markup=main_keyboard)
	except Exception as e:
		print(e)

bot = telebot.TeleBot(token)
admins = [889696918]

db = sqlite3.connect('data.db')
cursor = db.cursor()

# Keyboards
# Profile
profile_keyboard = types.InlineKeyboardMarkup()

key_update = types.InlineKeyboardButton(text="Update", callback_data="to_profile")
key_shop = types.InlineKeyboardButton(text="Shop", callback_data="to_shop")
key_close = types.InlineKeyboardButton(text="Close", callback_data="profile_close")

profile_keyboard.add(key_update)
profile_keyboard.add(key_shop)
profile_keyboard.add(key_close)

# Shop
shop_keyboard = types.InlineKeyboardMarkup()

shop_prices = {}

upgrade_plus = []
upgrade_prices = []

for i in cursor.execute("SELECT upgrade_plus FROM shop_prices"):
	upgrade_plus.append(i[0])

for q in cursor.execute(f"SELECT price FROM shop_prices"):
	upgrade_prices.append(q[0])

for i in range(len(upgrade_plus)):
	shop_prices[upgrade_plus[i]] = upgrade_prices[i]

for i in shop_prices:
	exec(f'key_click_plus{i} = types.InlineKeyboardButton(text="Сlick upgrade +{i}", callback_data="shop_click_plus 1-{shop_prices.get(i)}")')
	exec(f'shop_keyboard.add(key_click_plus{i})')

key_shop_update = types.InlineKeyboardButton(text="Update", callback_data="to_shop")
key_shop_close = types.InlineKeyboardButton(text="Close", callback_data="to_profile")

shop_keyboard.add(key_shop_update)
shop_keyboard.add(key_shop_close)

# print('ClickBot started')
post('Бот запущен')

# Команда /start
@bot.message_handler(commands=['start'])
def start_message(message):
	try:
		db = sqlite3.connect('data.db')
		cursor = db.cursor()
		user_balance = None
		click = 1

		for i in cursor.execute(f"SELECT balance FROM users WHERE id = {message.from_user.id}"):
			user_balance = i[0]

		for i in cursor.execute(f"SELECT click FROM users WHERE id = {message.from_user.id}"):
			click = i[0]

		if user_balance == None:
			user_balance = 0
			cursor.execute(f'INSERT INTO users VALUES ({message.from_user.id}, "{message.from_user.username}", 0, 1, 0)')
			db.commit()
			bot.send_message(message.from_user.id, 'You have registered')

		bot.send_message(message.from_user.id, texts.profile_text(user_balance, click), reply_markup=profile_keyboard)
		
	except Exception as e:
		print(e)

# Команда /post
@bot.message_handler(commands=['post'])
def post_message(message):
	try:
		db = sqlite3.connect('data.db')
		cursor = db.cursor()

		if message.from_user.id in admins:
			post(message.text[5:len(message.text)])
	except Exception as e:
		print(e)

@bot.message_handler(content_types=['text'])
def text_message(message):
	try:
		print(message.from_user.username)
		global shop_keyboard
		db = sqlite3.connect('data.db')
		cursor = db.cursor()
		user_balance = None

		for i in cursor.execute(f"SELECT balance FROM users WHERE id = {message.from_user.id}"):
			user_balance = i[0]

		for i in cursor.execute(f"SELECT click FROM users WHERE id = {message.from_user.id}"):
			click = i[0]

		if user_balance != None:
			if message.text == 'Click':
				cursor.execute(f"UPDATE users SET balance = {user_balance + click} WHERE id = {message.from_user.id}")
				db.commit()

		else:
			bot.send_message(message.from_user.id, "You aren't registered, write /start")

		test_username = None

		for i in cursor.execute(f"SELECT name FROM users WHERE id = {message.from_user.id}"):
			test_username = i[0]

		cursor.execute(f'UPDATE users SET name = "{message.from_user.username}" WHERE id = {message.from_user.id}')
		db.commit()

		bot.delete_message(message.from_user.id, message.message_id)
		user_balance = None

	except Exception as e:
		print(e)

@bot.callback_query_handler(func=lambda call: True)
def callback_answer(call):
	try:
		global shop_keyboard
		db = sqlite3.connect('data.db')
		cursor = db.cursor()

		for i in cursor.execute(f"SELECT click FROM users WHERE id = {call.from_user.id}"):
			click = i[0]

		for i in cursor.execute(f"SELECT balance FROM users WHERE id = {call.from_user.id}"):
			balance = i[0]

		for i in cursor.execute(f"SELECT upgrade_number FROM users WHERE id = {call.from_user.id}"):
			upgrade_number = i[0]

		upgrade_number_cost = 1 + 0.1 * upgrade_number

		text = texts.shop_text(balance, click)

		if call.data[0:15] == "shop_click_plus":
			call_data = (call.data).split(' ')
			call_data = call_data[1].split('-')

			upgrade_cost = int(int(call_data[1]) * upgrade_number_cost)

			if balance >= upgrade_cost:
				cursor.execute(f'UPDATE users SET click = {click + int(call_data[0])} WHERE id = {call.from_user.id}')
				cursor.execute(f'UPDATE users SET balance = {balance - upgrade_cost} WHERE id = {call.from_user.id}')
				cursor.execute(f'UPDATE users SET upgrade_number = {upgrade_number + 1} WHERE id = {call.from_user.id}')

				upgrade_number_cost = 1 + 0.1 * upgrade_number + 0.1
				balance -= upgrade_cost
				click += int(call_data[0])

				bot.edit_message_text(text+' ', chat_id=call.from_user.id, message_id=call.message.message_id, reply_markup=None)
				bot.edit_message_text(text, chat_id=call.from_user.id, message_id=call.message.message_id, reply_markup=shop_keyboard)

		elif call.data == 'to_profile':
			bot.edit_message_text(texts.profile_text(balance, click), chat_id=call.from_user.id, message_id=call.message.message_id, reply_markup=profile_keyboard)
			
		elif call.data == 'to_shop':
			bot.edit_message_text(text, chat_id=call.from_user.id, message_id=call.message.message_id, reply_markup=shop_keyboard)
			

		elif call.data == 'profile_close':
			bot.delete_message(call.from_user.id, call.message.message_id)

		db.commit()
	
	except Exception as e:
		print(e)

try:
	bot.polling()
except Exception as e:
	print(e)