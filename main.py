from gc import callbacks
from multiprocessing.resource_tracker import register
import sqlite3
import telebot
from telebot import TeleBot
from telebot.types import ChatFullInfo, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, \
    ReplyKeyboardRemove, Message, Update


bot = TeleBot('8120507635:AAFaU2FBLSxdgaAI5o4jJFhjKcJVvmUdgik')


@bot.message_handler(commands=['start'])
def main(message):
    @bot.callback_query_handler(func=lambda call: call.data in ['adm','us'])
    def handle(call):
        if call.data == 'adm':
            adminpanel(call.message)
        elif call.data == 'us':
            register(call.message)
    markup = InlineKeyboardMarkup()
    btn1 = InlineKeyboardButton("Организатор", callback_data='adm')
    btn2 = InlineKeyboardButton("Участник", callback_data='us')
    markup.add(btn1,btn2)
    bot.send_message(message.chat.id,"Приветствую вас в чат-боте для speed-dating на WestHorecForum!\nКакая у вас роль?", reply_markup=markup)

def register(message):
    @bot.callback_query_handler(func=lambda call: call.data in ['changename','leavename'])
    def handle(call):
        if call.data == 'changename':
            bot.delete_message(call.message.chat.id, call.message.id)
            bot.send_message(call.message.chat.id, "Введите новое имя", reply_markup=ReplyKeyboardRemove())
            bot.register_next_step_handler(call.message, changebytag,'name')
        elif call.data == 'leavename':
            bot.delete_message(call.message.chat.id, call.message.id)
            name = call.message.chat.first_name
            lname = call.message.chat.last_name
            if lname != None:
                name += " " + lname
            sql = sqlite3.connect('forum.db')
            cur = sql.cursor()
            cur.execute(f"UPDATE participants Set name = '{name}' where tg = '{id}'")
            sql.commit()
            cur.close()

    def changebytag(message, row):
        bot.delete_message(message.chat.id, message.id-1)
        sql = sqlite3.connect('forum.db')
        cur = sql.cursor()
        cur.execute(f"UPDATE participants Set {row} = '{message.text}' where tg = '{id}'")
        sql.commit()
        cur.close()
        sql.close()

    sql = sqlite3.connect('forum.db')
    cur = sql.cursor()
    id = message.chat.username
    name = message.chat.first_name
    lname = message.chat.last_name
    if lname != None:
        name += " " + lname

    if (len(sql.execute(f"select * from participants where tg = '{id}'").fetchall()) == 0):
        bot.send_message(message.chat.id, f"register {id}")
        com = f"INSERT INTO participants (tg) VALUES ('{id}');"
        cur.execute(com)
        sql.commit()
        bot.send_message(message.chat.id, "registered")
    cur = sql.execute(f"select * from participants where tg = '{id}'")
    arr = cur.fetchall()[0]

    def Name(message):
        markup = InlineKeyboardMarkup()
        btn1 = InlineKeyboardButton("Изменить", callback_data='changename')
        btn2 = InlineKeyboardButton("Оставить", callback_data='leavename')
        markup.row(btn1,btn2)
        if arr[1] == None:
            bot.send_message(message.chat.id, f"Ваше имя: {name}. Желаете изменить?", reply_markup=markup)
        else:
            phone(message)
    def phone(message):
        pass
    def comp(message):
        pass
    def field(message):
        pass
    def pos(message):
        pass
    def site(message):
        pass
    def offer(message):
        pass
    Name(message)
    # if not None in arr:
    #     if(booked == None):
    #         markup = InlineKeyboardMarkup()
    #         btn1 = InlineKeyboardButton("Да", callback_data='y1')
    #         btn2 = InlineKeyboardButton("Нет", callback_data='n1')
    #         markup.add(btn1)
    #         markup.add(btn2)
    #         bot.send_message(message.chat.id, "Вы хотите забронировать столики?",reply_markup=markup)
    #     else:
    #         booked = int(booked)
    #         if booked > 0:
    #             premiumpanel(message)
    #         else:
    #             basicpanel(message)


@bot.callback_query_handler(func=lambda call: call.data in ['y1', 'n1', 'bk1'])
def handle(call):
    def book(message):
        count = message.text
        if count.isdigit():
            id = message.chat.username
            sql = sqlite3.connect('forum.db')
            cur = sql.cursor()
            count = int(count)
            if count > 0:
                cur.execute(f"UPDATE participants Set booked = {count} where tg = '{id}'")
                sql.commit()
                cur.close()
                sql.close()
                premiumpanel(message)
            else:
                bot.send_message(message.chat.id, "Введите натуральное число!")
                bot.register_next_step_handler(message, book)
        else:
            bot.send_message(message.chat.id, "Введите натуральное число!")
            bot.register_next_step_handler(message,book)

    if call.data == 'y1':
        bot.delete_message(call.message.chat.id, call.message.id)
        markup = InlineKeyboardMarkup()
        btn = InlineKeyboardButton("Назад", callback_data="bk1")
        markup.add(btn)
        bot.send_message(call.message.chat.id, "Введите количество столиков", reply_markup=markup)
        bot.register_next_step_handler(call.message, book)
    elif call.data == 'n1':
        bot.delete_message(call.message.chat.id, call.message.id)
        basicpanel(call.message)
    elif call.data == 'bk1':
         register(call.message)
def adminpanel(message):
    bot.send_message(message.chat.id, 'admin panel')

def basicpanel(message):
    bot.send_message(message.chat.id, 'basic panel')
    pass

def premiumpanel(message):
    bot.send_message(message.chat.id, 'premium panel')
    pass




bot.infinity_polling()

#register -> create user if don't exist -> check name, add if it's not present -> so on, so forth