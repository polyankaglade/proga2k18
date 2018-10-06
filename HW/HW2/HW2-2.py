import json
import urllib.request
from collections import Counter
import operator

# функция спрашивает у пользователя, каким списком юзеров он хочет пользоваться:
# предустановленным или своим собственным
# и возвращает этот список
def get_userlist():
    print('Какой список пользователей вы хотите использовать?\n1) Предустановленный список из 20 пользователей\n2) Свой список')
    answer = str(input('Введите номер выбранного варианта: '))
    while answer != '1' and answer != '2':
        print('Введенные данные не соответствуют условию! Попробуйте еще раз.')
        answer = str(input('Введите номер выбранного действия: '))
    if answer == '1':
        userlist = 'elmiram, maryszmary, lizaku, nevmenandr, ancatmara, roctbb, akutuzov, agricolamz, lehkost, kylepjohnson, mikekestemont, demidovakatya, shwars, JelteF, timgraham, arogozhnikov, jasny, bcongdon, whyisjake, gvanrossum'.split(', ')
    elif answer == '2':
        userlist = str(input('Введите имена пользовтелей гитхаба через запятую с пробелом: ')).split(', ')
    return userlist            

# программа предлагает пользователю выбрать интересующего его юзера
def choose_user(userlist):
    print('Загружен следующий список пользователей:')
    for username in userlist:
        print(username)
    user = input('Введите имя интересующего вас пользователя: ')
    while user not in userlist:
        print('Указанного пользователя нет в списке. Попробуйте еще раз.')
        user = input('Введите имя интересующего вас пользователя: ')
    return user

# инструмент: функция для отправки запроса на сервер гитхаба
# возвращает данные о репозиториях юзера
def get_data(user, token):
    url = 'https://api.github.com/users/%s/repos?access_token=%s' % (user, token)  
    response = urllib.request.urlopen(url)
    text = response.read().decode('utf-8')
    data = json.loads(text)
    return data


# инструмент: функция для добавления значений к существующим ключам словаря        
def add_to_dict(key,value,myDict):
    if not key in myDict:
        myDict[key] = [value]
    else:
        myDict[key].append(value)
    
# функция выводит названия и описания всех репозиториев юзера
def get_repos(data, user):
    print('У пользователя', user, 'есть следующие репозитории:')
    for i in data:
        print('    ' + str(i['name']) + ': '+ str(i['description']))

# фунция выводит список языков, на которых пишет юзер,
# а также в каких репозиториях используется каждый из языков
def get_lang(data, user):
    languages = {}
    for i in data:
        language = str(i['language'])
        name = str(i['name'])
        if language != '' and language != 'None':
            add_to_dict(language,name,languages)
    print('Пользователь пишет на языках', end=' ')
    print(*languages, sep=', ', end='.\n')
    for key,values in languages.items():
        print('Язык', key, 'используется в репозитории(ях)', end=' ')
        print(*values, sep=', ', end='.\n')

# инструмент: функция принимает словарь вида {предмет: частота}
# и возращает список предметов с максимальной частотой
def count_most_common(c):
    # из отсортированного по значением словаря берется значение последнего ключа (т.е. максимальное значение)
    most_common_score = str(sorted(c.items(), key=operator.itemgetter(1))[-1][1])
    flipped = {} # "обратный" словарь вида частота: предметы
    for key,value in c.items():
        add_to_dict(str(value),key,flipped)
    result = flipped[most_common_score]
    return result

# подсчет у кого из пользователей в списке больше всего репозиториев
def count_repos(userlist, token):
    all_repos = {} # словарь вида юзер: кол-во репозиториев
    for user in userlist:
        data = get_data(user, token)
        all_repos.update({user: len(data)})
    result = count_most_common(all_repos)
    print('Среди пользователей списка больше всего репозиториев у',end=' ')
    print(*result,sep=', ', end='.\n')
    # да, он выдает 30 как максимум, я не смогла самостоятельно обойти ограничение
    # я конечно почитала все, что написано в документации, но оно слишком сложное
    # https://developer.github.com/v3/guides/traversing-with-pagination/

# подсчет какой язык самый популярный среди пользователей списка
# самым популярным считается язык, который используется у большинства юзеров хотя бы один раз
# я писала в ТГ почему это более логично, чем предложенный там же вариант
# (инструкция допускает обе интерпритации)
def count_langs(userlist, token):
    all_langs = [] #список из всех языков всех пользователей
    for user in userlist:
        data = get_data(user, token)
        languages = [] # все языки пользователя по одному разу
        for i in data:
            language = str(i['language'])
            if language != '' and language != 'None' and language not in languages:
                languages.append(language)
        all_langs = all_langs + languages
    c = dict(Counter(all_langs)) # словарь вида язык: кол-во пользователей, которые им пользуются
    result = count_most_common(c)
    print('Среди пользователей списка наиболее популярен(ы) язык(и)',end=' ')
    print(*result,sep=', ', end='.\n')

# подсчет у кого из пользователей списка больше всего подписчиков
def count_followers(userlist, token):
    all_followers = {} # словарь вида юзер: кол-во подписчиков
    for user in userlist:
        url = 'https://api.github.com/users/%s/followers?access_token=%s' % (user, token)  
        response = urllib.request.urlopen(url)
        text = response.read().decode('utf-8')
        data = json.loads(text)
        all_followers.update({user: len(data)})
    result = count_most_common(all_followers)
    print('Среди пользователей списка больше всего подписчиков у',end=' ')
    print(*result,sep=', ', end='.\n')
        

def main():
# Блок 1: технический
    print('ВНИМАНИЕ! Программе нужен ваш токен!')
    print('Откройте код и скопируйте свой токен туда, где написано "ВСТАВЬТЕ СВОЙ ТОКЕН СЮДА"')
    token = 'your_token' # ВСТАВЬТЕ СВОЙ ТОКЕН СЮДА
    userlist = get_userlist() # список юзеров: от пользователя или предустановленный
# Блок 2: работа с одним, выбранным из списка юзером
    user1 = choose_user(userlist) # пользователь выбирает юзера
    user1_data = get_data(user1, token) # данные о репозиториях выбранного юзера
    get_repos(user1_data, user1) # названия и описания репозиториев
    get_lang(user1_data, user1) # список языков и репозитории, где они используются
    print('\n')
# Блок 3: работа со всеми юзерами из списка
    count_repos(userlist, token) # подсчет у кого из пользователей в списке больше всего репозиториев
    print('\n')
    count_langs(userlist, token) # подсчет какой язык самый популярный среди пользователей списка
    print('\n')
    count_followers(userlist, token) # подсчет у кого из пользователей списка больше всего фолловеров

if __name__ == '__main__':
    main()
