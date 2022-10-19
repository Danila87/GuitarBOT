from ast import Lambda
from email import message
from email.message import Message
from glob import escape
from itertools import count
from unicodedata import name
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from telebot import types
from datetime import datetime
from function import *
from datetime import date
from bs4 import BeautifulSoup

import random
import os
import speech_recognition as sr
import subprocess
import yadisk
import telebot
import time
import datetime
import re
import requests
import logging
import schedule
import threading


# Служебные данные для бота
# TOKEN = os.environ["BOT_TOKEN"]
TOKEN = '5371019683:AAGM6VbDWxOijJqyVLfPoox7JdlCxjsMNpU'
YANDEX_TOKEN = 'y0_AgAAAAAO_DuQAAhmIAAAAADOUpN38O9Jqe8fTx275pqgdwJIP-pbvR8'

y = yadisk.YaDisk(token=YANDEX_TOKEN)
telebot.apihelper.ENABLE_MIDDLEWARE = True
bot = telebot.TeleBot(TOKEN, skip_pending = True)


# Лог файлы
logfile_audio_record = f'audio_record//{str(datetime.date.today())}_record.log'
logfile_audio_error = f'audio_record//{str(datetime.date.today())}_error.log'
logfile_mat = f'log_files//{str(datetime.date.today())}_mat.log'


# Текущие даты
now = datetime.datetime.now()
year = str(now.year)
month = str(now.month)
day = str(now.day)

mut_user_values = {} 
list_banned_users = []

cotik_prison = open("img\cotik_prison.jpg", "wb")


# Словари
Months = {'Январь': '01', 'Февраль': '02', 'Март': '03', 'Апрель': '04', 'Май': '05', 'Июнь': '06', 'Июль': '07', 'Август': '08', 'Сентябрь': '09', 'Октябрь': '10', 'Ноябрь': '11', 'Декабрь': '12'}
Type_event = {'Орлятский круг': '1', 'Песенный зачёт' : '2', 'Спевка': '3', 'Квартирник': '4'}


# Класс для запоминания айди пользователя (Костыль ППЦ)
class UserBanRemove():
    def __init__(self, id_user):
        self.id_user = id_user

user_ban_remove = UserBanRemove('0')


# Хендлер для забаненых 
@bot.message_handler(func = lambda message: message.from_user.id in list_banned_users)
def banned(message):
    bot.send_message(message.chat.id, f'Ожидайте пока бан спадет')


# Удаление из бана
def banned_remove(id_user):
    
    print (id_user)
    list_banned_users.remove(id_user)


# Обнуление счетчика сообщений
def mut_user_values_clear():

    now = datetime.datetime.now().timestamp()
    for i in mut_user_values:
        if mut_user_values[i]['id_user'] not in list_banned_users:
            mut_user_values[i]['count'] = 0
            mut_user_values[i]['date_first'] = int(now)


# Расписание раз в 45 секунд
def schedule_user():

    schedule.every(45).seconds.do(mut_user_values_clear)

    while True:
        schedule.run_pending()
        time.sleep(1)


# Отдельный поток для расписания
thread = threading.Thread(target = schedule_user)
thread.start()

# Старт программы
@bot.message_handler(commands = ['start'])
def start (message):

    id_user = message.from_user.id
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    nickname = message.from_user.username

    row = db_user_registration_select(id_user = id_user)

    if row == 1:
        bot.send_message(message.chat.id, f'Вы уже зарегистрированы. \nПопробуйте ввести другую команду')
    else:
        bot.send_message(message.chat.id, f'Добро пожаловать!')
        time.sleep(1)
        sent = bot.send_message(message.chat.id, f'Согласны ли вы на рассылку новых событий, новостей и т.п.?', reply_markup=keyboard_yes_no(message))
        time.sleep(1)
        bot.register_next_step_handler(sent, user_registration_newsletter, id_user, first_name, last_name, nickname)

def user_registration_newsletter(message, id_user, first_name, last_name, nickname):

    if message.text == "Да":
        bot.send_message(message.chat.id, f'Успешно!\nОтказаться от рассылки можно в меню в разделе "Настройки"')
        db_user_insert(id_user = id_user, first_name = first_name, last_name = last_name, nickname = nickname, event_status = 1)
        time.sleep(1)
        keyboard_user(message)
    else:
        bot.send_message(message.chat.id, f'Успешно!\nПодписаться на рассылку можно в меню в разделе "Настройки"')
        db_user_insert(id_user = id_user, first_name = first_name, last_name = last_name, nickname = nickname, event_status = 0)
        time.sleep(1)
        keyboard_user(message)


