from ast import Lambda
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
import re

#Служебные данные для бота
token = "5371019683:AAGM6VbDWxOijJqyVLfPoox7JdlCxjsMNpU"
bot = telebot.TeleBot(token)
garold = open('img\garold.jpg', 'rb')
cotik_sad = open ("img\cotik_sad.jpg", "rb")

#Текущие даты
now = datetime.datetime.now()
year = str(now.year)
month = str(now.month)
day = str(now.day)

#Словари
Months = {'Январь': '01', 'Февраль': '02', 'Март': '03', 'Апрель': '04', 'Май': '05', 'Июнь': '06', 'Июль': '07', 'Август': '08', 'Сентябрь': '09', 'Октябрь': '10', 'Ноябрь': '11', 'Декабрь': '12'}
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
        db_user_insert(id_user = id_user, first_name = first_name, last_name = last_name, nickname = nickname, event_status = 1)
        time.sleep(1)
        keyboard_user(message)
    else:
        bot.send_message(message.chat.id, "Успешно!\nПодписаться на рассылку можно в меню в разделе 'Настройки'")
        db_user_insert(id_user = id_user, first_name = first_name, last_name = last_name, nickname = nickname, event_status = 0)
        time.sleep(1)
        keyboard_user(message)


#Админ меню
@bot.message_handler(func = lambda message: message.text == 'Админ меню')
def admin_menu(message):

    rows = db_user_select_by_id(message.from_user.id)
    bot.send_message(message.chat.id, "Проверяю данные...")
    time.sleep(1.5)

    if rows[6] == 3 or rows [6] == 2:
        keyboard_admin(message)
    else:
        bot.send_message(message.chat.id, "В доступе отказано.")
        error(message = message)


#Подменю
@bot.message_handler(func = lambda message: message.text == "Вывести запросы" or message.text == "Назад")
def submenu(message):

    rows = db_user_select_by_id(message.from_user.id)
    if message.text == "Вывести запросы":
        if rows[6] == 1 or rows [6] == 2:
            KeyBoard = types.ReplyKeyboardMarkup(row_width = 1, resize_keyboard = True)
            btn1 = types.KeyboardButton(text = "За день")
            btn2 = types.KeyboardButton(text = "За месяц")
            btn3 = types.KeyboardButton(text = "За год")
            btn4 = types.KeyboardButton(text = "За всё время")
            btn5 = types.KeyboardButton(text = "Выбрать месяц")
            btn6 = types.KeyboardButton(text = "Отчёт за период")
            btn7 = types.KeyboardButton(text = "Назад")
            KeyBoard.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7)
            bot.send_message(message.chat.id, "Выберите период", reply_markup = KeyBoard)
        else:
            error(message = message)

    if message.text == "Назад":
        if rows[6] == 1 or rows [6] == 2:
            keyboard_admin(message)
        else:
            keyboard_user(message)

@bot.message_handler(func = lambda message: message.text == 'Песенники')
def send_pesennik_io_spo(message):

    keyboard = types.ReplyKeyboardMarkup(row_width = 1, resize_keyboard = True)
    btn1 = types.KeyboardButton(text = "Назад")

    for i in db_all_song_book():
            btn = types.KeyboardButton(text=i[1])
            keyboard.add(btn)
    keyboard.add(btn1)
    bot.send_message(message.chat.id, "Выберите песенник", reply_markup = keyboard)

@bot.message_handler(func = lambda message: message.text in [x[1] for x in db_all_song_book()])
def send_file_by_title(message):

    song_book_title = message.text
    db_song_book_by_title (message = message, song_book_title=song_book_title)


#Вывод основного меню
@bot.message_handler(func = lambda message: message.text == 'Меню' or message.text == "меню")
def main_menu(message):

    keyboard_user(message)

#Подменю "Администраторы"
@bot.message_handler(func=lambda message: message.text == "Администраторы")
def admin_edit_submenu(message):

    keyboard_admin_edit_submenu(message)

#Подменю "События"
@bot.message_handler(func = lambda message: message.text == "События")
def event_submenu(message):

    keyboard_event_submenu(message)

#Подменю "Отзывы"
@bot.message_handler(func = lambda message: message.text == "Отзывы")
def review_submenu(message):

    keyboard_review_submenu(message)

#Подменю "Настройки"
@bot.message_handler(func = lambda message: message.text == "Настройки")
def review_submenu(message):

    keyboard_setting_submenu(message, text = "Открываю")

#Назначение администратора
@bot.message_handler(func=lambda message: message.text == "Назначить администратором")
def appoint_as_administrator_start(message):

    sent = bot.send_message(message.chat.id, "Введите Id пользователя, с которым будете назначить администратором")
    bot.register_next_step_handler(sent, appoint_as_administrator_end)

