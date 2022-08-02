from ast import Lambda
from curses import keyname
from email import message
from email.message import Message
from glob import escape
from itertools import count
import telebot
import time
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from telebot import types
from datetime import datetime
from function import *
import datetime
from datetime import date

#Служебные данные для бота
token = "5371019683:AAGM6VbDWxOijJqyVLfPoox7JdlCxjsMNpU"
bot = telebot.TeleBot(token)

#Айди администора
admin_id = 798854480

#Текущие даты
now = datetime.datetime.now()
year = str(now.year)
month = str(now.month)
day = str(now.day)

#Словари
Month_test = {'Январь': '01', 'Февраль': '02', 'Март': '03', 'Апрель': '04', 'Май': '05', 'Июнь': '06', 'Июль': '07', 'Август': '08', 'Сентябрь': '09', 'Октябрь': '10', 'Ноябрь': '11', 'Декабрь': '12'}
Type_event = {'Орлятский круг': '1', 'Песенный зачёт' : '2', 'Спевка': '3', 'Квартирник': '4'}

#Старт программы
@bot.message_handler(commands = ['start'])
def start (message):

    id_user = message.from_user.id
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    nickname = message.from_user.username
    row = db_user_registration_select(id_user = id_user)

    if row == 1:
        bot.send_message(message.chat.id, 'Вы уже зарегистрированы. \nПопробуйте ввести другую команду')
    else:
        bot.send_message(message.chat.id, 'Добро пожаловать!')
        time.sleep(1)
        sent = bot.send_message(message.chat.id, "Согласны ли вы на рассылку новых событий, новостей и т.п.?", reply_markup=keyboard_yes_no(message))
        time.sleep(1)
        bot.register_next_step_handler(sent, user_registration_newsletter, id_user, first_name, last_name, nickname)

def user_registration_newsletter(message, id_user, first_name, last_name, nickname):
    if message.text == "Да":
        bot.send_message(message.chat.id, "Успешно!\nОтказаться от рассылки можно в меню в разделе 'Настройки'")
        db_users_insert(id_user = id_user, first_name = first_name, last_name = last_name, nickname = nickname, event_status = 1)
        time.sleep(1)
        keyboard_user(message)
    else:
        bot.send_message(message.chat.id, "Успешно!\nПодписаться на рассылку можно в меню в разделе 'Настройки'")
        db_users_insert(id_user = id_user, first_name = first_name, last_name = last_name, nickname = nickname, event_status = 0)
        time.sleep(1)
        keyboard_user(message)


#Админ меню
@bot.message_handler(func = lambda message: message.text == 'Админ меню')
def admin_menu(message):

    global admin_id
    bot.send_message(message.chat.id, "Проверяю данные...")
    time.sleep(1.5)

    if message.from_user.id == admin_id:
        keyboard_admin(message)
    else:
        bot.send_message(message.chat.id, "В доступе отказано.")
        error(message = message)


#Подменю
@bot.message_handler(func = lambda message: message.text == "Вывести запросы" or message.text == "Назад" or message.text == "Настройки")
def submenu(message):

    if message.text == "Вывести запросы":
        if message.from_user.id == admin_id:
            startKBoard = types.ReplyKeyboardMarkup(row_width = 1, resize_keyboard = True)
            btn1 = types.KeyboardButton(text = "За день")
            btn2 = types.KeyboardButton(text = "За месяц")
            btn3 = types.KeyboardButton(text = "За год")
            btn4 = types.KeyboardButton(text = "За всё время")
            btn5 = types.KeyboardButton(text = "Выбрать месяц")
            btn6 = types.KeyboardButton(text = "Отчёт за период")
            btn7 = types.KeyboardButton(text = "Назад")
            startKBoard.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7)
            bot.send_message(message.chat.id, "Выберите период", reply_markup = startKBoard)
        else:
            error(message = message)

    if message.text == "Назад":
        if message.from_user.id == admin_id:
            keyboard_admin(message)
        else:
            keyboard_user(message)

    if message.text == "Настройки":
        keyboard_profile_submenu(message, text = "Открываю")


