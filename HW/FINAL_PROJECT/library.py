import telebot
import config
import random
import flask
import re
import json
import sqlite3

# техническая часть раз

#conn = sqlite3.connect('books.db')
#c = conn.cursor()

telebot.apihelper.proxy = {'https': 'socks5h://geek:socks@t.geekclass.ru:7777'}
bot = telebot.TeleBot(token=config.token)
bot.remove_webhook()

# кастомная клавиатура для бота
def keyboard():
    markup = telebot.types.ReplyKeyboardMarkup()    
    markup.row('Полный список книг')
    markup.row('Поиск')
    markup.row('Взять книгу')
    markup.row('Вернуть книгу')
    markup.row('Рекомендация от бота')
    #markup.row('Справка')
    markup.row('Связаться с разработчиками')
    return markup

# код, получаемый из айди пользователя, декодится сайтом и в теории позволяет посылать пользователю сообщения с сайта
def make_pers_code(chat_id):
    x = chat_id
    n = '0123456789'
    l = 'abcdefghigklmnopqrstuvwxyz'
    L = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    code = ''.join(random.choices(l+L, k=random.randint(3, 7)))
    for i in x:
        code += i
        code += ''.join(random.choices(n, k=random.randint(2, 4)))
        code += ''.join(random.choices(l+L, k=random.randint(3, 7)))
    return code
    
# сам бот

# старт
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,
                     """Я - бот-библиотекарь Школы Лингвистики.
ВНИМАНИЕ: если я вам не отвечаю, загляните в мое описание!
краткое описание функций: /help
                     Внимание:
я пока не умею реагировать на отредактированные сообщения
""",
                     reply_markup=keyboard())

# справка по возможностям бота
@bot.message_handler(commands=['help'])
def help(message):
    text = """С помощью этого бота можно пользоваться Библиотекой Школы Лингвистики.
ВНИМАНИЕ: если я вам не отвечаю, загляните в мое описание!
- полный список книг
- поиск по названию, автору и т.п.
- взять книгу
- вернуть книгу
- проверить, какие книги у вас на руках: /check
- связаться с разроботчиками (по поводу любых неисправностей)
- рекомендация 'что почитать?'"""
    bot.send_message(message.chat.id, text, reply_markup=keyboard())

# проверить книги на руках
@bot.message_handler(commands=['check'])
def check(message):
    conn = sqlite3.connect('books.db')
    c = conn.cursor()
    
    owner = ('@' + message.from_user.username, )
    my_books = []
    for row in c.execute('SELECT * FROM all_books WHERE owner=? ORDER BY bookid', owner):
        book_info = "{}. автор(ы): {} (id: {})".format(row[1], row[2], row[0])
        my_books.append(book_info)
    conn.close()
    
    text = 'Сейчас у вас на руках {} книг(и)'.format(len(my_books))
    for book in my_books:
        text += '\n - {}'.format(book)
    bot.send_message(message.chat.id, text, reply_markup=keyboard())

# системная команда для добавления одмина
@bot.message_handler(commands=['dobavit_admina'])
def add_adm(message):
    admin = '@' + message.text.replace('dobavit_admina', '').strip()
    with open('admins.json', 'w', encoding='utf-8') as j:
        data = j.read()
        admins = json.loads(data)
        if admin not in admins.keys():
            admins[admin] = '@' + message.from_user.username
            j.write(json.dumps(admins))
            bot.send_message(message.chat.id, '{} теперь является админом (добавлен_а by {})'.format(admin, admins[admin]),
                             reply_markup=keyboard())
        else:
            bot.send_message(message.chat.id, '{} уже является админом (добавлен_а by {})'.format(admin, admins[admin]),
                             reply_markup=keyboard())

# что еще сделать?
# admin_help - список системных комманд для администраторов
# sys_help <command> - инструкция по использованию системной командой
# указать контакты Библиотекарей в описании


