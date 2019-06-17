import re
import random
import config
from flask import Flask
from flask import url_for, render_template, request, redirect
import sqlite3

#conn = sqlite3.connect('books.db')
#c = conn.cursor()

def make_key():
    n = '0123456789'
    l = 'abcdefghigklmnopqrstuvwxyz'
    L = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    key = ''.join(random.choices(l, k=2))
    key += ''.join(random.choices(n, k=1))
    key += ''.join(random.choices(L, k=2))
    key += ''.join(random.choices(n, k=5))
    key += ''.join(random.choices(l, k=2))
    key += ''.join(random.choices(n, k=3))
    return key

def decode_pers_code(pers_code):
    all_numbers = re.findall('[a-zA-Z]([0-9])', pers_code)
    chat_id = ''.join(all_numbers)
    return chat_id

app = Flask(__name__)

@app.route('/')
def index():
    conn = sqlite3.connect('books.db')
    c = conn.cursor()
    c.execute("SELECT * FROM all_books")
    all_table = c.fetchall()
    conn.close()
    return render_template('content_table.html', title='Полный список книг', all_table=all_table)

@app.route('/{}'.format(config.url))
def code():
    return render_template('index.html', title='Авторизация')

# страница поиска
@app.route('/search')
def search_page():
    return render_template('search.html', title='Поиск')


# сам поиск
def get_results(search_values):
    results = []
    conn = sqlite3.connect('books.db')
    c = conn.cursor()
    c.execute("SELECT * FROM all_books")
    all_table = c.fetchall()
    conn.close()
    if len(results) == 0:
        results = ['Нет результатов с такими параметрами - попробуйте другие.']
    return results

# сбор параметров поиска от пользователя
# и страница результатов
@app.route('/results')
def results():
    search_values = []
    parameters = ['age', 'lang1', 'born', 'habit', 'ling']
    for i in parameters:
        if request.args[i] == '':
            continue
        else:
            value = request.args[i]
        search_values.append(value.lower())

    results = get_results(search_values)
    return render_template('results.html', title='Результаты поиска',
                           results=results)

    
@app.route('/technical', methods=['POST'])
def tech():
    key = make_key()
    pers_code = str(request.form['code'])
    chat_id = decode_pers_code(pers_code)
    url_send = 'https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={text}'.format(
        token=config.token, chat_id = chat_id, text = key)
    return """
<html>
<body>
<p>Код подтврждения: <b>{}</b></p>
<p>Скопируйте этот код и отправьте обратно боту.</p>
</body>
</html>
""".format(key)


    
@app.route('/reawaken')
def reawaken():
    return """
<html>
<meta http-equiv="refresh" content="3; url="https://linguistics-library.herokuapp.com/">
<body>
<p>Я проснулся! Сейчас отвечу.</p>
</body>
</html>
"""


if __name__ == '__main__':
    import os
    app.debug = True
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