#Вывод основного меню
@bot.message_handler(func=lambda message: message.text == 'Меню' or message.text == "меню")
def main_menu(message):

    keyboard_user(message)

@bot.message_handler(func=lambda message: message.text == "Подключить рассылку" or message.text == "Отключить рассылку")
def user_newsletter_edit(message):

    if message.text == "Подключить рассылку":
        db_user_newsletter_edit(id_user = message.from_user.id, status = 1)
        keyboard_profile_submenu(message, text = "Обновляю данные")
        time.sleep(1)
        bot.send_message(message.chat.id, "Рассылка подключена!")
    else:
        db_user_newsletter_edit(id_user = message.from_user.id, status = 0)
        keyboard_profile_submenu(message, text = "Обновляю данные")
        time.sleep(1)
        bot.send_message(message.chat.id, "Рассылка отключена!")


#Список песен
@bot.message_handler(func=lambda message: message.text == 'Список песен')
def list_song(message):

    chat_id = message.chat.id
    song_list = []
    for i in db_song_select():
        song_list.append(i[1]+'\n')
        song_list.sort()
    bot.send_message(chat_id,'Вот доступный список песен:')
    time.sleep(1.5)
    bot.send_message(chat_id,(''.join(song_list)))


#Оставить отзыв
@bot.message_handler(func=lambda message: message.text == 'Оставить отзыв')
def comment(message):

    chat_id = message.chat.id
    sent = bot.send_message(chat_id, 'Напишите следующим сообщением свой отзыв.')
    bot.register_next_step_handler(sent, comment_save)

def comment_save(message):

    chat_id = message.chat.id
    id_user = message.from_user.id
    user_text = message.text
    db_comment_insert(id_user = id_user, text_review = user_text, looked_status = 0, date = date.today())
    bot.send_message(chat_id, 'Спасибо за ваш отзыв!')


#Показать комментарии
@bot.message_handler(func = lambda message: message.text == 'Показать комментарии')
def comment_select(message):

    if message.from_user.id == admin_id:
        comment_list = []
        count = 0
        for i in db_comment_select():
            count = count + 1
            comment_list.append(str(count) + '. ' + i[2] + '\n' + 'Дата: ' + i[4] + '\n\n')
            db_comment_update(id_review=i[0])
        if len(comment_list) == 0:
            bot.send_message(message.chat.id, "Вы посмотрели все комментарии")
        else:
            bot.send_message(message.chat.id, (''.join(comment_list)))
    else:
        error(message = message)


#Поиск запросов по периодам
@bot.message_handler(func = lambda message: message.text == "За всё время" or message.text == "За день" or message.text == "За месяц" or message.text == "За год")
def requests_by_date(message):

    requests_list = []

    if message.from_user.id == admin_id:

        if message.text == "За всё время":
            row = len(db_requests_count())
            if row == 0:
                bot.send_message(message.chat.id, "За выбранный период нет данных.\nПопробуйте позже.")
            else:
                for i in db_requests_count():
                    requests_list.append(i[0] + ' : ' + str(i[1]) + '\n')
                    requests_list.sort()
                bot.send_message(message.chat.id, (''.join(requests_list)))

        if message.text == "За день":
            date1 = "'" + str(date.today()) + "'"
            row = len(db_requests_select_date(date1 = date1))
            if row == 0:
                bot.send_message(message.chat.id, "За выбранный период нет данных.\nПопробуйте позже.")
            else:
                for i in db_requests_select_date(date1=date1):
                    try:
                        requests_list.append(i[0] + ' : ' + str(i[1]) + '\n')
                        requests_list.sort()
                    except:
                        error(message=message)
                bot.send_message(message.chat.id, (''.join(requests_list)))

        if message.text == "За месяц":
            date1 = "'"+year+'-0'+month+'-%'+"'"
            row = len(db_requests_select_date(date1 = date1))
            if row == 0:
                bot.send_message(message.chat.id, "За выбранный период нет данных.\nПопробуйте позже.")
            else:
                for i in db_requests_select_date(date1=date1):
                    try:
                        requests_list.append(i[0] + ' : ' + str(i[1]) + '\n')
                        requests_list.sort()
                    except:
                        error(message=message)
                bot.send_message(message.chat.id, (''.join(requests_list)))

        if message.text == "За год":
            date1 = "'"+year+'-%-'+'%'+"'"
            row = len(db_requests_select_date(date1 = date1))
            if row == 0:
                bot.send_message(message.chat.id, "За выбранный период нет данных.\nПопробуйте позже.")
            else:
                for i in db_requests_select_date(date1=date1):
                    try:
                        requests_list.append(i[0] + ' : ' + str(i[1]) + '\n')
                        requests_list.sort()
                    except:
                        error(message = message)
                bot.send_message(message.chat.id, (''.join(requests_list)))
    else:
        error(message=message)