def appoint_as_administrator_end(message):

    id_user = message.text

    try:
        rows = db_user_select_by_id(id_user =  id_user)

        bot.send_message(message.chat.id, "Проверяю пользователя " + rows[3])
        time.sleep(1)
        if rows[6] == 3 or rows[6] == None:
            db_user_upgrade(id_user = id_user, status = 2)
            bot.send_message(message.chat.id, "Назначаю пользователя " + rows[3] + " администратором.")
            time.sleep(1)
            bot.send_message(message.chat.id, "Права повышены!")
            try:
                bot.send_photo(rows[0], garold)
            except:
                bot.send_message(message.chat.id, "Возникла ошибка из-за которой вы не получите мем :(")
            bot.send_message(rows[0], "Поздравляем " + rows[3] +", вы назначены администратором! Введите 'Админ меню', чтобы открыть меню администратора.")
        else:
            bot.send_message(message.chat.id, "Данный пользователь уже администратор.")

    except:
        bot.send_message(message.chat.id, "Возникла ошибка. Возможно такого пользователя не существует или вы ввели неверный ID.\nПопробуйте ещё раз.")
        time.sleep(1)
        appoint_as_administrator_start(message)

#Понижение администратора
@bot.message_handler(func=lambda message: message.text == "Убрать администратора")

def downgrad_as_administrator_start(message):

    sent = bot.send_message(message.chat.id, "Введите Id пользователя, которого хотите убрать с поста администратора")
    bot.register_next_step_handler(sent, downgrad_as_administrator_end)

def downgrad_as_administrator_end(message):

    keyboard = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("Администратор", url='https://t.me/Danila877')
    keyboard.add(btn1)
    
    id_user = message.text
    
    try:
        rows = db_user_select_by_id(id_user = id_user)

        bot.send_message(message.chat.id, "Проверяю пользователя " + rows[3])
        time.sleep(1)
        if rows[6] == 2:
            db_user_upgrade(id_user = id_user, status = 3)
            bot.send_message(message.chat.id, "Понижаю пользователя  " + rows[3] + " .")
            time.sleep(1)
            bot.send_message(message.chat.id, "Права понижены!")
            try:
                bot.send_photo(rows[0], cotik_sad)
            except:
                bot.send_message(message.chat.id, "Возникла ошибка из-за которой вы не получите фото котика :(")
            bot.send_message(rows[0], "Уважаемый/ая " + rows[3] +", у вас забрали права администратора! Вы можете обратиться к разработчику для выяснения причин.")
            administrator_call(message)
        else:
            bot.send_message(message.chat.id, "Данный пользователь не администратор.")

    except:
        bot.send_message(message.chat.id, "Возникла ошибка. Возможно такого пользователя не существует или вы ввели неверный ID.\nПопробуйте ещё раз.")
        time.sleep(1)
        downgrad_as_administrator_start(message)


#Показать всех администраторов
@bot.message_handler(func=lambda message:message.text == "Показать всех администраторов")
def show_all_administrators(message):
    
    admin_list = []
    try:
        for i in db_all_admin_select():
            admin_list.append(i[3] + " " + i[7].lower() +  "\nID:" + str(i[0]) +'\n\n')
            admin_list.sort()

        bot.send_message(message.chat.id,"Администраторы:\n\n " + (''.join(admin_list)))
    except:
        bot.send_message(message.chat.id, "Администраторов нет.")


#Подключение и отключение рассылки
@bot.message_handler(func=lambda message: message.text == "Подключить рассылку" or message.text == "Отключить рассылку")
def user_newsletter_edit(message):

    if message.text == "Подключить рассылку":
        db_user_newsletter_edit(id_user = message.from_user.id, status = 1)
        keyboard_setting_submenu(message, text = "Обновляю данные")
        time.sleep(1)
        bot.send_message(message.chat.id, "Рассылка подключена!")
    else:
        db_user_newsletter_edit(id_user = message.from_user.id, status = 0)
        keyboard_setting_submenu(message, text = "Обновляю данные")
        time.sleep(1)
        bot.send_message(message.chat.id, "Рассылка отключена!")