# системная команда для добаления книг в БД через бота, надо подключить проверку на одмина
@bot.message_handler(commands=['add_book'])
def add_book(message):
    name = '@' + message.from_user.username
    with open('admins.json', 'w', encoding='utf-8') as j:
        data = j.read()
    admins = json.loads(data)
    if admin in admins.keys():
        info = message.text.replace('/add_book\n')
        try:
            bookid = re.search('id: ([0-9]+?)\n', info)
            name = re.search('name: (.+?)\n', info)
            author = re.search('author: (.+?)\n', info)
            year = re.search('year: ([0-9]+?)$', info)

            full_info = (bookid.group(1), name.group(1), author.group(1), int(year.group(1)))
            
            conn = sqlite3.connect('books.db')
            c = conn.cursor()
            c.execute("INSERT INTO all_books VALUES (?,?,?,?)", full_info)
            conn.commit()
            conn.close()
            
            bot.send_message(message.chat.id, 'книга добавлена')
        except:
            bot.send_message(message.chat.id, 'кажется что-то пошло не так')
    else:
        bot.send_message(message.chat.id, 'У вас нет прав на добавление новых книг. Обратитесь к администратору библиотеки.')

# просто ссылка на сайт, см. его код
@bot.message_handler(regexp="Полный список книг")
def list_books(message):
    button = telebot.types.InlineKeyboardMarkup()
    url_button = telebot.types.InlineKeyboardButton(text="Полный список книг", url="https://linguistics-library.herokuapp.com/") 
    button.add(url_button)
    bot.send_message(message.chat.id, "Вся библиотека доступна по ссылке", reply_markup=button)
    bot.send_message(message.chat.id, 'Чем еще могу быть полезен?', reply_markup=keyboard())

# просто кидает мой ТГ
@bot.message_handler(regexp="Связаться с разработчиками")
def contact(message):
    text = "По любым вопросам писать сюда: @Polyana_A"
    bot.send_message(message.chat.id, text, reply_markup=keyboard())

# случайная книга из всей БД
@bot.message_handler(regexp="Рекомендация от бота")
def recommend(message):
    books = ['Читайте Пушкина', 'Почитайте свое резюме :)', 'Лучше почитайте свой курсач/диплом/диссер :)']
    
    conn = sqlite3.connect('books.db')
    c = conn.cursor()
    for row in c.execute('SELECT * FROM all_books ORDER BY bookid'):
        book_info = "{}. автор(ы): {} (id: {})".format(row[1], row[2], row[0])
        books.append(book_info)
    conn.close()
    
    bot.send_message(message.chat.id, random.choice(books), reply_markup=keyboard())

# ссылка на поиск (функционирует на сайте)
@bot.message_handler(regexp="Поиск")
def search(message):
    button = telebot.types.InlineKeyboardMarkup()
    url_button = telebot.types.InlineKeyboardButton(text="Поиск по Библиотеке", url="https://linguistics-library.herokuapp.com/search")
    button.add(url_button)
    bot.send_message(message.chat.id, "Поиск откроется после нажатия кнопки", reply_markup=button)
    bot.send_message(message.chat.id, 'Чем еще могу быть полезен?', reply_markup=keyboard())

# активизирует возможность вернуть книгу
@bot.message_handler(regexp="[a-z]{2}[0-9][A-Z]{2}[0-9]{5}[a-z]{2}[0-9]{3}$")
def return_book(message):
    markup = telebot.types.ForceReply(selective=False)
    try:
        if message.reply_to_message.text == 'Скопируйте и отправьте мне код подтверждения':
            text = "Пожалуйста, оправьте ID книги, которую вы хотите вернуть" # в формате 'вернуть: XXXXX'
            bot.send_message(message.chat.id, "Авторизация пройдена!")
            bot.send_message(message.chat.id, text, reply_markup=markup)
        else:
            bot.send_message(message.chat.id, "Вы пытаетесь меня обмануть! Я вас запомнил, {}".format(
                message.from_user.username), reply_markup=keyboard())
    except:
        bot.send_message(message.chat.id, "Не надо пропускать шаги! Я вас запомнил, {}".format(
            message.from_user.username), reply_markup=keyboard())

