import telebot, datetime, pytz,time as tm
from telebot import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import *

tz = pytz.timezone('Asia/Yekaterinburg')
bot = telebot.TeleBot('6417863002:AAGeq0rVURHeAG-Mg-_PgwTI2rO5Phm3R-Y')

massiv = []

def menu(bot, message, messageId):
   bot.delete_message(message.chat.id, messageId)
   markup = InlineKeyboardMarkup(row_width=3)
   item1 = InlineKeyboardButton(text = "Словарь", callback_data = "dictionary")
   item2 = InlineKeyboardButton(text = "ТЕСТ", callback_data = "test")
   markup.add(item1, item2)
   try:
      bot.edit_message_text(chat_id=message.chat.id, message_id = messageId ,text = 'Вот что я могу сделать: ',  parse_mode='html', reply_markup=markup)
   except:
      bot.send_message(message.chat.id, 'Вот что я могу сделать: ',  parse_mode='html', reply_markup=markup)

def checkWorld(message,k,massiv,random_number, chat, messageId):
   bot.delete_message(message.chat.id, message.message_id)
   keyboard = InlineKeyboardMarkup()
   keyboard.add(InlineKeyboardButton('<--', callback_data = 'test'),InlineKeyboardButton('-->', callback_data = 'next'))
   if message.text.lower() == k.lower():
      massiv.pop(random_number)
      if massiv != []:
         random_number = (random.randint(0, (len(massiv))-1))
         for k in massiv[random_number].keys():
            bot.edit_message_text(chat_id=chat, message_id=messageId, text = f'{(len(massiv))}: Введи перевод слова {massiv[random_number][k]}: ')
            bot.register_next_step_handler(message, checkWorld, k,massiv,random_number, chat, messageId)
      else:
         menu(bot, message, messageId)
   else:
      bot.edit_message_text(chat_id=chat, message_id=messageId, text=f'Не правильно, верный перевод: {k}!',reply_markup = keyboard)

def crateMassive(message, chat, messageId):
   bot.delete_message(message.chat.id, message.message_id)
   cursor.execute("SELECT * FROM words")
   size = int(message.text)
   massive_big = cursor.fetchmany(size)
   if massiv != []:
      massiv.clear()

   for a in massive_big:
      kortej = dict([(a[0],a[1])])
      massiv.append(kortej)

   random_number = (random.randint(0, (len(massiv))-1))
   for k in massiv[random_number].keys():
      bot.edit_message_text(chat_id=chat, message_id=messageId, text = f'{(len(massiv))}: Введи перевод слова {massiv[random_number][k]}: ')
      bot.register_next_step_handler(message, checkWorld, k,massiv,random_number, chat, messageId)

#Действия после start
@bot.message_handler(commands=['start'])
def start_message(message):
   bot.send_message(message.from_user.id, f'Добро пожаловать, {message.from_user.first_name}', parse_mode='html')
   db_table_val(message, bot)
   menu(bot, message, message.id)

@bot.message_handler(commands=['menu'])
def message_menu(message):
   menu(bot, message, message.id)

#Действия callback
@bot.callback_query_handler(func=lambda callback: callback.data)
def callback(callback):
   mycallback(bot, callback)

#Действия когда пришёл текст
@bot.message_handler(content_types=["text"])
def bot_message(message):
   message_to_bot = message.text.lower()

   if message_to_bot == 'меню' or message_to_bot == 'menu':
      menu(bot, message, message.id)

   else:
      delete = telebot.types.ReplyKeyboardRemove()
      bot.send_message(message.chat.id, f'Вы написали: {message.text}\n', parse_mode='html', reply_markup=delete)
      TIME = (datetime.datetime.now(tz)).strftime('%H:%M:%S')
      DATE = (datetime.datetime.now(tz)).strftime('%d.%m')
      print(f'{TIME} {DATE} | Пользователь {message.from_user.username} {message.from_user.first_name} написал {message.text}')
      bot.delete_message(message.chat.id, message.message_id)

def mycallback(bot, callback):
   if callback.data == 'test':
      bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.id, text = f'Напиши количество слов')
      bot.register_next_step_handler(callback.message, crateMassive, callback.message.chat.id, callback.message.id)

   elif callback.data == 'next':
      if massiv != []:
         random_number = (random.randint(0, (len(massiv))-1))
         for k in massiv[random_number].keys():
            bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.id, text = f'{(len(massiv))}: Введи перевод слова {massiv[random_number][k]}: ')
            bot.register_next_step_handler(callback.message, checkWorld, k,massiv,random_number, callback.message.chat.id, callback.message.id)
      else:
         menu(bot, callback.message, callback.message.id)

   elif callback.data == 'dictionary':
      keyboard = InlineKeyboardMarkup()
      keyboard.add(InlineKeyboardButton('menu', callback_data = 'menu'))
      bot.delete_message(callback.message.chat.id, callback.message.message_id)
      massiv2 = []
      all_words = ''
      count = 0
      cursor.execute("SELECT * FROM words")
      massive_big = cursor.fetchall()
      for a in massive_big:
         kortej2 = dict([(a[0],a[1])])
         massiv2.append(kortej2)
      for k in massiv2:
         for key in k:
            count += 1
            all_words += (f'{count}. {k[key]}: {key}\n')
      if len(all_words) > 4096:
         for x in range(0, len(all_words), 4096):
            bot.send_message(callback.message.chat.id, all_words[x:x+4096],reply_markup = keyboard)
      else:
         bot.send_message(callback.message.chat.id, all_words,reply_markup = keyboard)

   elif callback.data == 'menu':
      menu(bot, callback.message, callback.message.id)

if __name__ == '__main__':
   TIME = (datetime.datetime.now(tz)).strftime('%H:%M:%S')
   DATE = (datetime.datetime.now(tz)).strftime('%d.%m')
   print ('Бот запущен:', TIME)
   while True:
      try:
         bot.infinity_polling(none_stop=True, timeout=123)
      except Exception as e:
         TIME = (datetime.datetime.now(tz)).strftime('%H:%M:%S')
         DATE = (datetime.datetime.now(tz)).strftime('%d.%m')
         print(e)
         tm.sleep(15)
         continue