#Вывод данных пользователя
@bot.message_handler(func=lambda message: message.text == "Показать мои данные")
def user_profile_slow(message):
    rows = db_user_select_by_id(message.from_user.id)

    if rows[4] == 0:
        newsletter_subscription = "Отключена"
    else:
        newsletter_subscription = "Подключена"

    bot.send_message(message.chat.id, "Ваш ID: " + "*"+str(rows[0])+"*" + "\n" + "Ваше имя: " + str(rows[1]) + "\n" + "Ваша фамилия: " + str(rows[2]) + "\n" + "Ваш никнейм: " + str(rows[3]) + "\n" + "Ваш статус: " + rows [7] + "\n" + "Подписка на рассылку: " + newsletter_subscription, parse_mode="Markdown")

#Пересылка различных сообщений пользователям
@bot.message_handler(func=lambda message: message.text == "Переслать сообщение")
def forward_message_start(message):

    rows = db_user_select_by_id(id_user =  message.from_user.id)

    if rows[6] == 2 or rows[6] == 1:
        sent = bot.send_message(message.chat.id, "Следующее сообщение будет отправлено пользовалям у которых подключена рассылка.\nВведите 'Отмена' если вы нажали кнопку по ошибке.")
        bot.register_next_step_handler(sent, forward_message_end)
    else:
        error(message = message)

def forward_message_end(message):

    rows = db_user_select_by_id(id_user =  message.from_user.id)
    users = db_user_select()

    if message.text == "Отмена" or message.text == "отмена":
        if rows[6] == 1 or rows [6] == 2:
            keyboard_admin(message)
        else:
            keyboard_user(message)
    else:
        bot.send_message(message.chat.id, "Пробую разослать сообщение пользователям..")
        try:
            for i in users:
                bot.forward_message(i[0], message.chat.id, message.message_id)
            bot.send_message(message.chat.id, "Сообщение успешно разослано.")
        except:
            bot.send_message(message.chat.id, "Возникла ошибка")


#Оставить отзыв
@bot.message_handler(func=lambda message: message.text == 'Оставить отзыв')
def review(message):

    sent = bot.send_message(message.chat.id, 'Напишите следующим сообщением свой отзыв.')
    bot.register_next_step_handler(sent, review_save)

def review_save(message):

    id_user = message.from_user.id
    user_text = message.text
    db_review_insert(id_user = id_user, text_review = user_text, looked_status = 0, date = date.today())
    bot.send_message(message.chat.id, 'Спасибо за ваш отзыв!')


#Показать отзывы
@bot.message_handler(func = lambda message: message.text == 'Показать отзывы')
def review_show(message):

    rows = db_user_select_by_id(message.from_user.id)

    if rows[6] == 1:
        review_list = []
        count = 0
        for i in db_review_select():
            count = count + 1
            review_list.append(str(count) + '. ' + i[2] + '\n' + 'Дата: ' + i[4] + '\n\n')
            db_review_update(id_review=i[0])
        if len(review_list) == 0:
            bot.send_message(message.chat.id, "Вы посмотрели все отзывы")
        else:
            bot.send_message(message.chat.id, (''.join(review_list)))
    else:
        error(message = message)


#Поиск запросов по периодам
@bot.message_handler(func = lambda message: message.text == "За всё время" or message.text == "За день" or message.text == "За месяц" or message.text == "За год")
def requests_by_date(message):

    requests_list = []

    rows = db_user_select_by_id(message.from_user.id)

    if rows[6] == 1 or rows [6] == 2:

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
            present_day = "'" + str(date.today()) + "'"
            row = len(db_requests_select_date(selected_date = present_day))
            if row == 0:
                bot.send_message(message.chat.id, "За выбранный период нет данных.\nПопробуйте позже.")
            else:
                for i in db_requests_select_date(selected_date = present_day):
                    try:
                        requests_list.append(i[0] + ' : ' + str(i[1]) + '\n')
                        requests_list.sort()
                    except:
                        error(message = message)
                bot.send_message(message.chat.id, (''.join(requests_list)))

        if message.text == "За месяц":
            present_month = "'"+year+'-0'+month+'-%'+"'"
            row = len(db_requests_select_date(selected_date = present_month))
            if row == 0:
                bot.send_message(message.chat.id, "За выбранный период нет данных.\nПопробуйте позже.")
            else:
                for i in db_requests_select_date(selected_date = present_month):
                    try:
                        requests_list.append(i[0] + ' : ' + str(i[1]) + '\n')
                        requests_list.sort()
                    except:
                        error(message=message)
                bot.send_message(message.chat.id, (''.join(requests_list)))

        if message.text == "За год":
            present_year = "'"+year+'-%-'+'%'+"'"
            row = len(db_requests_select_date(selected_date = present_year))
            if row == 0:
                bot.send_message(message.chat.id, "За выбранный период нет данных.\nПопробуйте позже.")
            else:
                for i in db_requests_select_date(selected_date = present_year):
                    try:
                        requests_list.append(i[0] + ' : ' + str(i[1]) + '\n')
                        requests_list.sort()
                    except:
                        error(message = message)
                bot.send_message(message.chat.id, (''.join(requests_list)))
    else:
        error(message = message)


