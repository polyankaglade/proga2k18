# на моем компьютере запуск этого скрипта из IDLE
# вызывает ошибку io.UnsupportedOperation: fileno
# если верить гуглу, единственное решение - запускать из cmd

import json
import csv
from collections import Counter
from datetime import datetime
from flask import Flask
from flask import url_for, render_template, request, redirect

app = Flask(__name__)
output_file = 'results.csv'
fields = ['name', 'age', 'lang1', 'born',
          'habit', 'ling', 'edu', 'answers']

# создает файл для записи результатов,
# если его не было до этого
try:
    file = open(output_file)
except IOError as e:
    with open(output_file, 'w', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(
                csvfile, delimiter='\t',
                fieldnames=fields)
            writer.writeheader()


# главная страница с анкетой
@app.route('/')
def main_anketa():
    return render_template('index.html', title='Главная')


# запись в csv таблицу + страница "спасибо"
@app.route('/thank_you', methods=['POST'])
def write_res():
    name = request.form['name']
    age = request.form['age']
    lang1 = request.form['lang1']
    born = request.form['born']
    habit = request.form['habit']
    edu = request.form['edu']
    ling = 'да' if 'ling' in request.form else 'нет'
    answers = request.form.getlist('answers')
    for i in range(len(answers)):
        answers[i] = answers[i].lower()
    answers = ', '.join(answers)
    with open(output_file, 'a', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(
            csvfile, delimiter='\t',
            fieldnames=fields)
        writer.writerow({'name': name, 'age': age, 'lang1': lang1.lower(),
                         'born': born.lower(), 'habit': habit.lower(),
                         'ling': ling, 'edu':  edu,
                         'answers':  answers})
    return render_template('thanks.html', title='Ответ записан')


# страница поиска
@app.route('/search')
def search_page():
    return render_template('search.html', title='Поиск')


# сам поиск
def get_results(search_values, edu):
    results = []
    with open(output_file, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(
            csvfile, delimiter='\t',
            fieldnames=fields)
        for row in reader:
            x = 0
            y = 0
            row = list(row.values())
            for i in range(1, 6):
                if search_values[i-1] == 'любой':
                    x = 1
                elif row[i] == search_values[i-1]:
                    x = 1
                else:
                    x = 0
                    break
            if edu[0] == 'любой' or row[6] in edu:
                y = 1
            else:
                y = 0

            if row == fields:
                x = 0
                y = 0

            if x == 1 and y == 1:
                results.append(' - '.join(row))
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
            value = 'любой'
        else:
            value = request.args[i]
        search_values.append(value.lower())

    if len(request.args.getlist('edu')) == 4:
        edu = ['любой']
    else:
        edu = request.args.getlist('edu')

    results = get_results(search_values, edu)
    return render_template('results.html', title='Результаты поиска',
                           age=search_values[0], lang1=search_values[1],
                           born=search_values[2].title(),
                           habit=search_values[3].title(),
                           ling=search_values[4], edu=edu,
                           results=results)


# страница с данными в формате json
@app.route('/json')
def make_json():
    all_json = {}
    index = 0
    with open(output_file, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(
            csvfile, delimiter='\t',
            fieldnames=fields)
        for row in reader:
            if row['age'] in fields:
                continue
            index += 1
            all_json[index] = json.loads(json.dumps(row))
    return render_template('json.html', title='JSON',
                           data=all_json)


# очень простая статистика
@app.route('/stats')
def get_stats():
    today = datetime.today()
    date = today.strftime("%m.%d.%Y")
    langs = []
    ages = []
    borns = []
    habits = []
    lings = []
    edus = []
    index = 0
    with open(output_file, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(
            csvfile, delimiter='\t',
            fieldnames=fields)
        for row in reader:
            if row['age'] in fields:
                continue
            index += 1
            langs.append(row['lang1'])
            ages.append(row['age'])
            borns.append(row['born'])
            habits.append(row['habit'])
            lings.append(row['ling'])
            edus.append(row['edu'])
    return render_template('stats.html', title='Статистика',
                           date=date,
                           corpus_volume=index,
                           min_age=min(ages),
                           max_age=max(ages),
                           langs=Counter(langs).most_common(3),
                           borns=Counter(borns).most_common(5),
                           habits=Counter(habits).most_common(5),
                           lings=dict(Counter(lings)),
                           edus=dict(Counter(edus)))


# как я говорила выше, не робит, только через cmd
if __name__ == '__main__':
    app.run(debug=True)