# Обработка сообщений
@bot.middleware_handler(update_types = ['message'])
def modify_message(bot_instance, message):

    registration(message = message)
    mat_check(message = message, type_event = 'написании запроса')
    

    # МУТ система
    now = datetime.datetime.now().timestamp()
    cotik_prison = open('img//cotik_banned.jpg', 'rb')
    
    if message.from_user.id not in mut_user_values: # Если пользователя нет в словаре значений
        mut_user_values[message.from_user.id] = {'id_user' : message.from_user.id, 'date_first' : int(now), 'date_last' : int(now) ,'count': 0}

    elif mut_user_values[message.from_user.id]['count'] > 15: # Если запросов больше 15
        
        if message.from_user.id not in list_banned_users: # Если пользователя нет в бан листе
            list_banned_users.append(message.from_user.id)
            mut_user_values[message.from_user.id]['date_first'] = int(now)
            bot.send_message(message.chat.id, f'Установлен бан на 3 минуты!' )
            bot.send_photo(message.chat.id, cotik_prison)
        
        else: # Если пользователь есть в бан листе
            
            if mut_user_values[message.from_user.id]['date_last'] - mut_user_values[message.from_user.id]['date_first'] > 180: # Если время прошло
                mut_user_values[message.from_user.id]['count'] = 0
                mut_user_values[message.from_user.id]['date_first'] = int(now)
                banned_remove(id_user = mut_user_values[message.from_user.id]['id_user'])
                bot.send_message(message.chat.id, f'Бан закончился\nНе спамьте больше!')
           
            else: # Если время ещё не прошло
                mut_user_values[message.from_user.id]['date_last'] = mut_user_values[message.from_user.id]['date_last'] = int(now)
                bot.send_message(message.chat.id, f'До конца бана осталось {str(180 - (mut_user_values[message.from_user.id]["date_last"] - mut_user_values[message.from_user.id]["date_first"]))} секунд')
    
    else: # Если запросов меньше 15
        mut_user_values[message.from_user.id]['date_last'] = mut_user_values[message.from_user.id]['date_last'] = int(now)
        mut_user_values[message.from_user.id]['count'] = mut_user_values[message.from_user.id]['count'] + 1


# Админ меню
@bot.message_handler(func=lambda message: message.text == 'Админ меню')
def admin_menu(message):

    rows = db_user_select_by_id(message.from_user.id)
    bot.send_message(message.chat.id, f'Проверяю данные...')
    time.sleep(1.5)

    if rows[6] == 1 or rows [6] == 2:
        keyboard_admin(message)
    else:
        bot.send_message(message.chat.id, f'В доступе отказано.')
        error(message = message)


# Подменю
@bot.message_handler(func=lambda message: message.text == 'Вывести запросы 📈' or message.text == 'Назад')
def submenu(message):

    rows = db_user_select_by_id(message.from_user.id)
    
    if message.text == 'Вывести запросы 📈':
        if rows[6] == 1 or rows [6] == 2:
            KeyBoard = types.ReplyKeyboardMarkup(row_width = 1, resize_keyboard = True)
            btn1 = types.KeyboardButton(text = 'За день')
            btn2 = types.KeyboardButton(text = 'За месяц')
            btn3 = types.KeyboardButton(text = 'За год')
            btn4 = types.KeyboardButton(text = 'За всё время')
            btn5 = types.KeyboardButton(text = 'Выбрать месяц')
            btn6 = types.KeyboardButton(text = 'Отчёт за период')
            btn7 = types.KeyboardButton(text = 'Назад')
            KeyBoard.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7)
            bot.send_message(message.chat.id, f'Выберите период', reply_markup = KeyBoard)
        else:
            error(message = message)

    if message.text == 'Назад':
        if rows[6] in (1,2):
            keyboard_admin(message)
        else:
            keyboard_user(message)


# Все песенники
@bot.message_handler(func=lambda message: message.text == 'Песенники 📔')
def send_pesennik(message):

    keyboard = types.ReplyKeyboardMarkup(row_width = 1, resize_keyboard = True)
    btn1 = types.KeyboardButton(text = 'Назад')

    for i in db_all_song_book():
            btn = types.KeyboardButton(text=i[1])
            keyboard.add(btn)

    keyboard.add(btn1)
    bot.send_message(message.chat.id, f'Выберите песенник', reply_markup = keyboard)


# Выдача файла песенника
@bot.message_handler(func=lambda message: message.text in [x[1] for x in db_all_song_book()])
def send_file_by_title(message):

    song_book_title = message.text
    db_song_book_by_title (message = message, song_book_title=song_book_title)


# Вывод основного меню
@bot.message_handler(func=lambda message: message.text == 'Меню' or message.text == 'меню')
def main_menu(message):

    keyboard_user(message)


# Подменю "Администраторы"
@bot.message_handler(func=lambda message: message.text == 'Администраторы 💼')
def admin_edit_submenu(message):

    keyboard_admin_edit_submenu(message)


# Подменю "События"
@bot.message_handler(func=lambda message: message.text == 'События 📅')
def event_submenu(message):

    keyboard_event_submenu(message)


# Подменю "Отзывы"
@bot.message_handler(func=lambda message: message.text == 'Отзывы 💬')
def review_submenu(message):

    keyboard_review_submenu(message)


# Подменю "Настройки"
@bot.message_handler(func=lambda message: message.text == 'Настройки ⚙️')
def review_submenu(message):

    keyboard_setting_submenu(message, text = 'Открываю')


# Назначение администратора
@bot.message_handler(func=lambda message: message.text == 'Назначить администратором')
def appoint_as_administrator_start(message):

    sent = bot.send_message(message.chat.id, f'Введите Id пользователя, которого вы хотите назначить администратором')
    bot.register_next_step_handler(sent, appoint_as_administrator_end)

