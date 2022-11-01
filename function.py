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


#TOKEN = os.environ["BOT_TOKEN"]
TOKEN = '5371019683:AAGM6VbDWxOijJqyVLfPoox7JdlCxjsMNpU'
YANDEX_TOKEN = 'y0_AgAAAAAO_DuQAAhmIAAAAADOUpN38O9Jqe8fTx275pqgdwJIP-pbvR8'
ydisk = yadisk.YaDisk(token=YANDEX_TOKEN)
bot = telebot.TeleBot(TOKEN, skip_pending=True)
conn = sqlite3.connect('database//database.db', check_same_thread=False)
cotik = open('img//cotik.jpg', 'rb')
logfile_mat = 'log_files//' + str(datetime.date.today()) + '_mat.log'


# РАЗЛИЧНЫЕ МЕНЮ ПОЛЬЗОВАТЕЛЕЙ


# Админ меню
def get_keyboard_admin(message):

    keyboard = types.ReplyKeyboardMarkup(row_width = 2, resize_keyboard=True)
    btn_song_list = types.KeyboardButton(text="Список песен 📔")
    btn_reviews = types.KeyboardButton(text="Отзывы 💬")
    btn_requests = types.KeyboardButton(text="Вывести запросы 📈")
    btn_events = types.KeyboardButton(text="События 📅")
    btn_resend_message = types.KeyboardButton(text="Переслать сообщение ✉️")
    btn_settings = types.KeyboardButton(text="Настройки ⚙️")
    keyboard.add(btn_song_list, btn_reviews, btn_requests, btn_events, btn_resend_message ,btn_settings)
    time.sleep(1)
    bot.send_message(message.chat.id, "Открываю главное меню", reply_markup = keyboard)


# Пользовательское меню 
def get_keyboard_user(message):

    keyboard = types.ReplyKeyboardMarkup(row_width = 3, resize_keyboard=True)
    btn_song_list = types.KeyboardButton(text="Список песен 📔")
    btn_push_reviews = types.KeyboardButton(text="Оставить отзыв 💬")
    btn_events = types.KeyboardButton(text="События 📅")
    btn_settings = types.KeyboardButton(text="Настройки ⚙️")
    keyboard.add(btn_song_list, btn_push_reviews, btn_events, btn_settings)
    bot.send_message(message.chat.id, "Открываю меню", reply_markup = keyboard)


# Да/Нет клавиатура
def get_keyboard_yes_no():

    keyboard = types.ReplyKeyboardMarkup(row_width = 1, resize_keyboard=True)
    btn_yes = types.KeyboardButton(text="Да")
    btn_no = types.KeyboardButton(text="Нет")
    keyboard.add(btn_yes, btn_no)
    return keyboard


# Подменю настроек
def get_keyboard_setting_submenu(message, text):

    rows = db_select_user_by_id(id_user = message.from_user.id)
    keyboard = types.ReplyKeyboardMarkup(row_width = 2, resize_keyboard = True)
    btn_show_data = types.KeyboardButton(text="Показать мои данные 👤")
    btn_song_books = types.KeyboardButton(text="Песенники 📔")
    btn_help = types.KeyboardButton(text="Помощь ❓")
    btn_back = types.KeyboardButton(text="Назад")
    if rows[4] == 0 and rows != NoneType:
        btn_newsletter = types.KeyboardButton(text="Подключить рассылку 🔔")
    else:
        btn_newsletter = types.KeyboardButton(text="Отключить рассылку 🔕")
    if rows[6] == 1:
        btn_ban_list = types.KeyboardButton(text="Бан лист")
        btn_admin = types.KeyboardButton(text="Администраторы 💼")
        keyboard.add(btn_show_data, btn_newsletter, btn_admin, btn_song_books, btn_help, btn_ban_list, btn_back)
        bot.send_message(message.chat.id, text, reply_markup = keyboard)
    else:
        keyboard.add(btn_show_data, btn_newsletter, btn_song_books, btn_help, btn_back)
        bot.send_message(message.chat.id, text, reply_markup = keyboard)

