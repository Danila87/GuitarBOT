from bs4 import BeautifulSoup
from ast import Lambda
from email import message
from email.message import Message
from glob import escape
from itertools import count
from types import NoneType
from unicodedata import name
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from telebot import types
from datetime import datetime
from function import *
from datetime import date

import requests
import random
import os
import speech_recognition as sr
import sqlite3
import telebot
import time
import datetime
import re
import yadisk
import threading


"""
    ТЕХНИЧЕСКИЕ ПЕРЕМЕННЫЕ

    Variable:
        TOKEN : Токен бота. В данной версии токен зашит в переменную среды сервера (Heroku)
        YANDEX_TOKEN : Токен от Я.Диск. Нужен для работы с API Я.Диск
        ydisk : Переменная для работы с Я.Диск
        bot : Переменная для работы с библиотекой telebot
        conn : Переменная с соединением с базой данных
        cotik : Я хз почему не сделал через with ... as но это просто фотка котика
        logfile_mat : путь к лог файлу с матами
"""

#TOKEN = os.environ["BOT_TOKEN"]
TOKEN = '5371019683:AAGM6VbDWxOijJqyVLfPoox7JdlCxjsMNpU'
YANDEX_TOKEN = 'y0_AgAAAAAO_DuQAAhmIAAAAADOUpN38O9Jqe8fTx275pqgdwJIP-pbvR8'
ydisk = yadisk.YaDisk(token=YANDEX_TOKEN)
bot = telebot.TeleBot(TOKEN, skip_pending=True)
conn = sqlite3.connect('database//database.db', check_same_thread=False)
cotik = open('img//cotik.jpg', 'rb')
logfile_mat = 'log_files//' + str(datetime.date.today()) + '_mat.log'


# РАЗЛИЧНЫЕ МЕНЮ ПОЛЬЗОВАТЕЛЕЙ


def get_main_menu(message):
    rows = db_select_user_by_id(id_user=message.from_user.id)
    
    keyboard = types.ReplyKeyboardMarkup(row_width = 3, resize_keyboard=True)
    btn_song_list = types.KeyboardButton(text="Список песен 📔")
    btn_reviews = types.KeyboardButton(text="Отзывы 💬")
    btn_events = types.KeyboardButton(text="События 📅")
    btn_resend_message = types.KeyboardButton(text="Переслать сообщение ✉️")
    btn_requests = types.KeyboardButton(text="Вывести запросы 📈")
    btn_settings = types.KeyboardButton(text="Настройки ⚙️")

    if rows[6] in (1,2):
        keyboard.add(btn_song_list, btn_reviews, btn_events, btn_resend_message, btn_requests, btn_settings)
        bot.send_message(message.chat.id, "Открываю меню", reply_markup=keyboard)
    else:
        keyboard.add(btn_song_list, btn_reviews, btn_events, btn_settings)
        bot.send_message(message.chat.id, "Открываю меню", reply_markup=keyboard)


def get_keyboard_yes_no():

    """
    Вызов меню Да/нет

    Returns:
        keyboard: возвращает keyboard, которая должна вставать в send_message
    """

    keyboard = types.ReplyKeyboardMarkup(row_width = 1, resize_keyboard=True)
    btn_yes = types.KeyboardButton(text="Да")
    btn_no = types.KeyboardButton(text="Нет")
    keyboard.add(btn_yes, btn_no)
    return keyboard


def get_keyboard_setting_submenu(message):

    """
    Вызов меню настроек

    Args:
        message : объект message от telebot
    """

    rows = db_select_user_by_id(id_user = message.from_user.id)
    keyboard = types.ReplyKeyboardMarkup(row_width = 2, resize_keyboard = True)
    btn_show_data = types.KeyboardButton(text="Показать мои данные 👤")
    btn_song_books = types.KeyboardButton(text="Песенники 📔")
    btn_help = types.KeyboardButton(text="Помощь ❓")
    btn_ban_list = types.KeyboardButton(text="Бан лист")
    btn_admin = types.KeyboardButton(text="Администраторы 💼")
    btn_back = types.KeyboardButton(text="Назад")

    if rows[4] == 0 and rows != NoneType:
        btn_newsletter = types.KeyboardButton(text="Подключить рассылку 🔔")
    else:
        btn_newsletter = types.KeyboardButton(text="Отключить рассылку 🔕")

    if rows[6] == 1:
        keyboard.add(btn_show_data, btn_newsletter, btn_admin, btn_song_books, btn_help, btn_ban_list, btn_back)
        bot.send_message(message.chat.id, 'Обновляю данные', reply_markup = keyboard)
    else:
        keyboard.add(btn_show_data, btn_newsletter, btn_song_books, btn_help, btn_back)
        bot.send_message(message.chat.id, 'Обновляю данные', reply_markup = keyboard)