def appoint_as_administrator_end(message):

    id_user = message.text
    rows = db_user_select_by_id(id_user =  id_user)

    try:
        bot.send_message(message.chat.id, f'Проверяю пользователя {rows[3]}')
        time.sleep(1)
        if rows[6] == 3 or rows[6] == None:
            db_user_update(id_user = id_user, status = 2)
            bot.send_message(message.chat.id, f'Назначаю пользователя {rows[3]} администратором.')
            time.sleep(1)
            bot.send_message(message.chat.id, f'Права повышены!')
            try:
                garold = open('img\garold.jpg', 'rb')
                bot.send_photo(rows[0], garold)
                garold.close()
            except:
                bot.send_message(message.chat.id, f'Возникла ошибка из-за которой вы не получите мем :(')
            bot.send_message(f'{rows[0]}. Поздравляем {rows[3]}, вы назначены администратором! Введите Админ меню, чтобы открыть меню администратора.')
        else:
            bot.send_message(message.chat.id, f'Данный пользователь уже администратор.')
    except:
        bot.send_message(message.chat.id, f'Возникла ошибка. Возможно такого пользователя не существует или вы ввели неверный ID.\nПопробуйте ещё раз.')
        time.sleep(1)
        appoint_as_administrator_start(message)


# Понижение администратора
@bot.message_handler(func=lambda message: message.text == 'Убрать администратора')
def downgrad_as_administrator_start(message):

    sent = bot.send_message(message.chat.id, f'Введите Id пользователя, которого хотите убрать с поста администратора')
    bot.register_next_step_handler(sent, downgrad_as_administrator_end)

def downgrad_as_administrator_end(message):

    keyboard = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('Администратор', url = 'https://t.me/Danila877')
    keyboard.add(btn1)
    
    id_user = message.text
    
    try:
        rows = db_user_select_by_id(id_user = id_user)

        bot.send_message(message.chat.id, f'Проверяю пользователя {rows[3]}')
        time.sleep(1)
        if rows[6] == 2:
            db_user_update(id_user = id_user, status = 3)
            bot.send_message(message.chat.id, f'Понижаю пользователя {rows[3]}.')
            time.sleep(1)
            bot.send_message(message.chat.id, f'Права понижены!')
            try:
                cotik_sad = open ('img\cotik_sad.jpg', 'rb')
                bot.send_photo(rows[0], cotik_sad)
                cotik_sad.close()
            except:
                bot.send_message(message.chat.id, f'Возникла ошибка из-за которой вы не получите фото котика :(')
            bot.send_message(rows[0], f'Уважаемый/ая {rows[3]}, у вас забрали права администратора! Вы можете обратиться к разработчику для выяснения причин.')
            administrator_call(message)
        else:
            bot.send_message(message.chat.id, f'Данный пользователь не администратор.')

    except:
        bot.send_message(message.chat.id, f'Возникла ошибка. Возможно такого пользователя не существует или вы ввели неверный ID.\nПопробуйте ещё раз.')
        time.sleep(1)
        downgrad_as_administrator_start(message)


# Показать всех администраторов
@bot.message_handler(func=lambda message:message.text == 'Показать всех администраторов')
def show_all_administrators(message):
    
    admin_list = []
    try:
        for i in db_all_admin_select():
            admin_list.append(f'i[3] {i[7].lower()}\nID: {str(i[0])}\n\n')
            admin_list.sort()

        bot.send_message(message.chat.id,f'Администраторы:\n\n {("".join(admin_list))}')
    except:
        bot.send_message(message.chat.id, f'Администраторов нет.')


# Подключение и отключение рассылки
@bot.message_handler(func=lambda message: message.text == 'Подключить рассылку 🔔' or message.text == 'Отключить рассылку 🔕')
def user_newsletter_edit(message):

    if message.text == 'Подключить рассылку 🔔':
        db_user_newsletter_edit(id_user = message.from_user.id, status = 1)
        keyboard_setting_submenu(message, text = 'Обновляю данные')
        time.sleep(1)
        bot.send_message(message.chat.id, f'Рассылка подключена!')
    else:
        db_user_newsletter_edit(id_user = message.from_user.id, status = 0)
        keyboard_setting_submenu(message, text = 'Обновляю данные')
        time.sleep(1)
        bot.send_message(message.chat.id, f'Рассылка отключена!')


# Вывод данных пользователя
@bot.message_handler(func=lambda message: message.text == 'Показать мои данные 👤')
def user_profile_slow(message):

    try:
        rows = db_user_select_by_id(message.from_user.id)

        if rows[4] == 0:
            newsletter_subscription = 'Отключена'
        else:
            newsletter_subscription = 'Подключена'

        bot.send_message(message.chat.id, f'Ваш ID: *{str(rows[0])}*\nВаше имя: {str(rows[1])}\nВаша фамилия: {str(rows[2])}\nВаш никнейм: {str(rows[3])}\nВаш статус: {rows[7]}\nПодписка на рассылку: {newsletter_subscription}', parse_mode='Markdown')
    except:
        bot.send_message(message.chat.id, f'Не нашёл ваши данные:(\nВозможно вы не зарегистрированы. Введите /start для регистрации')


# Пересылка различных сообщений пользователям
@bot.message_handler(func=lambda message: message.text == 'Переслать сообщение ✉️')
def forward_message_start(message):

    rows = db_user_select_by_id(id_user =  message.from_user.id)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton(text = 'Отмена')
    keyboard.add(btn1)

    if rows[6] == 2 or rows[6] == 1:
        sent = bot.send_message(message.chat.id, f'Следующее сообщение будет отправлено пользовалям у которых подключена рассылка.', reply_markup=keyboard)
        bot.register_next_step_handler(sent, forward_message_end)
    else:
        error(message = message)

def forward_message_end(message):

    rows = db_user_select_by_id(id_user =  message.from_user.id)
    users = db_user_select()

    if message.text == 'Отмена':
        if rows[6] == 1 or rows [6] == 2:
            keyboard_admin(message)
        else:
            keyboard_user(message)
    else:
        bot.send_message(message.chat.id, f'Пробую разослать сообщение пользователям...')
        try:
            for i in users:
                bot.forward_message(i[0], message.chat.id, message.message_id)
            bot.send_message(message.chat.id, f'Сообщение успешно разослано.')
        except:
            bot.send_message(message.chat.id, f'Возникла ошибка')