#Поиск запросов по конкретному месяцу
@bot.message_handler(func=lambda message: message.text == 'Выбрать месяц')
def requests_select_date(message):

    rows = db_user_select_by_id(message.from_user.id)

    if rows[6] == 1 or rows [6] == 2:
        chat_id = message.chat.id
        sent = bot.send_message(chat_id, 'Введите месяц')
        bot.register_next_step_handler(sent, requests_select_date_show)
    else:
        error(message = message)

def requests_select_date_show(message):

    month = message.text
    requests_list = []
    present_month = "'"+year+'-'+Months[month]+'-%'+"'"
    row = len(db_requests_select_date(selected_date = present_month))
    if row == 0:
        bot.send_message(message.chat.id, "За выбранный период нет данных.\nПопробуйте позже.")
    else:
        for i in db_requests_select_date(daselected_datete1 = present_month):
            try:
                requests_list.append(i[0] + ' : ' + str(i[1]) + '\n')
                requests_list.sort()
            except:
                error(message = message)
        bot.send_message(message.chat.id, (''.join(requests_list)))


#Отчёт по запросам за выбранный период
@bot.message_handler(func=lambda message : message.text == 'Отчёт за период')
def request_select_date_between(message):
    rows = db_user_select_by_id(message.from_user.id)

    if rows[6] == 1 or rows [6] == 2:
        sent = bot.send_message(message.chat.id, "Введите начальную дату в формате '2022-01-01'")
        bot.register_next_step_handler(sent, date_between_start)
    else:
        error(message = message)

def date_between_start(message):
   sent = bot.send_message(message.chat.id, "Введите конечную дату в формате '2022-01-01'")
   start_date = message.text
   bot.register_next_step_handler(sent, date_between_end, start_date)

def date_between_end(message, start_date):
    final_date = message.text
    bot.send_message(message.chat.id, "Формирую отчёт...")
    time.sleep(1)
    start_date = "'" + start_date + "'"
    final_date = "'" + final_date + "'"
    requests_list = []
    if len(db_request_select_date_between(start_date = start_date, final_date = final_date)) == 0:
        bot.send_message(message.chat.id, "За выбранный период нет данных.\nПопробуйте позже.")
    else:
        try:
            for i in db_request_select_date_between(start_date = start_date, final_date = final_date):
                requests_list.append(i[0] + ' : ' + str(i[1]) + '\n')
                requests_list.sort()
            bot.send_message(message.chat.id, (''.join(requests_list)))
        except:
            error(message = message)


#Вставка события и его рассылка
@bot.message_handler(func=lambda message: message.text == "Создать событие")
def event_create_start(message):

    rows = db_user_select_by_id(message.from_user.id)

    if rows[6] == 1 or rows [6] == 2:

        keyboard = types.ReplyKeyboardMarkup(row_width = 1, resize_keyboard=True)
        btn = []
        btn1 = types.KeyboardButton(text = "Назад")
        for i in db_types_events():
            btn = types.KeyboardButton(text=i[0])
            keyboard.add(btn)
        keyboard.add(btn1)
        sent = bot.send_message(message.chat.id, "Выберите тип события.", reply_markup = keyboard)
        bot.register_next_step_handler(sent, date_event)
    else:
        error(message = message)

def date_event(message):

    rows =  [x[0] for x in db_types_events()]
    print(rows) 

    if message.text == "Назад":
        keyboard_admin(message)

    elif message.text in rows:
        type_event = message.text
        sent = bot.send_message(message.chat.id, "Введите дату декоративную.\nНапример '6 апреля'")
        bot.register_next_step_handler(sent, date_event_technical, type_event)

    else:
        bot.send_message(message.chat.id, "Вы ввели недопустимое значение, попробуйте ещё раз")
        time.sleep(1.5)
        event_create_start(message)