# Подменю "События"
def get_keyboard_event_submenu(message):

    rows = db_select_user_by_id(id_user = message.from_user.id)    
    keyboard = types.ReplyKeyboardMarkup(row_width = 2, resize_keyboard=True)
    btn_event_all = types.KeyboardButton(text="Показать ближайшие события")
    btn_back = types.KeyboardButton(text="Назад")
    if rows[6] in (1,2):
        btn_create_event = types.KeyboardButton(text="Создать событие")
        keyboard.add(btn_event_all, btn_create_event, btn_back)
        bot.send_message(message.chat.id, "Открываю", reply_markup = keyboard)
    else:
        keyboard.add(btn_event_all, btn_back)
        bot.send_message(message.chat.id, "Открываю", reply_markup = keyboard)


# Подменю "Отзывы"
def get_keyboard_review_submenu(message):

    rows = db_select_user_by_id(id_user = message.from_user.id)

    if rows[6] == 1 or rows[6] == 2:
        rows = db_select_user_by_id(id_user = message.from_user.id)
        keyboard = types.ReplyKeyboardMarkup(row_width = 2, resize_keyboard = True)
        btn_rewievs_all = types.KeyboardButton(text="Показать отзывы")
        btn_pull_rewievs = types.KeyboardButton(text="Оставить отзыв 💬")
        btn_back = types.KeyboardButton(text="Назад")
        keyboard.add(btn_rewievs_all, btn_pull_rewievs, btn_back)
        bot.send_message(message.chat.id, "Открываю", reply_markup = keyboard)
    else:
        error(message = message)


# Подменю "Администраторы"
def get_keyboard_admin_edit_submenu(message):

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
        error(message = message)


# Кнопка с ссылкой на администратора 
def get_administrator_call(message):

    keyboard = types.InlineKeyboardMarkup()
    btn_admin = types.InlineKeyboardButton("Администратор", url='https://t.me/Danila877')
    keyboard.add(btn_admin)
    bot.send_message(message.chat.id, "👇", reply_markup = keyboard)


# ФУНКЦИИ РАБОТЫ С ПОЛЬЗОВАТЕЛЯМИ


# Получение всех пользователей
def db_select_users_all():

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Users LEFT OUTER JOIN Role ON Users.Id_role = Role.Id_role")
    rows = cursor.fetchall()
    return rows


# Все айди чаты согласные на рассылку
def db_select_user_by_newsletter():

    cursor = conn.cursor()
    cursor.execute("SELECT id_user FROM Users WHERE Event_status = 1")
    rows = cursor.fetchall()
    return rows


# Конкретный человек по айди
def db_select_user_by_id(id_user:int):

    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM Users LEFT OUTER JOIN Role ON Users.Id_role = Role.Id_role WHERE id_user = ?", (id_user,))
        rows = cursor.fetchone()
        return rows
    except:
        pass


# Внесение данных о новом пользователе
def db_insert_user(id_user: int, first_name: str, last_name:str, nickname: str, event_status: int):

    try:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO Users (id_user, First_name, Last_name, Nickname, Event_status, Id_role) VALUES (?,?,?,?,?,3)', (id_user, first_name, last_name, nickname, event_status))
        conn.commit()
    except:
        pass


# Проверка на регистрацию пользователя
def db_select_user_registration(id_user: int):

    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Users WHERE id_user = ?', (id_user,))
    rows = cursor.fetchall()
    row = len(rows)
    return row


# Изменение статуса рассылки у пользователя
def db_update_user_newsletter(status: int, id_user: int):

    cursor = conn.cursor()
    cursor.execute("UPDATE Users SET Event_status = ? WHERE id_user = ?", (status, id_user))
    conn.commit()


# Изменение администраторов
def db_update_user(id_user:int, status):

    cursor = conn.cursor()
    cursor.execute("UPDATE Users SET Id_role = ? WHERE id_user = ?", (status, id_user))
    conn.commit()