# Оставить отзыв
@bot.message_handler(func=lambda message: message.text == 'Оставить отзыв 💬')
def review(message):

    sent = bot.send_message(message.chat.id, f'Напишите следующим сообщением свой отзыв.')
    bot.register_next_step_handler(sent, review_save)

def review_save(message):

    if message.content_type == 'text':
        if mat_check(message = message, type_event = 'написании отзыва'):
            sent = bot.send_message(message.chat.id, f'Мат запрещён!')
            bot.register_next_step_handler(sent, review_save)
            time.sleep (1)
            bot.send_message(message.chat.id, f'Напишите следующим сообщением свой отзыв.')
        else:
            id_user = message.from_user.id
            user_text = message.text
            db_review_insert(id_user = id_user, text_review = user_text, looked_status = 0, date = date.today(), message=message)
            bot.send_message(message.chat.id, f'Спасибо за ваш отзыв!')
    else:
        sent = bot.send_message(message.chat.id, f'Я принимаю только текст!)')
        bot.register_next_step_handler(sent, review_save)
        time.sleep (1)
        bot.send_message(message.chat.id, f'Напишите следующим сообщением свой отзыв.')


# Показать отзывы
@bot.message_handler(func=lambda message: message.text == 'Показать отзывы')
def review_show(message):

    rows = db_user_select_by_id(message.from_user.id)

    if rows[6] in (1,2) and len(rows) != 0:
        review_list = []
        count = 0
        for i in db_review_select():
            status = ''
            count = count + 1
            if i[3] == 0:  
                status = '*⚡️НОВЫЙ ОТЗЫВ⚡️*'
                db_review_update(id_review = i[0])
            elif i[3] == 1:
                status = 'Просмотрено'
            review_list.append(f'{str(count)}.{status}\nПользователь {str(i[6])} {str(i[7])} оставил следующий отзыв:\n_{str(i[2])}_\n\n*дата: {str(i[4])}*\n\n')
        bot.send_message(message.chat.id, (''.join(review_list)), parse_mode = 'Markdown')
    else:
        bot.send_message(message.chat.id, f'Отзывов нет')


# Поиск запросов по периодам
@bot.message_handler(func=lambda message: message.text == 'За всё время' or message.text == 'За день' or message.text == 'За месяц' or message.text == 'За год')
def requests_by_date(message):

    requests_list = []
    rows = db_user_select_by_id(message.from_user.id)

    if rows[6] == 1 or rows [6] == 2:

        if message.text == 'За всё время':
            row = len(db_requests_count())
            if row == 0:
                bot.send_message(message.chat.id, f'За выбранный период нет данных.\nПопробуйте позже.')
            else:
                for i in db_requests_count():
                    requests_list.append(f'{i[0]} : {str(i[1])}\n')
                bot.send_message(message.chat.id, (''.join(requests_list)))

        if message.text == 'За день':
            present_day = "'" + str(date.today()) + "'"
            row = len(db_requests_select_date(selected_date = present_day))
            if row == 0:
                bot.send_message(message.chat.id, f'За выбранный период нет данных.\nПопробуйте позже.')
            else:
                for i in db_requests_select_date(selected_date = present_day):
                    try:
                        requests_list.append(f'{i[0]} : {str(i[1])}\n')
                    except:
                        error(message = message)
                bot.send_message(message.chat.id, (''.join(requests_list)))

        if message.text == 'За месяц':
            present_month = "'"+year+'-0'+month+'-%'+"'"
            row = len(db_requests_select_date(selected_date = present_month))
            if row == 0:
                bot.send_message(message.chat.id, f'За выбранный период нет данных.\nПопробуйте позже.')
            else:
                for i in db_requests_select_date(selected_date = present_month):
                    try:
                        requests_list.append(f'{i[0]} : {str(i[1])}\n')
                    except:
                        error(message=message)
                bot.send_message(message.chat.id, (''.join(requests_list)))

        if message.text == 'За год':
            present_year = "'"+year+'-%-'+'%'+"'"
            row = len(db_requests_select_date(selected_date = present_year))
            if row == 0:
                bot.send_message(message.chat.id, f'За выбранный период нет данных.\nПопробуйте позже.')
            else:
                for i in db_requests_select_date(selected_date = present_year):
                    try:
                        requests_list.append(f'{i[0]} : {str(i[1])}\n')
                    except:
                        error(message = message)
                bot.send_message(message.chat.id, (''.join(requests_list)))
    else:
        error(message = message)


# Поиск запросов по конкретному месяцу
@bot.message_handler(func=lambda message: message.text == 'Выбрать месяц')
def requests_select_date(message):

    rows = db_user_select_by_id(message.from_user.id)

    if rows[6] == 1 or rows [6] == 2:
        chat_id = message.chat.id
        sent = bot.send_message(chat_id, f'Введите месяц. Например "Май"')
        bot.register_next_step_handler(sent, requests_select_date_show)
    else:
        error(message = message)