def get_keyboard_event_submenu(message):

    """
    Вызов меню событий

    Args:
        message : объект message от telebot
    """

    rows = db_select_user_by_id(id_user = message.from_user.id)    
    keyboard = types.ReplyKeyboardMarkup(row_width = 2, resize_keyboard=True)
    btn_event_all = types.KeyboardButton(text="Показать ближайшие события")
    btn_back = types.KeyboardButton(text="Назад")
    btn_create_event = types.KeyboardButton(text="Создать событие")

    if rows[6] in (1,2):
        keyboard.add(btn_event_all, btn_create_event, btn_back)
        bot.send_message(message.chat.id, "Открываю", reply_markup = keyboard)
    else:
        keyboard.add(btn_event_all, btn_back)
        bot.send_message(message.chat.id, "Открываю", reply_markup = keyboard)


def get_keyboard_review_submenu(message):

    """
    Вызов меню отзывов

    Args:
        message : объект message от telebot
    """

    rows = db_select_user_by_id(id_user = message.from_user.id)
    btn_pull_rewievs = types.KeyboardButton(text="Оставить отзыв 💬")
    btn_rewievs_all = types.KeyboardButton(text="Показать отзывы")
    btn_back = types.KeyboardButton(text="Назад")

    if rows[6] in (1,2):
        keyboard = types.ReplyKeyboardMarkup(row_width = 2, resize_keyboard = True)
        keyboard.add(btn_rewievs_all, btn_pull_rewievs, btn_back)
        bot.send_message(message.chat.id, "Открываю", reply_markup = keyboard)
    else:
        keyboard = types.ReplyKeyboardMarkup(row_width = 1, resize_keyboard = True)
        keyboard.add(btn_pull_rewievs, btn_back)
        bot.send_message(message.chat.id, "Открываю", reply_markup = keyboard)

def get_keyboard_admin_edit_submenu(message):

    """
    Вызов меню администраторов

    Args:
        message : объект message от telebot
    """

    rows = db_select_user_by_id(id_user = message.from_user.id)

    if rows[6] == 1:
        keyboard = types.ReplyKeyboardMarkup(row_width = 2, resize_keyboard = True)
        btn_back = types.KeyboardButton(text="Назад")
        btn_set_admin = types.KeyboardButton(text="Назначить администратором")
        btn_delete_admin = types.KeyboardButton(text="Убрать администратора")
        btn_admin_all = types.KeyboardButton(text="Показать всех администраторов")
        keyboard.add(btn_set_admin, btn_delete_admin, btn_admin_all, btn_back)
        bot.send_message(message.chat.id, "Открываю", reply_markup = keyboard)
    else:
        error(message=message)


def get_administrator_call(message, chat_id):

    """
    Вызов кнопки-ссылки на администратора

    Args:
        message : объект message от telebot
    """

    keyboard = types.InlineKeyboardMarkup()
    btn_admin = types.InlineKeyboardButton("Администратор", url='https://t.me/Danila877')
    keyboard.add(btn_admin)
    bot.send_message(chat_id, "👇", reply_markup = keyboard)


# ФУНКЦИИ РАБОТЫ С ПОЛЬЗОВАТЕЛЯМИ


def db_select_users_all():

    """
    SQL запрос для получения списка всех пользователей

    Returns:
        rows: Список кортежей с данными
    """

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Users LEFT OUTER JOIN Role ON Users.Id_role = Role.Id_role")
    rows = cursor.fetchall()
    return rows