#Поиск запросов по конкретному месяцу
@bot.message_handler(func=lambda message: message.text == 'Выбрать месяц')
def requests_select_date(message):

    chat_id = message.chat.id
    sent = bot.send_message(chat_id, 'Введите месяц')
    bot.register_next_step_handler(sent, requests_select_date_test)

def requests_select_date_test(message):

    month = message.text
    requests_list = []
    date1 = "'"+year+'-'+Month_test[month]+'-%'+"'"
    row = len(db_requests_select_date(date1 = date1))
    if row == 0:
        bot.send_message(message.chat.id, "За выбранный период нет данных.\nПопробуйте позже.")
    else:
        for i in db_requests_select_date(date1=date1):
            try:
                requests_list.append(i[0] + ' : ' + str(i[1]) + '\n')
                requests_list.sort()
            except:
                error(message = message)
        bot.send_message(message.chat.id, (''.join(requests_list)))


#Отчёт по запросам за выбранный период
@bot.message_handler(func=lambda message : message.text == 'Отчёт за период')
def request_select_date_between(message):
    sent = bot.send_message(message.chat.id, "Введите начальную дату в формате '2022-01-01'")
    bot.register_next_step_handler(sent, date_between_start)

def date_between_start(message):
   sent = bot.send_message(message.chat.id, "Введите конечную дату в формате '2022-01-01'")
   date1 = message.text
   bot.register_next_step_handler(sent, date_between_end, date1)

def date_between_end(message, date1):
    date2 = message.text
    bot.send_message(message.chat.id, "Формирую отчёт...")
    time.sleep(1)
    date11 = "'" + date1 + "'"
    date2 = "'" + date2 + "'"
    requests_list = []
    if len(db_request_select_date_between(date11 = date11, date2 = date2)) == 0:
        bot.send_message(message.chat.id, "За выбранный период нет данных.\nПопробуйте позже.")
    else:
        try:
            for i in db_request_select_date_between(date11 = date11, date2 = date2):
                requests_list.append(i[0] + ' : ' + str(i[1]) + '\n')
                requests_list.sort()
            bot.send_message(message.chat.id, (''.join(requests_list)))
        except:
            error(message=message)


#Вставка события и его рассылка
@bot.message_handler(func=lambda message: message.text == "Создать событие")
def event_create(message):

    keyboard = types.ReplyKeyboardMarkup(row_width = 1, resize_keyboard=True)
    btn = []
    btn1 = types.KeyboardButton(text = "Назад")
    for i in db_types_events():
        btn = types.KeyboardButton(text=i[0])
        keyboard.add(btn)
    keyboard.add(btn1)
    sent = bot.send_message(message.chat.id, "Выберите тип события.", reply_markup = keyboard)
    bot.register_next_step_handler(sent, date_event)

def date_event(message):

    if message.text == "Назад":
        keyboard_admin(message)
    else:
        type_event = message.text
        sent = bot.send_message(message.chat.id, "Введите дату декоративную.\nНапример '6 апреля'")
        bot.register_next_step_handler(sent, date_event_technical, type_event)

def date_event_technical (message, type_event):

    date_event = message.text
    sent = bot.send_message(message.chat.id, "Введите техническую дату в формате '2022-01-01' после которой мероприятие будет не актуально.\n")
    bot.register_next_step_handler(sent, text_event, type_event, date_event)

