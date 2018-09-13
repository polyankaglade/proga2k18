import re
import random

# приветствие, описание правил и прощание прописаны в функции main()

# пользователь выбирает одну из трех предложенных тем
# программа будет запрашивать ответ, пока пользователь не введет 1, 2 или 3
def choose_theme():
    print('Выберите одну из трех тем:')
    print('1) сыры\n2) столярные инструменты\n3) лингвистические термины')
    theme = str(input('Введите номер выбранной темы (цифрой): '))
    while theme != '1' and theme != '2' and theme != '3':
        print('Это не цифра от 1 до 3! Попробуйте еще раз.')
        theme = str(input('Введите номер выбранной темы (числом): '))
    return theme

# программа открывает файл со словами
# и выводит небольшой комментарий о выбранной теме
def make_word_list(theme):
    if theme == '1':
        with open('cheese.txt',encoding='utf-8') as f:
            word_list = f.read()
        word_list = word_list.replace('\ufeff','')
        word_list = word_list.split('\n')
        print('Загадано название сорта сыра.')
        return word_list
    elif theme == '2':
        with open('instruments.txt',encoding='utf-8') as f:
            word_list = f.read()
        word_list = word_list.replace('\ufeff','')
        word_list = word_list.split('\n')
        print('Загадано название столярного инструмента.')
        return word_list
    elif theme == '3':
        with open('termins.txt',encoding='utf-8') as f:
            word_list = f.read()
        word_list = word_list.replace('\ufeff','')
        word_list = word_list.split('\n')
        print('Загадан лингвистический термин.')
        return word_list

# программа выбирает случайное слово из списка
def random_word(word_list):
    x = len(word_list) -1 
    i = random.randint(0,x)
    word = word_list[i]
    return word

# программа открывает текстовый файл с рисунками виселицы
def hanger():
    with open('pictures.txt', encoding='utf-8') as f:
        picture = f.read()
    picture = picture.replace('\ufeff','')
    picture = picture.split(';')
    return picture

# сама игра
def game(word,picture):
    popytok = 16
    l = len(word)
    print('Отгадайте слово из',l,'букв.')
    # программа создает маску из символов "_"
    show_mask = str('_' * l) 
    print(show_mask)
    mask = list(show_mask)
    # программа сообщает изначально количество попыток
    print('У вас 16 попыток.') 
    all_guesses = []
    # программа запрашивает букву кириллического алфавита.
    # если пользователь вводит что-либо кроме допустимых символов
    # илли букву, которой нет в слове,
    # программа сообщает об этом и вычитает 1 попытку
    while popytok > -1:
        guess = str(input('Введите букву (кириллица): '))
        guess = guess.lower()
        if guess == '' or re.match('[^а-яё]',guess):
            print('Это не буква кириллицы!')
            popytok -= 1
        elif guess in all_guesses:
            print('Вы уже называли такую букву!')
            popytok -= 1
        elif guess not in word:            
            print('Упс, такой бкувы нет в этом слове.')
            popytok -= 1
        else:
            print('\n')
            n= -1 
            for letter in word:
                n += 1
                if guess == letter:
                    mask[n] = guess
                    show_mask = ''.join(mask)
        # список всех уже введенных букв
        all_guesses.append(guess)
        # программа рисует виселицу
        print(picture[popytok])
        # программа показывает маску слова с угаданными буквами (капсом)
        print(show_mask.upper())
        # программа завершает работу если пользователь угадал слово
        if show_mask == word:
            print('Поздравляю! Вы отгадали слово!')
            break
        # программа склоняет слово "попытка"
        if popytok > 4:
            print('У вас осталось',popytok,'попыток.')
        if 5 > popytok > 1:
            print('У вас осталось',popytok,'попытки.')
        if popytok == 1:
            print('У вас осталось',popytok,'попытка.')
        # программа завершает работу если пользователь истратил все попытки
        if popytok == 0:
            print('У вас не осталось попыток.')
            print('Вы проиграли :(')
            break
        
    
def main():
    # приветствие и правила игры
    print('''
Это игра "Виселица".
Правила: я загадываю слово, вы отгадываете его по буквам.
За каждую неправильно отгаданную букву у вас сгорает одна попытка
и появляется новая деталь на рисунке с виселицей.
Угадываете слово - висельник остается жить,
не угадываете - он умирает, а вы проигрываете.
Начнем!\n''')
    # программа предлагает сыграть заново
    again = 'да'
    while again == 'да':
        game(random_word(make_word_list(choose_theme())),hanger())
        again = input('\nХотите сыграть еще раз?(да/нет)')
    # прощание
    print('\nСпасибо за игру!')

if __name__ == "__main__":
    main()