def db_select_user_by_newsletter():

    """
    SQL запрос для получения пользователей, согласных на рассылку

    Returns:
        rows: Список кортежей с данными
    """

    cursor = conn.cursor()
    cursor.execute("SELECT id_user FROM Users WHERE Event_status = 1")
    rows = cursor.fetchall()
    return rows


def db_select_user_by_id(id_user:int):

    """
    SQL запрос для получения конкретного пользователя

    Args:
        id_user (int): Id пользователя, которого надо получить

    Returns:
        rows: Список кортежей с данными
    """

    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM Users LEFT OUTER JOIN Role ON Users.Id_role = Role.Id_role WHERE id_user = ?", (id_user,))
        rows = cursor.fetchone()
        return rows
    except:
        pass


def db_insert_user(id_user:int, first_name:str=None, last_name:str=None, nickname:str=None, event_status:int=0):

    """
    SQL запрос для внесения данных о пользователе

    Args:
        id_user (int): id пользователя
        first_name (str): Имя
        last_name (str): Фамилия
        nickname (str): Никнейм
        event_status (int): Статус подписки (1-Да, 2-Нет)
    """

    try:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO Users (id_user, First_name, Last_name, Nickname, Event_status, Id_role) VALUES (?,?,?,?,?,3)', (id_user, first_name, last_name, nickname, event_status))
        conn.commit()
    except:
        pass


def db_select_user_registration(id_user:int):

    """
    SQL запрос для проверки пользователя на регистрацию

    Args:
        id_user (int): id пользователя которого нужно проверить

    Returns:
        rows: возвращает длину результата (кол-во найденных записей)
    """

    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Users WHERE id_user = ?', (id_user,))
    rows = cursor.fetchall()
    row = len(rows)
    return row


def db_update_user_newsletter(status: int, id_user: int):

    """
    SQL запрос для изменения статуса рассылки у пользователя

    Args:
        status (int): Статус подписки. 1 - Подключено, 2 - Отключено
        id_user (int): Id Пользователя
    """

    cursor = conn.cursor()
    cursor.execute("UPDATE Users SET Event_status = ? WHERE id_user = ?", (status, id_user))
    conn.commit()


def db_update_user(id_user:int, status:int):

    """
    SQL запрос для повышения/понижения прав администратора

    Args:
        id_user (int): Id Пользователя
        status (int): Статус(роль) пользователя. 1 - Суперпользователь, 2 - Администратор, 3 - Обычный пользователь
    """

    cursor = conn.cursor()
    cursor.execute("UPDATE Users SET Id_role = ? WHERE id_user = ?", (status, id_user))
    conn.commit()


def db_select_all_admin():

    """
    SQL запрос для получения всех администраторов

    Returns:
        rows: Возвращает список кортежей (все данных всех админов)
    """

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Users LEFT OUTER JOIN Role ON Users.Id_role = Role.Id_role WHERE Users.Id_role = 2")
    rows = cursor.fetchall()
    return rows
    

# ВСЕ ФУНКЦИИ РАБОТЫ С ОТЗЫВАМИ


def db_insert_review(id_user:int, text_review:str, looked_status:int, date:str):

    """
    SQL запрос для вставки отзыва от пользователя

    Args:
        id_user (int): Id пользователя
        text_review (str): Текст отзыва
        looked_status (int): Статус (Просмотрено/ не просмотрено)
        date (str): Дата
    """

    try:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO Reviews (id_user, text_review, lookeed_status, date) VALUES (?, ?, ?, ?)', (id_user, text_review, looked_status, date))
        conn.commit()
    except:
        pass


def db_select_reviews():

    """
    SQL запрос для получения всех отзывов

    Returns:
        rows: Возвращает список кортежей
    """

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Reviews LEFT OUTER JOIN Users ON Reviews.id_user = Users.id_user WHERE date > date('now', '-7 days')")
    rows = cursor.fetchall()
    return rows


def db_update_review(id_review:int):

    """
    SQL запрос для обновления статуса отзыва

    Args:
        id_review (int): Id отзыва для обновления
    """

    cursor = conn.cursor()
    cursor.execute('UPDATE Reviews SET lookeed_status = 1 WHERE id_review = ?',(id_review,))
    conn.commit()