def text_event(message, type_event, date_event):

    date_event_technical = message.text
    sent = bot.send_message(message.chat.id, "Введите текст события")
    bot.register_next_step_handler(sent, event_preview, type_event, date_event, date_event_technical)

def event_preview(message, type_event, date_event, date_event_technical):

    text_event = message.text
    bot.send_message(message.chat.id, "Предпросмотр события: ")
    time.sleep(1)
    bot.send_message(message.chat.id, "Тип события: " + type_event + '\nДата события: ' + date_event + '\nТекст события:\n' + text_event + '\nТехническая дата: ' + date_event_technical)
    time.sleep(1)
    sent = bot.send_message(message.chat.id, "Сохранить событие?", reply_markup=keyboard_yes_no(message))
    bot.register_next_step_handler(sent, save_event, type_event, date_event, text_event, date_event_technical)

def save_event(message, type_event, date_event, text_event, date_event_technical):

    if message.text == "Да":
        bot.send_message(message.chat.id, "Событие сохранено.")
        time.sleep(1)
        type_event = Type_event[type_event]
        db_event_insert(dtype_event = type_event, ddate_event = date_event, ddate_event_techical = date_event_technical,dtext_event = text_event)
        keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        btn1 = types.KeyboardButton(text = "Да")
        btn2 = types.KeyboardButton(text = "Нет")
        sent = bot.send_message(message.chat.id, "Разослать событие пользователям?", reply_markup=keyboard_yes_no(message))
        bot.register_next_step_handler(sent, event_newsletter, type_event)

    elif message.text == "Нет":
        keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        btn1 = types.KeyboardButton(text="Да")
        btn2 = types.KeyboardButton(text="Нет.\nВернуться в главное меню.")
        keyboard.add(btn1, btn2)
        sent = bot.send_message(message.chat.id, "Создать заново?", reply_markup=keyboard_yes_no(message))
        bot.register_next_step_handler(sent, event_hub)

def event_hub(message):

    if message.text == "Да":
        event_create(message)
    else:
        keyboard_admin(message)

def event_newsletter(message, type_event):

    if message.text == "Да":
        event = db_event_select_last(type_event = type_event)
        for i in db_user_select():
            bot.send_message(i[0], "Опубликовано новое событие от гитаристов.")
            time.sleep(1)
            bot.send_message(i[0], event[2] + " состоится " + event[6].lower() + " !\n" + event[1])
        keyboard_admin(message)

    elif message.text == "Нет":
        keyboard_admin(message)


#Вывод ближайших событий
@bot.message_handler(func = lambda message: message.text == "Показать ближайшие события")
def test(message):

    iteration = 0
    for i in db_types_events():
        iteration = iteration + 1
        try:
            event = db_event_select_last(type_event = iteration)
            bot.send_message(message.chat.id, event[2] + " состоится " + event[6].lower() + " !\n" + event[1])
            time.sleep(0.5)
        except:
            print(123)


#Вывод песни
@bot.message_handler(func = lambda m: True)
def select_song(message):

    if message.text == '/start':
        bot.send_message(message.chat.id, 'Введите название песни а не команду.')
    else:
        chat_id = message.chat.id
        text_reply = message.text
        text_reply = text_reply.lower().replace(" ", "")
        row = False
        for i in db_song_select():
            a = fuzz.WRatio(i[2], text_reply)
            if a>75:
                bot.send_message(chat_id, 'Ищу песню: ' + i[1])
                time.sleep(1.5)
                bot.send_message(chat_id, i[3])
                try:
                    audio = open(r'song'+i[4], 'rb')
                    bot.send_audio(chat_id, audio)
                except:
                    pass
                row = True
                db_requests_insert(id_user=message.from_user.id, requests=i[1], date = date.today())
                break
        if row == False:
            time.sleep(1.5)
            bot.send_message(chat_id, 'К сожалению я не нашёл такую песню.\nПопробуйте другую.')


bot.polling(non_stop = True)