def date_event_technical (message, type_event):

    if message.text == "Назад":
        keyboard_admin(message)

    else:
        date_event = message.text
        date_event = date_event.title()

        result = re.match(r'(\b[0-9]\b (Января|Февраля|Марта|Апреля|Мая|Июня|Июля|Августа|Сентября|Октября|Ноября|Декарбря))|(\b[12][0-9]\b (Января|Февраля|Марта|Апреля|Мая|Июня|Июля|Августа|Сентября|Октября|Ноября|Декарбря))|(\b3[01]\b (Января|Февраля|Марта|Апреля|Мая|Июня|Июля|Августа|Сентября|Октября|Ноября|Декарбря))', date_event)

        if result == None:
            sent = bot.send_message(message.chat.id, "Вы ввели некорректную дату.\n Попробуйте ещё раз.")
            bot.register_next_step_handler(sent, date_event_technical, type_event)
            time.sleep (1.5)
            bot.send_message(message.chat.id, "Введите дату декоративную.\nНапример '6 апреля'")
        else:
            sent = bot.send_message(message.chat.id, "Введите техническую дату в формате '2022-01-01' после которой мероприятие будет не актуально.")
            bot.register_next_step_handler(sent, text_event, type_event, date_event)
    
def text_event(message, type_event, date_event):

    if message.text == "Назад":
        keyboard_admin(message)
    
    else:
        date_technical = message.text
        result = re.match(r'([12]\d\d\d)\-(0[1-9]|1[12])\-(0[1-9]|[12]\d|3[12])', date_technical)

        if result == None:
            sent = bot.send_message(message.chat.id, "Вы ввели недопустимую дату. Попробуйте ещё раз.")
            bot.register_next_step_handler(sent, text_event, type_event, date_event)
            time.sleep (1.5)
            bot.send_message(message.chat.id, "Введите техническую дату в формате '2022-01-01' после которой мероприятие будет не актуально.")
        else:
            sent = bot.send_message(message.chat.id, "Введите текст события")
            bot.register_next_step_handler(sent, event_preview, type_event, date_event, date_technical)

def event_preview(message, type_event, date_event, date_event_technical):

    text_event = message.text
    result = re.match(r'(\s+|^)[пПnрРp]?[3ЗзВBвПnпрРpPАaAаОoO0о]?[сСcCиИuUОoO0оАaAаыЫуУyтТT]?[Ппn][иИuUeEеЕ][зЗ3][ДдDd]\w*[\?\,\.\;\-]*|(\s+|^)[рРpPпПn]?[рРpPоОoO0аАaAзЗ3]?[оОoO0иИuUаАaAcCсСзЗ3тТTуУy]?[XxХх][уУy][йЙеЕeEeяЯ9юЮ]\w*[\?\,\.\;\-]*|(\s+|^)[бпПnБ6][лЛ][яЯ9]([дтДТDT]\w*)?[\?\,\.\;\-]*|(\s+|^)(([зЗоОoO03]?[аАaAтТT]?[ъЪ]?)|(\w+[оОOo0еЕeE]))?[еЕeEиИuUёЁ][бБ6пП]([аАaAиИuUуУy]\w*)?[\?\,\.\;\-]*', text_event)

    if result == None:
        bot.send_message(message.chat.id, "Предпросмотр события: ")
        time.sleep(1)
        bot.send_message(message.chat.id, "Тип события: " + type_event + '\nДата события: ' + date_event + '\nТекст события:\n' + text_event + '\nТехническая дата: ' + date_event_technical)
        time.sleep(1)
        sent = bot.send_message(message.chat.id, "Сохранить событие?", reply_markup=keyboard_yes_no(message))
        bot.register_next_step_handler(sent, save_event, type_event, date_event, text_event, date_event_technical)
    else:
        sent = bot.send_message(message.chat.id, "В вашем тексте обнаружен мат!\nВведите текст заново.")
        bot.register_next_step_handler(sent, event_preview, type_event, date_event, date_event_technical)
        time.sleep(1.5)
        bot.send_message(message.chat.id, "Введите текст события")

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
        event_create_start(message)
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
def event_show(message):

    count = 0
    for i in db_types_events():
        count = count + 1
        try:
            event = db_event_select_last(type_event = count)
            bot.send_message(message.chat.id, event[2] + " состоится " + event[6].lower() + " !\n" + event[1])
            time.sleep(0.5)
        except:
            pass


#Список песен
@bot.message_handler(func=lambda message: message.text == 'Список песен')
def list_of_songs(message):

    chat_id = message.chat.id
    list_song = []
    for i in db_song_select():
        list_song.append(i[1]+'\n')
        list_song.sort()
    bot.send_message(chat_id,'Вот доступный список песен:')
    time.sleep(1.5)
    bot.send_message(chat_id,(''.join(list_song)))


#Вывод песни
@bot.message_handler(func = lambda m: True)
def show_song(message):

    if message.text == '/start':
        bot.send_message(message.chat.id, 'Введите название песни а не команду.')
    else:
        chat_id = message.chat.id
        title_song = message.text
        title_song = title_song.lower().replace(" ", "")
        row = False
        for i in db_song_select():
            a = fuzz.WRatio(i[2], title_song)
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