# ВСЕ ФУНКЦИИ РАБОТЫ С ЗАПРОСАМИ


def db_requests_count():

    """
    SQL запрос для вывода запросов за всё время

    Returns:
        rows: Возвращает список запросов  
    """

    cursor = conn.cursor()
    cursor.execute('SELECT requests, COUNT (*) AS Count FROM Requests GROUP BY requests ORDER BY Count DESC')
    rows = cursor.fetchall()
    return rows


def db_insert_request(id_user:int, requests:str, date:str):

    """
    SQL запрос для внесения запросов

    Args:
        id_user (int): Id пользователя
        requests (str): Текст запроса
        date (str): Дата запроса
    """

    try:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO Requests (id_user, requests, date) VALUES (?, ?, ?)', (id_user, requests, date))
        conn.commit()
    except:
        pass


def db_select_requests_by_date(selected_date:str):

    """
    SQL запрос дла получения запросов за определённую дату

    Args:
        selected_date (str): Дата по которой нужно получить запросы. Можно в качестве аргумента передавать год, год-месяц, год-месяц-день.
                            Например "2022-01-% получит записи за весь январь 2022 года"

    Returns:
        rows: Возвращает список кортежей (список запросов)
    """

    cursor = conn.cursor()
    query = 'SELECT requests, COUNT (*) AS Count FROM Requests WHERE date LIKE ' + selected_date + ' GROUP BY requests ORDER BY Count DESC'
    cursor.execute(query)
    rows = cursor.fetchall()
    return rows


def db_select_requests_period(start_date:str, final_date:str):

    """
    SQL запрос для получения запросов за определённый период

    Args:
        start_date (str): Начальная дата
        final_date (str): Конечная дата

    Returns:
        rows: Возвращает список кортежей (список запросов)
    """

    cursor = conn.cursor()
    query = "SELECT requests, COUNT (*) AS Count FROM Requests WHERE date BETWEEN " + start_date + " AND " + final_date + " GROUP BY requests ORDER BY Count DESC"
    cursor.execute(query)
    rows = cursor.fetchall()
    return rows


# ВСЕ ФУНКЦИИ РАБОТЫ С СОБЫТИЯМИ


def db_select_event_types():

    """
    SQL запрос для получения всех типов событий

    Returns:
        rows: Список кортежей (типы событий)
    """

    cursor = conn.cursor()
    cursor.execute("SELECT Name_event FROM Type_event")
    rows = cursor.fetchall()
    return rows


def db_insert_event(dtype_event:int, ddate_event:str, dtext_event:str, ddate_event_techical:str):

    """
    SQL запрос для вставки нового события

    P.S. Здесь используется декоративная дата и техническая. Декоративная дата для красивого отображения и записывается например так "6 апреля", в то же время
    техническая дата нужна для проверки актуальности события и записывается например так "2022-11-01"

    Args:
        dtype_event (int): Тип события
        ddate_event (str): Дата события (декоративная)
        dtext_event (str): Текст события
        ddate_event_techical (str): Техническая дата
    """

    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Events (Text_event, Date_event, Date_event_technical ,Event_type) VALUES (?, ?, ?, ?)", (dtext_event, ddate_event, ddate_event_techical ,dtype_event))
        conn.commit()
    except:
        pass


def db_select_latest_event(type_event: str):

    """
    SQL запрос для получения актуального события

    Args:
        type_event (str): Тип события, которое нужно найти

    Returns:
        rows: Возвращает список кортежей (данные о событии)
    """

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Events LEFT OUTER JOIN Type_event ON Events.Event_type = Type_event.Id_event WHERE Event_type = ? AND Date_event_technical > date('now') ORDER BY Id_event DESC LIMIT 1", (type_event,))
    rows = cursor.fetchone()
    return rows


# ВСЕ ФУНКЦИИ РАБОТЫ С ПЕСНЯМИ