# Показ всех администраторов
def db_select_all_admin():

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Users LEFT OUTER JOIN Role ON Users.Id_role = Role.Id_role WHERE Users.Id_role = 2")
    rows = cursor.fetchall()
    return rows
    

# ВСЕ ФУНКЦИИ РАБОТЫ С ОТЗЫВАМИ


# Вставка отзывов
def db_insert_review(id_user:int, text_review: str, looked_status: int, date:str, message):

    try:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO Reviews (id_user, text_review, lookeed_status, date) VALUES (?, ?, ?, ?)', (id_user, text_review, looked_status, date))
        conn.commit()
    except:
        bot.send_message(message.chat.id, "Иди отсюда, черт")


# Поиск отзывов
def db_select_reviews():

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Reviews LEFT OUTER JOIN Users ON Reviews.id_user = Users.id_user WHERE date > date('now', '-7 days')")
    rows = cursor.fetchall()
    return rows


# Обновление отзывов
def db_update_review(id_review: int):

    cursor = conn.cursor()
    cursor.execute('UPDATE Reviews SET lookeed_status = 1 WHERE id_review = ?',(id_review,))
    conn.commit()


# ВСЕ ФУНКЦИИ РАБОТЫ С ЗАПРОСАМИ


# Вывод количества запросов за всё время
def db_requests_count():

    cursor = conn.cursor()
    cursor.execute('SELECT requests, COUNT (*) AS Count FROM Requests GROUP BY requests ORDER BY Count DESC')
    rows = cursor.fetchall()
    return rows


# Внесение данных в таблицу с запросами
def db_insert_request(id_user: int, requests: str, date: str):

    try:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO Requests (id_user, requests, date) VALUES (?, ?, ?)', (id_user, requests, date))
        conn.commit()
    except:
        pass

# Вывод запросов по дате
def db_select_requests_by_date(selected_date:str):

    cursor = conn.cursor()
    query = 'SELECT requests, COUNT (*) AS Count FROM Requests WHERE date LIKE ' + selected_date + ' GROUP BY requests ORDER BY Count DESC'
    cursor.execute(query)
    rows = cursor.fetchall()
    return rows


# Вывод запросов за выбранный период
def db_select_requests_the_period(start_date:str, final_date:str):

    cursor = conn.cursor()
    query = "SELECT requests, COUNT (*) AS Count FROM Requests WHERE date BETWEEN " + start_date + " AND " + final_date + " GROUP BY requests ORDER BY Count DESC"
    cursor.execute(query)
    rows = cursor.fetchall()
    return rows


# ВСЕ ФУНКЦИИ РАБОТЫ С СОБЫТИЯМИ


# Все типы событий
def db_select_event_types():

    cursor = conn.cursor()
    cursor.execute("SELECT Name_event FROM Type_event")
    rows = cursor.fetchall()
    return rows


# Вставка события
def db_insert_event(dtype_event: int, ddate_event: str, dtext_event: str, ddate_event_techical: str):

    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Events (Text_event, Date_event, Date_event_technical ,Event_type) VALUES (?, ?, ?, ?)", (dtext_event, ddate_event, ddate_event_techical ,dtype_event))
        conn.commit()
    except:
        pass

# Получение событий
def db_select_latest_event(type_event: str):

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Events LEFT OUTER JOIN Type_event ON Events.Event_type = Type_event.Id_event WHERE Event_type = ? AND Date_event_technical > date('now') ORDER BY Id_event DESC LIMIT 1", (type_event,))
    rows = cursor.fetchone()
    return rows


# ВСЕ ФУНКЦИИ РАБОТЫ С ПЕСНЯМИ


# Поиск всех песен
def db_select_song_all():

    cursor = conn.cursor()
    try:
        cursor.execute('SELECT * FROM songs')
        rows = cursor.fetchall()
        return rows
    except:
        pass


