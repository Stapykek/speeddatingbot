from gc import callbacks
from multiprocessing.resource_tracker import register
import sqlite3
from os.path import curdir

import telebot
from attr.validators import matches_re
from select import select
from telebot import TeleBot
from telebot.types import ChatFullInfo, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, \
    ReplyKeyboardRemove, Message, Update
from config import token


bot = TeleBot(token)


@bot.message_handler(commands=['start'])
def main(message):
    @bot.callback_query_handler(func=lambda call: call.data in ['adm','us'])
    def handle(call):
        bot.answer_callback_query(call.id, "")
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
        bot.answer_callback_query(call.id, "")
        if call.data == 'changename':
            bot.send_message(call.message.chat.id,"Введите новое имя", reply_markup=ReplyKeyboardRemove())
            bot.register_next_step_handler(call.message, changebytag, 'name')
            bot.register_next_step_handler(call.message, phone)
        elif call.data == 'leavename':
            name = call.message.chat.first_name
            lname = call.message.chat.last_name
            if lname != None:
                name += " " + lname
            sql = sqlite3.connect('forum.db')
            cur = sql.cursor()
            cur.execute(f"UPDATE participants Set name = '{name}' where tg = '{message.chat.username}'")
            sql.commit()
            cur.close()
            phone(message)

    def changebytag(message, row):
        sql = sqlite3.connect('forum.db')
        cur = sql.cursor()
        cur.execute(f"UPDATE participants Set {row} = '{message.text}' where tg = '{message.chat.username}'")
        sql.commit()
        cur.close()
        sql.close()

    sql = sqlite3.connect('forum.db')
    cur = sql.cursor()
    if (len(sql.execute(f"select * from participants where tg = '{message.chat.username}'").fetchall()) == 0):
        bot.send_message(message.chat.id, f"register {message.chat.username}")
        com = f"INSERT INTO participants (tg) VALUES ('{message.chat.username}');"
        cur.execute(com)
        sql.commit()
        bot.send_message(message.chat.id, "registered")

    cur = sql.execute(f"select * from participants where tg = '{message.chat.username}'")
    arr = cur.fetchall()[0]
    name = cur.execute(f"SELECT name from participants where tg='{message.chat.username}'").fetchone()
    if name == None:
        name = message.chat.first_name
        lname = message.chat.last_name
        if lname != None:
            name += " " + lname
    else:
        name = name[0]
    def Name(message):
        markup = InlineKeyboardMarkup()
        btn1 = InlineKeyboardButton("Изменить", callback_data='changename')
        btn2 = InlineKeyboardButton("Оставить", callback_data='leavename')
        markup.row(btn1,btn2)
        bot.send_message(message.chat.id, f"Ваше имя: {name}. Желаете изменить?", reply_markup=markup)

    def phone(message):
        if arr[7] == None:
            bot.send_message(message.chat.id, "Введите номер телефона")
            bot.register_next_step_handler(message, changebytag, 'phone')
            bot.register_next_step_handler(message, comp)
        else:
            comp(message)

    def comp(message):
        @bot.callback_query_handler(func=lambda call: call.data in ['incomp', 'nocomp'])
        def handler2(call):
            bot.answer_callback_query(call.id, "")
            if call.data == 'incomp':
                bot.send_message(call.message.chat.id, "Введите название компании", reply_markup=ReplyKeyboardRemove())
                bot.register_next_step_handler(call.message, changebytag, 'company')
                bot.register_next_step_handler(call.message, pos)
            elif call.data == 'nocomp':
                sql = sqlite3.connect('forum.db')
                cur = sql.cursor()
                cur.execute(f"UPDATE participants Set company = '-', pos = '-' where tg = '{message.chat.username}'")
                sql.commit()
                cur.close()
                sql.close()
                field(message)

        markup = InlineKeyboardMarkup()
        btn1 = InlineKeyboardButton("Да", callback_data='incomp')
        btn2 = InlineKeyboardButton("Нет", callback_data='nocomp')
        markup.row(btn1,btn2)
        if arr[3] == None:
            bot.send_message(message.chat.id, "Вы представляете компанию?", reply_markup = markup)
        elif arr[3] == '-':
            field(message)
        else:
            pos(message)

    def pos(message):
        @bot.callback_query_handler(func= lambda call: call.data in ['leavepos','nopos'])
        def handler4(call):
            bot.answer_callback_query(call.id, "")
            if call.data == 'leavepos':
                bot.send_message(call.message.chat.id, "Введите должность", reply_markup=ReplyKeyboardRemove())
                bot.register_next_step_handler(call.message, changebytag, 'pos')
                bot.register_next_step_handler(call.message, field)
            elif call.data == 'nopos':
                sql = sqlite3.connect('forum.db')
                cur = sql.cursor()
                cur.execute(f"UPDATE participants Set pos = '-' where tg = '{message.chat.username}'")
                sql.commit()
                cur.close()
                sql.close()
                field(message)

        markup = InlineKeyboardMarkup()
        btn1 = InlineKeyboardButton("Да", callback_data='leavepos')
        btn2 = InlineKeyboardButton("Нет", callback_data='nopos')
        markup.row(btn1,btn2)
        if arr[2] == None:
            bot.send_message(message.chat.id, "Вы желаете ввести должность?", reply_markup=markup)
        else:
            field(message)

    def field(message):
        if arr[4] == None:
            bot.send_message(message.chat.id, "Введите сферу деятельности", reply_markup=ReplyKeyboardRemove())
            bot.register_next_step_handler(message, changebytag, 'field')
            bot.register_next_step_handler(message, site)
        else:
            site(message)

    def site(message):
        @bot.callback_query_handler(func=lambda call: call.data in ['leavesite', 'nosite'])
        def handler7(call):
            bot.answer_callback_query(call.id, "")
            if call.data == 'leavesite':
                bot.send_message(call.message.chat.id, "Введите адрес веб-сайта", reply_markup=ReplyKeyboardRemove())
                bot.register_next_step_handler(call.message, changebytag, 'site')
                bot.register_next_step_handler(call.message, desc)

            elif call.data == 'nosite':
                sql = sqlite3.connect('forum.db')
                cur = sql.cursor()
                cur.execute(f"UPDATE participants Set site = '-' where tg = '{message.chat.username}'")
                sql.commit()
                cur.close()
                sql.close()
                desc(message)

        markup = InlineKeyboardMarkup()
        btn1 = InlineKeyboardButton("Да", callback_data='leavesite')
        btn2 = InlineKeyboardButton("Нет", callback_data='nosite')
        markup.row(btn1,btn2)

        if arr[6] == None:
            bot.send_message(message.chat.id, "Вы желаете оставить веб-сайт?", reply_markup=markup)
        else:
            desc(message)

    def desc(message):
        if arr[5] == None:
            bot.send_message(message.chat.id, "Оставьте описание о себе")
            bot.register_next_step_handler(message, changebytag, 'desc')
            bot.register_next_step_handler(message,book)
        else:
            book(message)

    def book(message):
        @bot.callback_query_handler(func= lambda call: call.data in['booktable','dontbook'])
        def handler(call):
            bot.answer_callback_query(call.id,"")
            if call.data == "booktable":
                bot.send_message(call.message.chat.id, "Введите дату, на которую вы хотите забронировать столик в формате: 'День бронирования' 'Время бронирования'.\nПример: 1 15:00")
                bot.register_next_step_handler(message,addbooking)
            if call.data == "dontbook":
                sql = sqlite3.connect('forum.db')
                cur = sql.cursor()
                meetswithus = int(sql.execute(f"SELECT COUNT(*) from meetings where creator = '{call.message.chat.username}'").fetchone()[0])
                cur.execute(f"Update participants Set booked = '{meetswithus}' where tg = '{call.message.chat.username}'")
                sql.commit()
                bookedcnt = cur.execute(f"SELECT (booked) from participants where tg = '{call.message.chat.username}'").fetchall()[0][0]
                if bookedcnt != None:
                    cur.close()
                    sql.close()
                    bookedcnt = int(bookedcnt)
                    if bookedcnt > 0:
                        premiumpanel(message)
                    else:
                        basicpanel(message)
                else:
                    cur.execute(f"UPDATE participants Set booked = 0 where tg='{message.chat.username}'")
                    sql.commit()
                    sql.close()
                    basicpanel(message)



        def addbooking(message):
            sql = sqlite3.connect('forum.db')
            cur = sql.cursor()
            cur = sql.execute(f"select * from participants where tg = '{message.chat.username}'")
            booked = list(map(str,message.text.split()))
            tables = int(cur.execute("SELECT COUNT(*) from tables").fetchone()[0])
            bookedatthattime = int(cur.execute(f"SELECT COUNT(*) from meetings where time = '{booked[1]}' and date = '{booked[0]}'").fetchone()[0])
            if bookedatthattime < tables:
                cur.execute(f"INSERT INTO meetings(creator,time,date) VALUES ('{message.chat.username}', '{booked[1]}', '{booked[0]}')")
                sql.commit()
                cur.close()
                sql.close()
                markup = InlineKeyboardMarkup()
                btn1 = InlineKeyboardButton("Да", callback_data='booktable')
                btn2 = InlineKeyboardButton("Нет", callback_data='dontbook')
                markup.row(btn1,btn2)
                bot.send_message(message.chat.id, "Вы хотите добавить ещё столик?", reply_markup=markup)
            else:
                bot.send_message(message.chat.id, "Все столики на это время уже забронированы. Выберите другой день/время.")
                bot.register_next_step_handler(message, addbooking)




        if arr[8] == None:
            markup = InlineKeyboardMarkup()
            yb = InlineKeyboardButton("Да", callback_data='booktable')
            nb = InlineKeyboardButton("Нет", callback_data='dontbook')
            markup.row(yb,nb)
            bot.send_message(message.chat.id, "Вы желаете забронировать столики?", reply_markup=markup)
        elif(arr[8]!=0):
            premiumpanel(message)
        else:
            basicpanel(message)
    Name(message)