def db_select_song_all():

    """
    SQL запрос для получения всех песен

    Returns:
        rows: Возвращает список кортежей
    """

    cursor = conn.cursor()
    try:
        cursor.execute('SELECT * FROM songs')
        rows = cursor.fetchall()
        return rows
    except:
        pass



def db_select_song(title_song:str):

    """
    SQL запрос для получения песни по её заголовку

    Args:
        title_song (str): Заголовок песни, которую нужно найти

    Returns:
        rows: Возвращает список коретежей (данные о песне)
    """

    cursor = conn.cursor()
    cursor.execute('SELECT * FROM songs WHERE Title_song = ?',(title_song,))
    rows = cursor.fetchone()
    return rows


def db_select_song_by_type(type_song:str):

    """
    SQL запрос для получения песен определённой категории

    Args:
        type_song (str): Категория, по которой нужно отобрать песни

    Returns:
        rows: Возвращает список кортежей 
    """

    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Songs LEFT OUTER JOIN Type_song ON Songs.Type_song = Type_song.id_type WHERE Type_song.Type_song = ?', (type_song,))
    rows = cursor.fetchall()
    return rows


def db_select_song_type():

    """
    SQL запрос для получения всех категорий песен

    Returns:
        rows: Возвращает список кортежей (категории песен)
    """

    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Type_song ')
    rows = cursor.fetchall()
    return rows


def song_search(message, title_song:str = 'None'):

    """
    Отбор всех подходящих песен по заголовку пользователя

    Args:
        message : объект message от telebot
        title_song (str): Название песни, по которой идёт отбор
    """

    keyboard = types.InlineKeyboardMarkup()
    key = False

    for i in db_select_song_all():
        a = fuzz.WRatio(i[2], title_song)
        if a>75:
            bot.send_message(message.chat.id, 'Вы ввели: ' + title_song)
            key = True
            break

    if key == False:
        time.sleep(1)
        bot.send_message(message.chat.id, 'К сожалению я не разобрал ваш запрос.\nПопробуйте ещё раз.')

    if key:
        for i in db_select_song_all():
                a = fuzz.WRatio(i[2], title_song)
                if a>75:
                    btn = types.InlineKeyboardButton(i[1], callback_data=i[1])
                    keyboard.add(btn)
        time.sleep(1)
        bot.send_message(message.chat.id, "Вот что я нашёл:", reply_markup = keyboard)


# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ


def error(message):

    """
    Вывод ошибки. Выводит картинку и ссылку на Администратора

    Args:
        message : объект message от telebot
    """

    try:
        time.sleep(0.5)
        bot.send_photo(message.chat.id, cotik)
        time.sleep(0.5)
        bot.send_message(message.chat.id, "Что-то пошло не так.\nО данной ошибке можете написать в отзывах или написать самому разработчику по ссылке ниже !)")
        get_administrator_call(message, message.chat.id)
    except:
        bot.send_message(message.chat.id, "Возникла неожиданная ошибка.\nОбратитесь к администратору.")
        get_administrator_call(message, message.chat.id)
        bot.send_photo(message.chat.id, cotik)


def db_select_songbook_all():

    """
    SQL запрос для получения списка всех песенников

    Returns:
        rows: Возвращает список кортежей
    """

    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Song_book")
    rows = cursor.fetchall()
    return rows


def db_select_songbook_by_title(message, song_book_title:str = "Песенник ИОСПО"):

    """
    SQL запрос для получения песенника по заголовку. Отправляет файл с песенником

    Args:
        message : объект message от telebot
        song_book_title (str): Заголовок песенника. По дефолту стоит песенник ИО СПО
    """

    cursor = conn.cursor()
    cursor.execute("SELECT file_path FROM Song_book WHERE title_book = ?", (song_book_title,))
    rows = cursor.fetchone()
    file = open (rows[0], 'rb')
    bot.send_message(message.chat.id, "Загружаю...")
    bot.send_document(message.chat.id, file)