def requests_select_date_show(message):

    if message.content_type == 'text':
        month = message.text
        result = re.match(r'Январь\b|Февраль\b|Март\b|Апрель\b|Май\b|Июнь\b|Июль\b|Август\b|Сентябрь\b|Октябрь\b|Ноябрь\b|Декабрь\b', month)

        if result != None:
            requests_list = []
            present_month = "'"+year+'-'+Months[month]+'-%'+"'"
            row = len(db_requests_select_date(selected_date = present_month))
            if row == 0:
                bot.send_message(message.chat.id, f'За выбранный период нет данных.\nПопробуйте позже.')
            else:
                for i in db_requests_select_date(selected_date = present_month):
                    try:
                        requests_list.append(f'{i[0]} : {str(i[1])}\n')
                    except:
                        error(message = message)
                bot.send_message(message.chat.id, (''.join(requests_list)))
        else:
            bot.send_message(message.chat.id, f'Ошибка ввода, попробуйте еще раз!)')
            time.sleep(1)
            sent = bot.send_message(message.chat.id, f'Введите месяц. Например "Май"')
            bot.register_next_step_handler(sent, requests_select_date_show)

    else:
        bot.send_message(message.chat.id, f'Ошибка ввода, попробуйте еще раз!)')
        time.sleep(1)
        sent = bot.send_message(message.chat.id, f'Введите месяц. Например "Май"')
        bot.register_next_step_handler(sent, requests_select_date_show)


# Отчёт по запросам за выбранный период
@bot.message_handler(func=lambda message : message.text == 'Отчёт за период')
def request_select_date_between(message):

    rows = db_user_select_by_id(message.from_user.id)

    if rows[6] == 1 or rows [6] == 2:
        sent = bot.send_message(message.chat.id, f'Введите начальную дату в формате 2022-01-01')
        bot.register_next_step_handler(sent, date_between_start)
    else:
        error(message = message)

def date_between_start(message):

    if message.content_type == 'text':
        start_date = message.text
        result = re.match(r'([12]\d\d\d)\-(0[1-9]|1[12])\-(0[1-9]|[12]\d|3[12])', start_date)

        if result != None:
            sent = bot.send_message(message.chat.id, f'Введите конечную дату в формате 2022-01-01')
            bot.register_next_step_handler(sent, date_between_end, start_date)
        else:
            bot.send_message(message.chat.id, f'Возникла ошибка ввода, попробуйте еще раз.')   
            time.sleep(1)
            sent = bot.send_message(message.chat.id, f'Введите начальную дату в формате 2022-01-01') 
            bot.register_next_step_handler(sent, date_between_start) 

    else:
        bot.send_message(message.chat.id, f'Введите дату как в примере!)')   
        time.sleep(1)
        sent = bot.send_message(message.chat.id, f'Введите начальную дату в формате 2022-01-01') 
        bot.register_next_step_handler(sent, date_between_start)  

def date_between_end(message, start_date):

    if message.content_type == 'text':
        final_date = message.text
        result = re.match(r'([12]\d\d\d)\-(0[1-9]|1[12])\-(0[1-9]|[12]\d|3[12])', start_date)

        if result != None:
            bot.send_message(message.chat.id, f'Формирую отчёт...')
            time.sleep(1)
            start_date = "'" + start_date + "'"
            final_date = "'" + final_date + "'"
            requests_list = []
            if len(db_request_select_date_between(start_date = start_date, final_date = final_date)) == 0:
                bot.send_message(message.chat.id, f'За выбранный период нет данных.\nПопробуйте позже.')
            else:
                try:
                    for i in db_request_select_date_between(start_date = start_date, final_date = final_date):
                        requests_list.append(f'{i[0]} : {str(i[1])}\n')
                        requests_list.sort()
                    bot.send_message(message.chat.id, (''.join(requests_list)))
                except:
                    error(message = message)
        else:
            bot.send_message(message.chat.id, f'Возникла ошибка ввода, попробуйте еще раз.')
            time.sleep(1)
            sent = bot.send_message(message.chat.id, f'Введите начальную дату в формате "2022-01-01"') 
            bot.register_next_step_handler(sent, date_between_end, start_date)
    else:
        bot.send_message(message.chat.id, f'Введите дату как в примере!)')
        time.sleep(1)
        sent = bot.send_message(message.chat.id, f'Введите начальную дату в формате "2022-01-01"') 
        bot.register_next_step_handler(sent, date_between_end, start_date)


# Вставка события и его рассылка
@bot.message_handler(func=lambda message: message.text == 'Создать событие')
def event_create_start(message):

    rows = db_user_select_by_id(message.from_user.id)

    if rows[6] in (1,2):

        keyboard = types.ReplyKeyboardMarkup(row_width = 1, resize_keyboard=True)
        btn = []
        btn1 = types.KeyboardButton(text = 'Назад')
        for i in db_types_events():
            btn = types.KeyboardButton(text = i[0])
            keyboard.add(btn)
        keyboard.add(btn1)
        sent = bot.send_message(message.chat.id, f'Выберите тип события.', reply_markup = keyboard)
        bot.register_next_step_handler(sent, date_event)
    else:
        error(message = message)

def date_event(message):

    rows =  [x[0] for x in db_types_events()]

    if message.text == 'Назад':
        keyboard_admin(message)

    elif message.text in rows:
        type_event = message.text
        sent = bot.send_message(message.chat.id, f'Введите дату декоративную.\nНапример "6 апреля"')
        bot.register_next_step_handler(sent, date_event_technical, type_event)

    else:
        bot.send_message(message.chat.id, f'Вы ввели недопустимое значение, попробуйте ещё раз')
        time.sleep(1.5)
        event_create_start(message)