def adminpanel(message):
    bot.send_message(message.chat.id, 'admin panel')

def basicpanel(message):
    markup = InlineKeyboardMarkup()
    btn2 = InlineKeyboardButton('Получить расписание встреч', callback_data='print')
    markup.add(btn2)
    sql = sqlite3.connect('forum.db')
    cur = sql.cursor()
    user_data = cur.execute(f"SELECT * from participants where tg = '{message.chat.username}'").fetchone()
    bot.send_message(message.chat.id, 'Здравствуйте, ' + user_data[1] + '. У Вас обычный доступ.', reply_markup=markup)
    pass


def premiumpanel(message):
    @bot.callback_query_handler(func=lambda call: call.data in ['browse', 'print'])
    def handle(call):
        if call.data == 'browse':
            sql = sqlite3.connect('forum.db')
            cur = sql.cursor()
            meetings = cur.execute(f"SELECT * from meetings where participant_ID IS NULL and creator != '{call.message.chat.username}'").fetchall()
            cur.close()
            sql.close()
            browsemeetings(call.message, call.message.chat.username,meetings)
        if call.data == 'print':
            printmeetings(call.message, call.message.chat.username)

    sql = sqlite3.connect('forum.db')
    cur = sql.cursor()
    user_data = cur.execute(f"SELECT * from participants where tg = '{message.chat.username}'").fetchone()
    markup = InlineKeyboardMarkup()
    btn1 = InlineKeyboardButton('Записаться на встречу', callback_data='browse')
    btn2 = InlineKeyboardButton('Получить расписание встреч', callback_data='print')
    markup.add(btn1)
    markup.add(btn2)
    sql = sqlite3.connect('forum.db')
    cur = sql.cursor()
    bot.send_message(message.chat.id, 'Здравствуйте, ' + user_data[1] + '. У Вас премиум доступ.',reply_markup=markup)