def get_img_from_Masha(message):

    """
    Функция для получения фотографии Тимоти Шаламе или Джонни Деппа для Маши. Сделал чисто по приколу

    Args:
        message : объект message от telebot

    Returns:
        img_url: Вовзращает ссылку откуда скачивать фото
    """

    bot.send_message(message.chat.id, 'Формирую списки\n[////                ]')
    time.sleep(1.5)
    

    image_shalame_list = []
    image_depp_list = []
    line_list = []

    used_links = open("files/used_links.txt", "a")
    used_links2 = open("files/used_links.txt", "r").read().split('\n')

    urlsite = 'https://www.theplace.ru'
    count = 0


    # Заполнение списка ссылками из файла
    for line in used_links2:
        line_list.append(line)

    bot.edit_message_text ('Собираю фотографии\n[//////              ]', chat_id=message.chat.id, message_id=message.message_id + 1)
    time.sleep(1)


    # Шаламе
    def shalame_get_link():
        
        for p in range(1,3):

            url = 'https://www.theplace.ru/photos/timothee_chalamet/?page='+str(p)
            r = requests.get(url)
            soup = BeautifulSoup(r.text, 'lxml')
            images = soup.findAll('div', class_='p-1')

            for image in images:
                link = image.find('a').get('href')
                r2 = requests.get(urlsite + link)
                soup2 = BeautifulSoup(r2.text, 'lxml')
                link2 = soup2.find('img', class_ = 'pic big_pic').get('src')
                image_shalame_list.append(urlsite + link2)


    # Джонни
    def jonny_get_link():

        for p in range(1,3):

            url = 'https://www.theplace.ru/photos/johnny_depp/?page='+str(p)
            r = requests.get(url)
            soup = BeautifulSoup(r.text, 'lxml')
            images = soup.findAll('div', class_='col-6 col-sm-6 col-md-6 col-lg-4 col-xl-3 pb-3')
            for image in images:
                link = image.find('a', class_='photos-pic-card__link').get('href')
                r2 = requests.get(urlsite+link)
                soup2 = BeautifulSoup(r2.text, 'lxml')
                link2 = soup2.find('img', class_='pic big_pic').get('src')
                image_depp_list.append(urlsite+link2)

    
    t1 = threading.Thread(target = shalame_get_link)
    t2 = threading.Thread(target = jonny_get_link)

    #Запуск потоков
    t1.start()
    t2.start()

    #Ждём пока выполнятся потоки
    t1.join()
    t2.join()

    bot.edit_message_text ('Выбираю фотографию\n[////////////////    ]', chat_id=message.chat.id, message_id=message.message_id + 1)
    image_list = image_depp_list + image_shalame_list        
    image_list = list(set(image_list) - set(line_list))

    if len(image_list):
        time.sleep(1.5)
        bot.edit_message_text ('Загружаю фотографию\n[//////////////////  ]', chat_id = message.chat.id, message_id=message.message_id + 1)
        time.sleep(1.5)
        random.shuffle(image_list)
        img_url = random.choice(image_list)
        used_links.write(img_url + '\n')
        bot.edit_message_text ('Загружено\n[////////////////////]', chat_id = message.chat.id, message_id=message.message_id + 1)
        return img_url
    else:
        bot.send_message(message.chat.id, 'Фотографии закончились. ')


def audio_to_text(dest_name: str, message):

    """
    Перевод аудио в текст

    Args:
        dest_name (str): Пусть до файла
        message : объект message от telebot

    Returns:
        result: Возвращает текст из аудиосообщения
    """

    try:
    # Функция для перевода аудио , в формате ".vaw" в текст
        r = sr.Recognizer() # такое вообще надо комментить?
        # тут мы читаем наш .vaw файл
        message = sr.AudioFile(dest_name)
        with message as source:
            audio = r.record(source)
        result = r.recognize_google(audio, language="ru_RU") # здесь можно изменять язык распознавания
        return result
    except:
        bot.send_message(message.chat.id, 'Возникла ошибка.\nПопробуйте ещё раз.')

