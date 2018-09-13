import re
import random
from collections import Counter

# программа извлекает из текста все слова и приводит их к нижнему регистру
def clear_text():
    with open('mishkina_kasha.txt', encoding='utf-8') as f:
        text = f.read()
    text = re.sub('[^а-яёА-ЯЁ-]',' ',text)
    text = re.sub('\s+',' ',text)
    text = text.lower()
    print('Загружен текст "Мишкина каша", автор: Николай Носков.')
    return text

# создается список из всех слов текста
def create_wordlist(text):
    word_list = text.split(' ')
    return word_list

# создается словарь,ключи - слова с частотностью больше 3, значение - частотность
def count_words(word_list):
    words_counted = Counter(sorted(word_list))
    c1=words_counted.copy()
    for key,value in c1.items():
        if value < 3:
            del words_counted[key]
    print('Загружен список слов с частотностью больше 3.')
    return words_counted

# программа запрашивает у пользователя длину и первую букву слова
# если введенные данные не соответствуют условию, программа сообщает об этом
# и запрашивает данные заново
def get_request():
    l = input('Слово какой длины вы ищете? ')
    x = False
    while x == False:
        try:
            int(l)
            x = True
        except ValueError:
            l = input('Введенные вами данные не соответствуют условию! Слово какой длины вы ищете? ')
            x = False
    letter = input('С какой буквы слово должно начинаться? ')
    while letter == '' or re.match('[^а-яё]',letter):
        letter = input('Это не буква кириллического алфавита! С какой буквы слово должно начинаться? ') 
    letter = letter.lower()
    return l,letter

# сосдается список из всех слов, соответствующих запросу ппользователя.
# если таких слов нет, возращается сообщение, что ничего не найдено
def find_word(words_counted,x):
    all_words_found = []
    length, letter = x
    for key in words_counted.keys():
        if len(key) == int(length) and key[0] == letter:
            all_words_found.append(key)
    if len(all_words_found) == 0:
        all_words_found.append('не найдено :(')
    return all_words_found

# программа выбирает случайное слово из списка
# и выводит его на экран
# если ни одного слово не найдено, список состоит из одного элемента "не найдено"
# и программа выводит именно его
def random_word(all_words_found):
    res = random.choice(all_words_found)
    print('Слово:', res)

# программа предлагает найти еще одно слово в том же тексте
def main():
    word_counted = count_words(create_wordlist(clear_text()))
    again = 'да'
    while again == 'да':
        request = get_request()
        result = random_word(find_word(word_counted,request))
        again = input('Хотите найти еще одно слово?(да/нет)')

if __name__ == "__main__":
    main()