def date_event_technical (message, type_event):

    if message.text == 'Назад':
        keyboard_admin(message)

    elif message.content_type == 'text':
        date_event = message.text
        date_event = date_event.title()

        result = re.match(r'(\b[1-9]\b (Января|Февраля|Марта|Апреля|Мая|Июня|Июля|Августа|Сентября|Октября|Ноября|Декарбря)|(\b[12][0-9]\b (Января|Февраля|Марта|Апреля|Мая|Июня|Июля|Августа|Сентября|Октября|Ноября|Декарбря))|\b3[01]\b (Января|Марта|Апреля|Мая|Июня|Июля|Августа|Сентября|Октября|Ноября|Декарбря))', date_event)

        if result == None:
            sent = bot.send_message(message.chat.id, f'Вы ввели некорректную дату.\n Попробуйте ещё раз.')
            bot.register_next_step_handler(sent, date_event_technical, type_event)
            time.sleep (1.5)
            bot.send_message(message.chat.id, f'Введите дату декоративную.\nНапример "6 апреля"')
        else:
            sent = bot.send_message(message.chat.id, f'Введите техническую дату в формате "2022-01-01" после которой мероприятие будет не актуально.')
            bot.register_next_step_handler(sent, text_event, type_event, date_event)
    else:
        sent = bot.send_message(message.chat.id, f'Я принимаю только текст!)')
        bot.register_next_step_handler(sent, date_event_technical, type_event)
        time.sleep (1.5)
        bot.send_message(message.chat.id, f'Введите дату декоративную.\nНапример "6 апреля"')

def text_event(message, type_event, date_event):

    if message.text == 'Назад':
        keyboard_admin(message)
    
    elif message.content_type == 'text':
        date_technical = message.text
        result = re.match(r'([12]\d\d\d)\-(0[1-9]|1[12])\-(0[1-9]|[12]\d|3[12])', date_technical)

        if result == None:
            sent = bot.send_message(message.chat.id, f'Вы ввели недопустимую дату. Попробуйте ещё раз.')
            bot.register_next_step_handler(sent, text_event, type_event, date_event)
            time.sleep (1.5)
            bot.send_message(message.chat.id, f'Введите техническую дату в формате "2022-01-01" после которой мероприятие будет не актуально.')
        else:
            sent = bot.send_message(message.chat.id, f'Введите текст события')
            bot.register_next_step_handler(sent, event_preview, type_event, date_event, date_technical)
    else:
        sent = bot.send_message(message.chat.id, f'Я принимаю только текст!)')
        bot.register_next_step_handler(sent, text_event, type_event, date_event)
        time.sleep (1.5)
        bot.send_message(message.chat.id, f'Введите техническую дату в формате "2022-01-01" после которой мероприятие будет не актуально.')

def event_preview(message, type_event, date_event, date_event_technical):

    text_event = message.text

    if message.content_type == 'text':

        if mat_check(message = message, type_event = 'Создании события'):
            bot.send_message(message.chat.id, f'В вашем тексте обнаружен мат!\nДобро пожаловать в бан!')
            bot.send_message(message.chat.id, f'Напишите администратору для разблокировки')
            administrator_call(message)
            list_banned_users.append(str(message.from_user.id))
        else:
            bot.send_message(message.chat.id, f'Предпросмотр события: ')
            time.sleep(1)
            bot.send_message(message.chat.id, f'Тип события: {type_event}\nДата события: {date_event}\nТекст события:\n{text_event}\nТехническая дата: {date_event_technical}')
            time.sleep(1)
            sent = bot.send_message(message.chat.id, f'Сохранить событие?', reply_markup = keyboard_yes_no(message))
            bot.register_next_step_handler(sent, save_event, type_event, date_event, text_event, date_event_technical)

    else: 
        sent = bot.send_message(message.chat.id, f'Я принимаю только текст!)')
        bot.register_next_step_handler(sent, event_preview, type_event, date_event, date_event_technical)
        time.sleep(0.5)
        bot.send_message(message.chat.id, f'Введите текст события')

def save_event(message, type_event, date_event, text_event, date_event_technical):

    if message.text == 'Да':
        bot.send_message(message.chat.id, f'Событие сохранено.')
        time.sleep(1)
        type_event = Type_event[type_event]
        db_event_insert(dtype_event = type_event, ddate_event = date_event, ddate_event_techical = date_event_technical,dtext_event = text_event)
        keyboard = types.ReplyKeyboardMarkup(row_width = 1, resize_keyboard = True)
        btn1 = types.KeyboardButton(text = 'Да')
        btn2 = types.KeyboardButton(text = 'Нет')
        sent = bot.send_message(message.chat.id, f'Разослать событие пользователям?', reply_markup = keyboard_yes_no(message))
        bot.register_next_step_handler(sent, event_newsletter, type_event)

    elif message.text == 'Нет':
        keyboard = types.ReplyKeyboardMarkup(row_width = 1, resize_keyboard = True)
        btn1 = types.KeyboardButton(text='Да')
        btn2 = types.KeyboardButton(text='Нет.\nВернуться в главное меню.')
        keyboard.add(btn1, btn2)
        sent = bot.send_message(message.chat.id, f'Создать заново?', reply_markup = keyboard_yes_no(message))
        bot.register_next_step_handler(sent, event_hub)

    else:
        sent = bot.send_message(message.chat.id, f'Я вас непонимаю. Введите "Да" или "Нет"')
        bot.register_next_step_handler(sent, event_preview, type_event, date_event, date_event_technical)

def event_hub(message):

    if message.text == 'Да':
        event_create_start(message)
    else:
        keyboard_admin(message)