# TODO Подумать над более продуманным фильтром
def mat_check(message, type_event:str = 'None'):

    """
    Проверка сообщения на мат

    Args:
        message : объект message от telebot
        type_event (str): Тип события, который записывает функция в логи (Создание события, написание запроса и т.д.)

    Returns:
        True: Возвращает True в случае если в сообщении есть мат. В других случаях ничего не возвращает
    """

    if message.content_type == 'text':
        row = db_select_user_by_id(id_user=message.from_user.id)
        words = message.text.split(' ')
        for i in words:
            text = i.lower()
            result = re.match(r'\b((у|[нз]а|(хитро|не)?вз?[ыьъ]|с[ьъ]|(и|ра)[зс]ъ?|(о[тб]|под)[ьъ]?|(.\B)+?[оаеи])?-?([её]б(?!о[рй])|и[пб][ае][тц]).*?|(н[иеа]|([дп]|верт)о|ра[зс]|з?а|с(ме)?|о(т|дно)?|апч)?-?ху([яйиеёю]|ли(?!ган)).*?|(в[зы]|(три|два|четыре)жды|(н|сук)а)?-?бл(я(?!(х|ш[кн]|мб)[ауеыио]).*?|[еэ][дт]ь?)|(ра[сз]|[зн]а|[со]|вы?|п(ере|р[оие]|од)|и[зс]ъ?|[ао]т)?п[иеё]зд.*?|(за)?п[ие]д[аое]?р([оа]м|(ас)?(ну.*?|и(ли)?[нщктл]ь?)?|(о(ч[еи])?|ас)?к(ой)|юг)[ауеы]?|манд([ауеыи](л(и[сзщ])?[ауеиы])?|ой|[ао]вошь?(е?к[ауе])?|юк(ов|[ауи])?)|муд([яаио].*?|е?н([ьюия]|ей))|мля([тд]ь)?|лять|([нз]а|по)х|м[ао]л[ао]фь([яию]|[еёо]й))\b', text)
            #result = re.match(r'(\s+|^)[пПnрРp]?[3ЗзВBвПnпрРpPАaAаОoO0о]?[сСcCиИuUОoO0оАaAаыЫуУyтТT]?[Ппn][иИuUeEеЕ][зЗ3][ДдDd]\w*[\?\,\.\;\-]*|(\s+|^)[рРpPпПn]?[рРpPоОoO0аАaAзЗ3]?[оОoO0иИuUаАaAcCсСзЗ3тТTуУy]?[XxХх][уУy][йЙеЕeEeяЯ9юЮ]\w*[\?\,\.\;\-]*|(\s+|^)[бпПnБ6][лЛ][яЯ9]([дтДТDT]\w*)?[\?\,\.\;\-]*|(\s+|^)(([зЗоОoO03]?[аАaAтТT]?[ъЪ]?)|(\w+[оОOo0еЕeE]))?[еЕeEиИuUёЁ][бБ6пП]([аАaAиИuUуУy]\w*)?[\?\,\.\;\-]*', i)
            if result != None:
                with open(logfile_mat, 'a', encoding='utf-8') as logm:
                    logm.write(str(datetime.datetime.today().strftime("%H:%M:%S")) + ': Пользователь ' + str(row[1]) + ' ' + str(row[2]) + ' ' + ' написал "' + i + '" при ' + type_event + '.\n')
                try:
                    ydisk.upload("log_files/"+str(datetime.date.today()) + '_mat.log', "GuitarBOT_log/Log_mat/"+str(datetime.date.today()) + '_mat.log')
                except:
                    ydisk.remove("GuitarBOT_log/Log_mat/"+str(datetime.date.today()) + '_mat.log', permanently=True)
                    ydisk.upload("log_files/"+str(datetime.date.today()) + '_mat.log', "GuitarBOT_log/Log_mat/"+str(datetime.date.today()) + '_mat.log')

                return True
                

def auto_registration(message, event_status:int = 0):

    """
    Функция для авторегистрации пользователя

    Args:
        message : объект message от telebot
        event_status (int): Статус подписки. По умолчанию равен 0 (Отключена)
    """

    rows = db_select_user_by_id(id_user = message.from_user.id)
    if rows == None:
        id_user = message.from_user.id
        first_name = message.from_user.first_name
        last_name = message.from_user.last_name
        nickname = message.from_user.username
        db_insert_user(id_user=id_user, first_name=first_name, last_name=last_name, nickname=nickname, event_status=event_status)