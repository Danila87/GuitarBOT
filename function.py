import re
import sqlite3
import telebot
from telebot import types
import time

token = "5371019683:AAGM6VbDWxOijJqyVLfPoox7JdlCxjsMNpU"
bot = telebot.TeleBot(token)
conn = sqlite3.connect('database.db', check_same_thread=False)
cursor = conn.cursor()
cotik = open('cotik.jpg', 'rb')


#Админ меню
def keyboard_admin(message):
    startKBoard = types.ReplyKeyboardMarkup(row_width = 1, resize_keyboard=True)
    btn2 = types.KeyboardButton(text = "Список песен")
    btn3 = types.KeyboardButton(text = "Оставить отзыв")
    btn4 = types.KeyboardButton(text = "Показать комментарии")
    btn5 = types.KeyboardButton(text = "Вывести запросы")
    btn6 = types.KeyboardButton(text = "Создать событие")
    btn7 = types.KeyboardButton(text = "Показать ближайшие события")
    btn1 = types.KeyboardButton(text = "Настройки")
    startKBoard.add(btn2, btn3, btn4, btn5, btn6, btn7, btn1)
    time.sleep(1)
    bot.send_message(message.chat.id, "Открываю главное меню", reply_markup=startKBoard)

#Пользовательское меню 
def keyboard_user(message):
    startKBoard = types.ReplyKeyboardMarkup(row_width = 1, resize_keyboard=True)
    btn2 = types.KeyboardButton(text = "Список песен")
    btn3 = types.KeyboardButton(text = "Оставить отзыв")
    btn4 = types.KeyboardButton(text = "Показать ближайшие события")
    btn1 = types.KeyboardButton(text = "Настройки")
    startKBoard.add(btn2, btn3, btn4, btn1)
    bot.send_message(message.chat.id, "Открываю меню", reply_markup=startKBoard)

#Да/Нет клавиатура
def keyboard_yes_no(message):
    keyboard = types.ReplyKeyboardMarkup(row_width = 1, resize_keyboard=True)
    btn1 = types.KeyboardButton(text = "Да")
    btn2 = types.KeyboardButton(text = "Нет")
    keyboard.add(btn1, btn2)
    return keyboard

#Подменю профиля
def keyboard_profile_submenu(message, text):
    rows = db_user_select_by_id(id_user = message.from_user.id)
    keyboard = types.ReplyKeyboardMarkup(row_width = 1, resize_keyboard = True)
    btn1 = types.KeyboardButton(text = "Показать мои данные")
    if rows[4] == 0:
        btn2 = types.KeyboardButton(text = "Подключить рассылку")
    else:
        btn2 = types.KeyboardButton(text = "Отключить рассылку")
    btn3 = types.KeyboardButton(text = "Назад")
    keyboard.add(btn1, btn2, btn3)
    bot.send_message(message.chat.id, text, reply_markup = keyboard)

#Внесение данных в таблицу с запросами
def db_requests_insert(id_user: int, requests: str, date: str):
	cursor.execute('INSERT INTO Requests (id_user, requests, date) VALUES (?, ?, ?)', (id_user, requests, date))
	conn.commit()

#Внесение данных о новом пользователе
def db_users_insert(id_user: int, first_name: str, last_name:str, nickname: str, event_status: int):
    cursor.execute('INSERT INTO Users (id_user, First_name, Last_name, Nickname, Event_status) VALUES (?,?,?,?,?)', (id_user, first_name, last_name, nickname, event_status))
    conn.commit()

#Проверка на регистрацию пользователя
def db_user_registration_select(id_user: int):
    cursor.execute('SELECT * FROM Users WHERE id_user = ?', (id_user,))
    rows = cursor.fetchall()
    row = len(rows)
    return row

#Изменение статуса рассылки у пользователя
def db_user_newsletter_edit(status: int, id_user: int):
    cursor.execute("UPDATE Users SET Event_status = ? WHERE id_user = ?", (status, id_user))
    conn.commit()

#Поиск песни
def db_song_select():
    cursor.execute('SELECT * FROM songs')
    rows = cursor.fetchall()
    return rows

#Вставка отзывов
def db_comment_insert(id_user:int, text_review: str, looked_status: int, date:str):
    cursor.execute('INSERT INTO Reviews (id_user, text_review, lookeed_status, date) VALUES (?, ?, ?, ?)', (id_user, text_review, looked_status, date))
    conn.commit()

#Поиск комментариев
def db_comment_select():
    cursor.execute('SELECT * FROM Reviews WHERE lookeed_status = 0 ')
    rows = cursor.fetchall()
    return rows

#Обновление комментариев
def db_comment_update(id_review: int):
    cursor.execute('UPDATE Reviews SET lookeed_status = 1 WHERE id_review = ?',(id_review,))
    conn.commit()

#Вывод количества запросов за всё время
def db_requests_count():
    cursor.execute('SELECT requests, COUNT (*) AS Count FROM Requests GROUP BY requests')
    rows = cursor.fetchall()
    return rows

#Вывод ошибки
def error(message):
    try:
        time.sleep(0.5)
        bot.send_photo(message.chat.id, cotik)
        time.sleep(0.5)
        keyboard = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton("Администратор", url='https://t.me/Danila877')
        keyboard.add(btn1)
        bot.send_message(message.chat.id, "Что-то пошло не так.\nО данной ошибке можете написать в комментариях или написать самому разработчику по ссылке ниже !)", reply_markup = keyboard)
    except:
        keyboard = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton("Администратор", url='https://t.me/Danila877')
        keyboard.add(btn1)
        bot.send_message(message.chat.id, "Возникла неожиданная ошибка.\nОбратитесь к администратору.", reply_markup = keyboard)
        bot.send_photo(message.chat.id, cotik)

#Вывод запросов по дате
def db_requests_select_date(date1:str):
    query = 'SELECT requests, COUNT (*) AS Count FROM Requests WHERE date LIKE ' + date1 + ' GROUP BY requests'
    cursor.execute(query)
    rows = cursor.fetchall()
    return rows

#Вывод запросов за выбранный период
def db_request_select_date_between(date11:str, date2:str):
    query = "SELECT requests, COUNT (*) AS Count FROM Requests WHERE date BETWEEN " + date11 + " AND " + date2 + " GROUP BY requests"
    cursor.execute(query)
    rows = cursor.fetchall()
    return rows

#Все типы событий
def db_types_events():
    cursor.execute("SELECT Name_event FROM Type_event")
    rows = cursor.fetchall()
    return rows

#Все айди чаты согласные на рассылку
def db_user_select():
    cursor.execute("SELECT id_user FROM Users WHERE Event_status = 1")
    rows = cursor.fetchall()
    return rows

#Конкретный человек по айди
def db_user_select_by_id(id_user:int):
    cursor.execute("SELECT * FROM Users WHERE id_user = ?", (id_user,))
    rows = cursor.fetchone()
    return rows

#Вставка события
def db_event_insert(dtype_event: int, ddate_event: str, dtext_event: str, ddate_event_techical: str):
    cursor.execute("INSERT INTO Events (Text_event, Date_event, Date_event_technical ,Event_type) VALUES (?, ?, ?, ?)", (dtext_event, ddate_event, ddate_event_techical ,dtype_event))
    conn.commit()
    
#Получение последнего события 
def db_event_select_last(type_event: str):
    cursor.execute("SELECT * FROM Events LEFT OUTER JOIN Type_event ON Events.Event_type = Type_event.Id_event WHERE Event_type = ? ORDER BY Id_event DESC LIMIT 1", (type_event,))
    rows = cursor.fetchone()
    return rows