def event_newsletter(message, type_event):

    if message.text == 'Да':
        event = db_event_select_last(type_event = type_event)
        for i in db_user_select():
            bot.send_message(i[0], f'Опубликовано новое событие от гитаристов.')
            time.sleep(1)
            bot.send_message(i[0], f'{event[2]} состоится {event[6].lower()}!\n{event[1]}')
        keyboard_admin(message)

    elif message.text == 'Нет':
        keyboard_admin(message)

    else:  
        sent = bot.send_message(message.chat.id, f'Я вас непонимаю. Введите "Да" или "Нет"')
        bot.register_next_step_handler(sent, event_newsletter, type_event)


# Вывод ближайших событий
@bot.message_handler(func=lambda message: message.text == 'Показать ближайшие события')
def event_show(message):

    count = 0
    key = False

    for i in db_types_events():
        count = count + 1
        try:
            event = db_event_select_last(type_event = count)
            bot.send_message(message.chat.id, f'{event[2]} состоится {event[6].lower()}!\n{event[1]}')
            time.sleep(0.5)
            key = True
        except:
            pass
    if key == False:
        bot.send_message(message.chat.id, f'Новых событий пока нет')


# Бан лист
@bot.message_handler(func=lambda message: message.text == 'Бан лист')
def ban_list_show(message):

    rows = db_user_select_by_id(message.from_user.id)

    if rows[6] == 1:

        if len(list_banned_users) is not 0:
            keyboard = types.InlineKeyboardMarkup()
            for i in list_banned_users:
                btn0 = types.InlineKeyboardButton(i, callback_data = i)
                keyboard.add(btn0)
            bot.send_message(message.chat.id, f'Бан лист:', reply_markup = keyboard)
        else:
            bot.send_message(message.chat.id, f'Бан лист пуст')


#Удаление пользователя из бан листа
@bot.callback_query_handler(func=lambda call: call.data in list_banned_users or call.data == 'Yes' or call.data == 'No')
def ban_list_delete_start(call):

    if call.data in list_banned_users:
        user_ban_remove.id_user = call.data
        keyboard = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton('Нет', callback_data = 'No')
        btn2 = types.InlineKeyboardButton('Да', callback_data = 'Yes')
        btn3 = types.InlineKeyboardButton('Удалить из бана?')
        keyboard.add(btn3)
        keyboard.row(btn1, btn2)
        bot.edit_message_reply_markup(chat_id = call.message.chat.id, message_id = call.message.message_id, reply_markup = keyboard)

    try:
        if call.data == 'Yes':
            list_banned_users.remove(user_ban_remove.id_user)
            if len(list_banned_users) is not 0:
                keyboard = types.InlineKeyboardMarkup()
                for i in list_banned_users:
                    btn0 = types.InlineKeyboardButton(i, callback_data = i)
                    keyboard.add(btn0)
                bot.edit_message_reply_markup(chat_id = call.message.chat.id, message_id = call.message.message_id, reply_markup = keyboard)
            else:
                bot.send_message(call.message.chat.id, f'Бан лист пустой')

        elif call.data == 'No':
            if len(list_banned_users) is not 0:
                keyboard = types.InlineKeyboardMarkup()
                for i in list_banned_users:
                    btn0 = types.InlineKeyboardButton(i, callback_data = i)
                    keyboard.add(btn0)
                bot.edit_message_reply_markup(chat_id = call.message.chat.id, message_id = call.message.message_id, reply_markup = keyboard)
            else:
                bot.send_message(call.message.chat.id, f'Бан лист пустой')
    except:
        pass


# Список песен
@bot.message_handler(func=lambda message: message.text == 'Список песен 📔')
def list_of_songs(message):

    rows = db_type_song_select()
    keyboard = types.InlineKeyboardMarkup()
    
    for i in rows: 
        btn = types.InlineKeyboardButton(i[1], callback_data = i[1])
        keyboard.add(btn)
    bot.send_message(message.chat.id, f'Доступные категории', reply_markup = keyboard)


# Обработка типов песен и вывод списка песен
@bot.callback_query_handler(func=lambda call: call.data == 'back_to_category' or call.data in [x[1] for x in db_type_song_select()] or call.data  == 'next_page' or call.data == 'back_page')
def list_of_song_by_type1(call):

    if call.data in [x[1] for x in db_type_song_select()]:
        btn3 = types.InlineKeyboardButton('Вернуться к категориям', callback_data = 'back_to_category')

        row = db_song_select_by_type(type_song = call.data)
        keyboard = types.InlineKeyboardMarkup()
        
        for i in row:
            btn = types.InlineKeyboardButton(i[1], callback_data = i[1])
            keyboard.add(btn)
        keyboard.add(btn3)
        bot.edit_message_reply_markup(chat_id = call.message.chat.id, message_id = call.message.message_id, reply_markup = keyboard)
    
    if call.data == 'back_to_category':
        rows = db_type_song_select()
        keyboard = types.InlineKeyboardMarkup()
        for i in rows: 
            btn_type = types.InlineKeyboardButton(i[1], callback_data = i[1])
            keyboard.add(btn_type)
        bot.edit_message_reply_markup(chat_id = call.message.chat.id, message_id = call.message.message_id, reply_markup = keyboard)


