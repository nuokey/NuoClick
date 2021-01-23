import telebot
from telebot import types
import sqlite3
import time

import config

token = open('token.txt').read()

def post(message):
	db = sqlite3.connect('data.db')
	cursor = db.cursor()

	for i in cursor.execute('SELECT user_id FROM users'):
		bot.send_message(i[0], message)

bot = telebot.TeleBot(token)
admins = [889696918, 737286150, 773282852]

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

key_click_plus1 = types.InlineKeyboardButton(text="Click upgrade +1", callback_data=f"shop_click_plus 1-{config.click_upgrade1}")
key_click_plus5 = types.InlineKeyboardButton(text="Click upgrade +5", callback_data=f"shop_click_plus 5-{config.click_upgrade5}")
key_click_plus10 = types.InlineKeyboardButton(text="Click upgrade +10", callback_data=f"shop_click_plus 10-{config.click_upgrade10}")
key_click_plus100 = types.InlineKeyboardButton(text="Click upgrade +100", callback_data=f"shop_click_plus 100-{config.click_upgrade100}")
key_click_plus1000 = types.InlineKeyboardButton(text="Click upgrade +1000", callback_data=f"shop_click_plus 1000-{config.click_upgrade1000}")

shop_prices = {}

for i in cursor.execute("SELECT upgrade_plus FROM shop_prices"):
	print(0)
	for q in cursor.execute(f"SELECT price FROM shop_prices WHERE upgrade_plus = {i[0]}"):
		shop_prices[i[0]] = q[0]

print(shop_prices)

key_shop_update = types.InlineKeyboardButton(text="Update", callback_data="to_shop")
key_shop_close = types.InlineKeyboardButton(text="Close", callback_data="to_profile")

shop_keyboard.add(key_click_plus1)
shop_keyboard.add(key_click_plus5)
shop_keyboard.add(key_click_plus10)
shop_keyboard.add(key_click_plus100)
shop_keyboard.add(key_click_plus1000)
shop_keyboard.add(key_shop_update)
shop_keyboard.add(key_shop_close)

print('ClickBot started')
# post('Бот запущен')

@bot.message_handler(commands=['start'])
def start_message(message):
	try:
		db = sqlite3.connect('data.db')
		cursor = db.cursor()
		user_balance = None

		main_keyboard = types.ReplyKeyboardMarkup()
		main_keyboard.row('Click', 'Profile')

		bot.send_message(message.from_user.id, "ClickBot\nVersion: 0.3", reply_markup=main_keyboard)

		for i in cursor.execute(f"SELECT balance FROM users WHERE user_id = {message.from_user.id}"):
			user_balance = i[0]

		if user_balance == None:
			cursor.execute(f"INSERT INTO users VALUES ({message.from_user.id}, 0, 1, 0)")
			db.commit()
			bot.send_message(message.from_user.id, 'You have registered')
	except:
		pass

@bot.message_handler(commands=['post'])
def post_message(message):
	try:
		db = sqlite3.connect('data.db')
		cursor = db.cursor()

		if message.from_user.id in admins:
			post(message.text[5:len(message.text)])
	except:
		pass

@bot.message_handler(content_types=['text'])
def text_message(message):
	try:
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

			elif message.text == 'Profile':
				bot.send_message(message.from_user.id, f'Your profile\nCoins: {user_balance}\nCoins per click: {click}', reply_markup=profile_keyboard)

		else:
			bot.send_message(message.from_user.id, "You aren't registered, write /start")

		bot.delete_message(message.from_user.id, message.message_id)
		user_balance = None
	except:
		pass

@bot.callback_query_handler(func=lambda call: True)
def callback_answer(call):
	try:
		global shop_keyboard
		print(0)
		db = sqlite3.connect('data.db')
		cursor = db.cursor()

		for i in cursor.execute(f"SELECT click FROM users WHERE user_id = {call.from_user.id}"):
			click = i[0]

		for i in cursor.execute(f"SELECT balance FROM users WHERE user_id = {call.from_user.id}"):
			balance = i[0]

		for i in cursor.execute(f"SELECT upgrade_number FROM users WHERE user_id = {call.from_user.id}"):
			upgrade_number = i[0]

		upgrade_number_cost = 1 + 0.1 * upgrade_number

		text = f'Shop\nCoins: {balance}\nCoins per click: {click}\n\nPlus 1: {int(config.click_upgrade1 * upgrade_number_cost)}\nPlus 5: {int(config.click_upgrade5 * upgrade_number_cost)}\nPlus 10: {int(config.click_upgrade10 * upgrade_number_cost)}\nPlus 100: {int(config.click_upgrade100 * upgrade_number_cost)}\nPlus 1000: {int(config.click_upgrade1000 * upgrade_number_cost)}'

		if call.data[0:15] == "shop_click_plus":
			call_data = (call.data).split(' ')
			call_data = call_data[1].split('-')

			upgrade_cost = int(int(call_data[1]) * upgrade_number_cost)

			if balance >= upgrade_cost:
				cursor.execute(f'UPDATE users SET click = {click + int(call_data[0])} WHERE user_id = {call.from_user.id}')
				cursor.execute(f'UPDATE users SET balance = {balance - upgrade_cost} WHERE user_id = {call.from_user.id}')
				cursor.execute(f'UPDATE users SET upgrade_number = {upgrade_number + 1} WHERE user_id = {call.from_user.id}')

				upgrade_number_cost = 1 + 0.1 * upgrade_number + 0.1
				balance -= upgrade_cost
				click += int(call_data[0])

				text = f'Shop\nCoins: {balance}\nCoins per click: {click}\n\nPlus 1: {int(config.click_upgrade1 * upgrade_number_cost)}\nPlus 5: {int(config.click_upgrade5 * upgrade_number_cost)}\nPlus 10: {int(config.click_upgrade10 * upgrade_number_cost)}\nPlus 100: {int(config.click_upgrade100 * upgrade_number_cost)}\nPlus 1000: {int(config.click_upgrade1000 * upgrade_number_cost)}'
				
				bot.edit_message_text(text+' ', chat_id=call.from_user.id, message_id=call.message.id, reply_markup=None)
				bot.edit_message_text(text, chat_id=call.from_user.id, message_id=call.message.id, reply_markup=shop_keyboard)

		elif call.data == 'to_profile':
			bot.edit_message_text(f'Your profile\nCoins: {balance}\nCoins per click: {click}', chat_id=call.from_user.id, message_id=call.message.id, reply_markup=profile_keyboard)
			
		elif call.data == 'to_shop':
			bot.edit_message_text(text, chat_id=call.from_user.id, message_id=call.message.id, reply_markup=shop_keyboard)
		
		elif call.data == 'profile_close':
			bot.delete_message(call.from_user.id, call.message.id)

		db.commit()
	
	except:
		pass

try:
	bot.polling()
except Exception as e:
	print(e)