def arrangemeetings(uid):
    sql = sqlite3.connect('forum.db')
    cur = sql.cursor()

def browsemeetings(message,uid,meetings):
    sql = sqlite3.connect('forum.db')
    cur = sql.cursor()
    cur.close()
    def step(message,uid,mts):
        @bot.callback_query_handler(func=lambda call: call.data in ['want', 'dontwant', 'dontbrowsereq'])
        def handler(call):
            if call.data == 'want':
                makerequest(message,mts[0],uid)
                browsemeetings(message, uid, mts[1:])
            elif call.data == 'dontwant':
                browsemeetings(message,uid, mts[1:])
            elif call.data == 'dontbrowsereq':
                sql = sqlite3.connect('forum.db')
                bk = int(sql.execute(f"SELECT booked from participants where tg = '{uid}'").fetchone()[0])
                sql.close()
                if bk>0:
                    premiumpanel(message)
                else:
                    basicpanel(message)
        if len(meetings)>0:
            mt = meetings[0]
            sql = sqlite3.connect('forum.db')
            cur = sql.cursor()
            crid = cur.execute(f"Select creator from meetings where meeting_ID = '{mt[0]}'").fetchone()[0]
            crname = cur.execute(f"Select name from participants where tg = '{crid}'").fetchone()[0]
            markup = InlineKeyboardMarkup()
            btn1 = InlineKeyboardButton("Записаться", callback_data="want")
            btn2 = InlineKeyboardButton("Отказаться", callback_data="dontwant")
            btn3 = InlineKeyboardButton("Выйти в меню", callback_data="dontbrowsereq")
            markup.row(btn1,btn2)
            markup.row(btn3)
            bot.send_message(message.chat.id, "Доступна встреча в: " + mt[3] + ". В день форума: " + mt[4] + " На встрече будет: " + crname, reply_markup=markup)
        else:
            sql = sqlite3.connect('forum.db')
            bk = int(sql.execute(f"SELECT booked from participants where tg = '{uid}'").fetchone()[0])
            sql.close()
            if bk > 0:
                premiumpanel(message)
            else:
                basicpanel(message)
    #def тут
    step(message, uid, meetings)