# Вывод картинки для Маши
@bot.message_handler(commands = ['Masha'])
def Masha (message):

    with open('img\masha.jpg', 'wb') as i:
        i.write(requests.get(get_img_from_Masha(message=message)).content)

    with open('img\masha.jpg', 'rb') as i:
        bot.send_photo(message.chat.id, i)

    time.sleep(1)
    sent = bot.send_message(message.chat.id, f'Ещё?', reply_markup=keyboard_yes_no(message))
    bot.register_next_step_handler(sent, Masha_hub)


def Masha_hub(message):
    
    if message.text == 'Да':
        Masha(message = message)
    else:
        keyboard_user(message = message)


# Помощь
@bot.message_handler(func=lambda message: message.text == 'Помощь ❓')
def help (message):
    
    bot.send_message(message.chat.id, f'ПОМОЩЬ\n\n• Бот создан для облегчения поиска песен из песенника. Для того чтобы найти песню просто введите её название, можно с ошибками но незначительными:)\n\n• Если у вас неожиданно пропало меню или по какой-то причине не оно открылось отправьте боту "Меню" и он его перезапустит.\n\n• В случае если бот не работает должным образом и выдаёт ошибку то вы можете написать администратору (В случае ошибки бот пришлёт на него ссылку) либо оставить отзыв с описанием проблемы.\n\n• Если программой предусмотрено, что у вас недостаточно прав для выполнения определённых функций то бот пришлёт вам ошибку с котиком :)\n\n• Если у вас есть пожелания по поводу улучшения работы бота или вы просто хотите оставить благодарность, то для этого вы можете написать отзыв через соответствующую команду!)')


# Поиск песни через текст и аудио
@bot.message_handler(content_types = ['voice', 'text'])
def search_song(message):

    if message.content_type == 'text':

       title_song = message.text
       title_song = title_song.lower().replace(' ', '')
       song_searc(message = message, title_song=title_song)

    elif message.content_type == 'voice':

        try:
            file_info = bot.get_file(message.voice.file_id)
            path = os.path.splitext(file_info.file_path)[0] # Вот тут-то и полный путь до файла (например: voice/file_2.oga)
            fname = os.path.basename(path) # Преобразуем путь в имя файла (например: file_2.oga)
            fname = f'audio_record//{fname}'
            print(fname)
            doc = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(TOKEN, file_info.file_path))# Получаем и сохраняем присланную голосвуху (Ага, админ может в любой момент отключить удаление айдио файлов и слушать все, что ты там говоришь. А представь, что такую бяку подселят в огромный чат и она будет просто логировать все сообщения [анонимность в телеграмме, ахахаха])
            
            with open(f'{fname}.oga', 'wb') as f:
                f.write(doc.content) # вот именно тут и сохраняется сама аудио-мессага
            
            process = subprocess.run(['ffmpeg', '-i', fname+'.oga', fname+'.wav'])
            result = audio_to_text(f'{fname}.wav', message = message) # Вызов функции для перевода аудио в текст, а заодно передаем имена файлов, для их последующего удаления
            resultsrc = result.lower().replace(' ', '')
            song_searc(message = message, title_song = resultsrc)
            
            with open(logfile_audio_record, 'a', encoding = 'utf-8') as logrecord:
                logrecord.write(f'{str(datetime.datetime.today().strftime("%H:%M:%S"))}: Пользователь {str(message.from_user.id)}_{str(message.from_user.first_name)}_{str(message.from_user.last_name)}_{str(message.from_user.username)} записал {result}\n')
            
            try:
                y.upload(f'audio_record/{str(datetime.date.today())}_record.log', f'GuitarBOT_log/Log_record/{str(datetime.date.today())}_record.log')
            except:
                y.remove(f'GuitarBOT_log/Log_record/{str(datetime.date.today())}_record.log', permanently = True)
                y.upload(f'audio_record/{str(datetime.date.today())}_record.log', f'GuitarBOT_log/Log_record/{str(datetime.date.today())}_record.log')
            
        
        except sr.UnknownValueError as e:
            bot.send_message(message.chat.id, f'У меня не получилось разобрать ваше сообщение.\nПопробуйте ещё раз')

        except Exception as e:

            with open(logfile_audio_error, 'a', encoding = 'utf-8') as logerr:
                logerr.write(f'{str(datetime.datetime.today().strftime("%H:%M:%S"))}: Пользователь {str(message.from_user.id)}_{str(message.from_user.first_name)}_{str(message.from_user.last_name)}_{str(message.from_user.username)} ошибка {str(e)}\n')

            try:
                y.upload(f'audio_record/{str(datetime.date.today())}_error.log', f'GuitarBOT_log/Log_record/{str(datetime.date.today())}_error.log')
            except:
                y.remove(f'GuitarBOT_log/Log_record/{str(datetime.date.today())}_error.log', permanently = True)
                y.upload(f'audio_record/{str(datetime.date.today())}_error.log', f'GuitarBOT_log/Log_record/{str(datetime.date.today())}_error.log')
            error(message = message)
        
        finally:
            os.remove(f'{fname}.wav')
            os.removef(f'{fname}.oga')


# Вывод текста песни через кнопку
@bot.callback_query_handler(func=lambda call: call.data in [x[1] for x in db_song_select_all()])
def call_data(call):

    rows = db_song_select(title_song = call.data)
    bot.send_message(call.message.chat.id, f'{rows[1].upper()}\n\n{rows[3]}')

    try:
        audio = open(r'song'+rows[4], 'rb')
        bot.send_audio(call.message.chat.id, audio, title = rows[1])
        audio.close()
    except:
        pass
    db_requests_insert(id_user = call.message.from_user.id, requests = rows[1], date = date.today())

bot.polling(non_stop = True)