# позволяет взять или вернуть книгу
@bot.message_handler(regexp="[0-9]{4}")
def manage_book(message):
    conn = sqlite3.connect('books.db')
    c = conn.cursor()
    
    user = '@' + message.from_user.username

    bookid = (str(message.text.strip()), )
        
    c.execute("SELECT * FROM all_books WHERE bookid=?", bookid)
    resp = c.fetchone()
    owner = str(resp[4])
    #bot.send_message(message.chat.id, str(owner[4]))
    try:        
        if message.reply_to_message.text == 'Пожалуйста, оправьте ID книги, которую вы хотите взять':
            if owner == 'None':
                
                conn = sqlite3.connect('books.db')
                c = conn.cursor()
                data = (user, str(message.text.strip()))
                c.execute("UPDATE all_books SET owner=? WHERE bookid=?", data)
                conn.commit()
                conn.close()
                bot.send_message(message.chat.id,
                             "{} взял_а книгу {}".format(user, message.text),
                             reply_markup=keyboard())
            else:
                bot.send_message(message.chat.id,
                             "Простите, но {} уже взял_а книгу {}".format(owner, message.text),
                             reply_markup=keyboard())
                
        elif message.reply_to_message.text == 'Пожалуйста, оправьте ID книги, которую вы хотите вернуть':
            if user == owner:
                
                conn = sqlite3.connect('books.db')
                c = conn.cursor()
                data = (None, str(message.text.strip()))
                c.execute("UPDATE all_books SET owner=? WHERE bookid=?", data)
                conn.commit()
                conn.close()
                
                bot.send_message(message.chat.id,
                             "{} вернул_а книгу {}".format(user, message.text),
                             reply_markup=keyboard())
            elif owner == 'None':
                bot.send_message(message.chat.id,
                                 "Кажется, вы еще не взяли эту книгу, а уже пытаетесь вернуть! Не надо так, я вас запомнил, {}".format(user),
                             reply_markup=keyboard())
            else:
                bot.send_message(message.chat.id,
                                 "Простите, но книгу, которую вы пытаетесь вернуть, брал другой пользователь ({}), а не вы.".format(owner),
                             reply_markup=keyboard())
    except:
        bot.send_message(message.chat.id,
                     "Кажется, вы не выбрали, что хотите сделать с этой книгой!",
                     reply_markup=keyboard())

# активирует возможность взять книгу
@bot.message_handler(regexp="Взять книгу")
def borrow(message):
    markup = telebot.types.ForceReply(selective=False)
    text = "Пожалуйста, оправьте ID книги, которую вы хотите взять" # в формате 'взять: XXXXX'
    bot.send_message(message.chat.id, text, reply_markup=markup)

# запускает процес т.н. авторизации, т.е. не отсканировав физический код невозможно вернуть книгу
@bot.message_handler(regexp="Вернуть книгу")
def return_instruction(message):
    markup = telebot.types.ReplyKeyboardRemove(selective=False)
    pers_code = make_pers_code(str(message.chat.id))

    button = telebot.types.InlineKeyboardMarkup()
    url_button = telebot.types.InlineKeyboardButton(text="скопируйте код и вставьте, перейдя по этой ссылке", url="https://linguistics-library.herokuapp.com/{}".format(config.url))
    button.add(url_button)
    
    bot.send_message(message.chat.id, "Пожалуйста, отсканируйте QR-код из Библиотеки и следуйте инструкциям на сайте.", reply_markup=markup)
    bot.send_message(message.chat.id, "Ваш код авторизации:", reply_markup=markup)
    bot.send_message(message.chat.id, " *{}*".format(pers_code), parse_mode="Markdown", reply_markup=button)
    markup_force = telebot.types.ForceReply(selective=False)
    bot.send_message(message.chat.id, "Скопируйте и отправьте мне код подтверждения", reply_markup=markup_force)

# отлавливает дураков            
@bot.message_handler(content_types=['audio', 'document', 'photo', 'sticker', 'video',
                                    'video_note', 'voice', 'location', 'contact',
                                    'new_chat_members', 'left_chat_member',
                                    'new_chat_title', 'new_chat_photo',
                                    'delete_chat_photo', 'group_chat_created',
                                    'supergroup_chat_created', 'channel_chat_created',
                                    'migrate_to_chat_id', 'migrate_from_chat_id', 'pinned_message'])
def send_error(message):
    bot.send_message(message.chat.id, 'Простите, я понимаю только известные мне команды.',
                     reply_markup=keyboard())

# техническая часть два
if __name__ == '__main__':
    bot.polling(none_stop=True)