def makerequest(message : Message,mt,uid: str):
    sql = sqlite3.connect('forum.db')
    cur = sql.cursor()
    requests = cur.execute(f"SELECT * from requests where participant_ID = '{uid}'").fetchall()
    for i in requests:
        if i[0] == mt[0]:
            bot.send_message(message.chat.id, "Вы уже записывались на эту встречу")
            return
    bot.send_message(message.chat.id, "Предварительная запись на встречу отправлена.")
    cur.execute(f"Update meetings set participant_ID = '{uid}' where meeting_ID = '{mt[0]}'")
    sql.commit()
    cur.close()
    sql.close()

def printmeetings(message,uid): # not DONE!
    msg = "Ваши встречи:\n"
    sql = sqlite3.connect('forum.db')
    cur = sql.cursor()
    arr = cur.execute('SELECT * from meetings').fetchall()
    for i in arr:
        if (i[1] == uid or i[2] == uid) and i[2] != None:
            if i[1] == uid:
                otherid = i[2]
            else:
                otherid = i[1]
            othername = cur.execute(f"Select name from participants where tg= '{otherid}'").fetchone()
            if othername == None:
                msg += "Встреча с: " + str(otherid) + ", в день форума: " + i[4] + ", в: " + i[3] + f"\n"
            else:
                msg += "Встреча с: " + othername[0] + ", в день форума: " + i[4] + ", в: " + i[3] + "\n"
    if msg == "Ваши встречи:\n": msg = "У вас ещё нет встреч"
    bot.send_message(message.chat.id, msg)
    sql = sqlite3.connect('forum.db')
    bk = int(sql.execute(f"SELECT booked from participants where tg = '{uid}'").fetchone()[0])
    sql.close()
    if bk > 0:
        premiumpanel(message)
    else:
        basicpanel(message)





bot.infinity_polling()

#register -> create user if don't exist -> check name, add if it's not present -> so on, so forth