# Поиск песни по заголовку
def db_select_song(title_song):

    cursor = conn.cursor()
    cursor.execute('SELECT * FROM songs WHERE Title_song = ?',(title_song,))
    rows = cursor.fetchone()
    return rows


# Поиск песни по категории
def db_select_song_by_type(type_song):

    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Songs LEFT OUTER JOIN Type_song ON Songs.Type_song = Type_song.id_type WHERE Type_song.Type_song = ?', (type_song,))
    rows = cursor.fetchall()
    return rows


# Получение категорий песен
def db_select_song_type():

    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Type_song ')
    rows = cursor.fetchall()
    return rows


# Отбор песен
def song_search(message, title_song):

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


# Вывод ошибки
def error(message):

    try:
        time.sleep(0.5)
        bot.send_photo(message.chat.id, cotik)
        time.sleep(0.5)
        bot.send_message(message.chat.id, "Что-то пошло не так.\nО данной ошибке можете написать в отзывах или написать самому разработчику по ссылке ниже !)")
        get_administrator_call(message)
    except:
        bot.send_message(message.chat.id, "Возникла неожиданная ошибка.\nОбратитесь к администратору.")
        get_administrator_call(message)
        bot.send_photo(message.chat.id, cotik)


# Все песенники
def db_select_songbook_all():
 
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Song_book")
    rows = cursor.fetchall()
    return rows


# Песенник по заголовку
def db_select_songbook_by_title(message, song_book_title):

    cursor = conn.cursor()
    cursor.execute("SELECT file_path FROM Song_book WHERE title_book = ?", (song_book_title,))
    rows = cursor.fetchone()
    file = open (rows[0], 'rb')
    bot.send_message(message.chat.id, "Загружаю...")
    bot.send_document(message.chat.id, file)


# Получение фотографии для Маши
def get_img_from_Masha(message):

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


# Перевод аудио в текст
def audio_to_text(dest_name: str, message):

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


# Проверка на мат
def mat_check(message, type_event):
    
    if message.content_type == 'text':
        row = db_select_user_by_id(id_user=message.from_user.id)
        words = message.text.split(' ')
        for i in words:
            result = re.match(r'\b((у|[нз]а|(хитро|не)?вз?[ыьъ]|с[ьъ]|(и|ра)[зс]ъ?|(о[тб]|под)[ьъ]?|(.\B)+?[оаеи])?-?([её]б(?!о[рй])|и[пб][ае][тц]).*?|(н[иеа]|([дп]|верт)о|ра[зс]|з?а|с(ме)?|о(т|дно)?|апч)?-?ху([яйиеёю]|ли(?!ган)).*?|(в[зы]|(три|два|четыре)жды|(н|сук)а)?-?бл(я(?!(х|ш[кн]|мб)[ауеыио]).*?|[еэ][дт]ь?)|(ра[сз]|[зн]а|[со]|вы?|п(ере|р[оие]|од)|и[зс]ъ?|[ао]т)?п[иеё]зд.*?|(за)?п[ие]д[аое]?р([оа]м|(ас)?(ну.*?|и(ли)?[нщктл]ь?)?|(о(ч[еи])?|ас)?к(ой)|юг)[ауеы]?|манд([ауеыи](л(и[сзщ])?[ауеиы])?|ой|[ао]вошь?(е?к[ауе])?|юк(ов|[ауи])?)|муд([яаио].*?|е?н([ьюия]|ей))|мля([тд]ь)?|лять|([нз]а|по)х|м[ао]л[ао]фь([яию]|[еёо]й))\b', message.text)
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
                
# Авторегистрация
def auto_registration(message, event_status):

    rows = db_select_user_by_id(id_user = message.from_user.id)
    if rows == None:
        id_user = message.from_user.id
        first_name = message.from_user.first_name
        last_name = message.from_user.last_name
        nickname = message.from_user.username
        db_insert_user(id_user=id_user, first_name=first_name, last_name=last_name, nickname=nickname, event_status=event_status)