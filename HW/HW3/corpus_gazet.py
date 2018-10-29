import re
import os
import urllib.request
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup

# приветствие и настройка объема корпуса
def hello(start_link):
    print('Эта программа скачивает статьи с сайта %s' % start_link)
    print('Объем по умолчанию - 100 тыс. слов.')
    print('Если вы хотите изменить объем полученного корпуса, введите необходимое число слов.')
    print('Если хотите оставить объем по умолчанию, просто нажмите Enter.')
    answ = input('кол-во слов / Enter: ')
    x = False
    # это небольшой эксперимент по проверке инпута, обычно я делаю не так и короче
    while x == False:
        if len(answ) > 0:
            x = False
        else:
            max_words = 100000
            x = True
        try:
            max_words = float(answ)
            x = True
        except ValueError:
            print('Вы ввели что-то не то. Попробуйте еще раз.')
            x = False
            answ = input('кол-во слов / Enter: ')
    return max_words    

# фунция для открытия ссылок
def open_link(link):
    try:
        req = Request(link, headers={'User-Agent': 'Mozilla/5.0'})
        #connect to that page
        f = urlopen(req)
    except urllib.error.HTTPError:
        print('An Error occured')
        print(link)
    else:
        #read it all in
        myfile = f.read()
        #build a document model
        soup = BeautifulSoup(myfile,'html.parser')
    return soup

# собирает список ссылок на все статьи газеты
def get_all_links(start_link):
    all_links = []
    link = start_link + '/archive'
    # открывает страницу архива газеты
    soup = str(open_link(link))
    print('страница архива скачана')
    # ищет все ссылки на дни, в которые что-либо публиковалось
    archive_days = re.findall('<td class="day.*?"><a href="(.+?)">',soup)
    total_days = len(archive_days)
    print('Всего дней:', total_days)
    for n,day in enumerate(archive_days[0:5]):
        # собирает ссылку на архив за определенный день
        day_link = start_link + str(day)
        # открывает архив за этот день
        day_soup = open_link(day_link)
        # вырезает блок основного контента
        article_links = day_soup.findAll(id='content')
        article_links = str(article_links[0])
        # ищет все ссылки на собственно статьи
        article_links = re.findall('field-content"><a href="(.+?)">',
                                   article_links)
        print('страница %d из %d обработана' % (n,total_days)) # для визуализации процесса
        # добавляет все ссылки в общий список
        for article_link in article_links: 
            all_links.append(article_link)
    return all_links

# достает все нужную информацию со страницы
def get_article(link):
    # у каждой газеты на сайте есть индивидуальный индекс
    # он впоследствии и используется в кач-ве названия файла
    index = re.search('-(\d+)$',link)
    index = str(index.group(1))
    # открывает статью по ссылке
    soup = open_link(link)
    # находит заголовок
    title = soup.findAll(id='page-title')
    title_clean = title[0].get_text()
    # находит категорию статьи (все статьи этой газеты размечены)
    category = soup.findAll(attrs={"class" : "breadcrumb"})
    category = str(category[0])
    category_clean = re.search('›.*>([а-яА-ЯёЁ]+?)<',category)
    category_clean = category_clean.group(1)
    # находит время публикации
    time = soup.findAll(
        attrs={"class" : "field field-name-field-article-date field-type-date field-label-hidden"})
    time = time[0].get_text()
    # оставляет только дд.мм.гггг
    time_clean = re.search(
        '(\d{2})\.(\d{2})\.(\d{4})',time) # отделяет месяц и год
    time_general = time_clean.group()
    # определяет год
    year = time_clean.group(3)
    # определяет месяц
    month = time_clean.group(2)
    # находит содержание статьи
    # первые предложения с сутью статьи (1-2 обычно)
    preview = soup.findAll(
        attrs={"class" : "field field-name-field-article-lead field-type-text-long field-label-hidden"})
    preview = preview[0].get_text()
    # основной текст статьи
    main_text = soup.findAll(
        attrs={"class" : "field field-name-body field-type-text-with-summary field-label-hidden"})
    main_text = main_text[0].get_text()
    # находит подпись
    author = soup.findAll(
        attrs={"class" : "field field-name-field-article-author field-type-text field-label-hidden"})
    author = author[0].get_text()
    # проверяет наличие автора статьи
    if len(author) > 0:
        author_clean = re.search('[а-яА-ЯёЁ\s]*',author)
        author_clean = author_clean.group()
    else:
        author_clean = 'None'
    
    # склеивает первую строку с основной статьей
    article_text = preview + '\n' + main_text
    
    word_count = len(article_text.split())
    return title_clean,article_text,author_clean,year,month,time_general,category_clean,index,word_count

# в зависимости от режима создает и (до)записывает метаданные
def write_meta(regime,metadata):
    dirname = '.'
    meta = os.path.join(dirname,'metadata.csv')
    with open(meta,regime,encoding='utf-8') as m:
        m.write(metadata)

# прогоняет текст через майстем и кладет результат в нужные папки
def mystem(temp_filepath,out_dir1,out_dir2,index):
    os.system(r'C:\mystem.exe  -lcid --eng-gr ' +
              temp_filepath + ' ' + out_dir1 + os.sep + index + '.txt')
    os.system(r'C:\mystem.exe  -lcid --eng-gr --format xml ' +
              temp_filepath + ' ' + out_dir2 + os.sep + index + '.xml')
    
# создает все нужные папки каталога и записывает туда файлы
def write_down(title,article_text,author,year,month,time,category,index,full_link):
    # для PAIN TEXT
    # собирает всё, что надо записать в одну строку
    full_article = '@au %s\n@ti %s\n@da %s\n@topic %s\n@url %s\n%s' % (author,
                                    title,time,category,full_link,article_text)
    # собирает путь
    dirname = '.'
    directory = os.path.join(dirname,'plain',year,month)
    # проверяет путь и создает папки, которых нет
    if not os.path.exists(directory):
        os.makedirs(directory)
    # собирает название файла
    filename = '%s.txt' % index
    # собиает путь к файлу
    filepath = os.path.join(directory,filename)
    # записывает файл .txt
    with open(filepath,'w',encoding='utf-8') as f:
        f.write(full_article)

    # для MYSTEM
    # проверяет пути для папок аутпута и создает те, которых нет
    out_dir1 = os.path.join(os.getcwd(),'mystem-plain',year,month)
    if not os.path.exists(out_dir1):
        os.makedirs(out_dir1)
    out_dir2= os.path.join(os.getcwd(),'mystem-xml',year,month)
    if not os.path.exists(out_dir2):
        os.makedirs(out_dir2)
    # записывает только текст статьи (без метаданных) во временный файл
    with open(filename,'w',encoding='utf-8')as t:
        t.write(article_text)
    # подает его майстему
    temp_filepath = os.path.join(os.getcwd(),filename)
    mystem(temp_filepath,out_dir1,out_dir2,index)
    # удаляет временный файл
    os.remove(filename)
    metadata = '\n%s\t%s\t%s\t%s\tпублицистика\t%s\tнейтральный\tн-возраст\tн-уровень\tгородская\t%s\tВолгоградская Правда\t%s\tгазета\tРоссия\tВолгодонский регион\tru' % (filepath,author,title,time,category,full_link,year)

    # записывает метаданные в таблицу csv
    write_meta('a',metadata)

def main():
    # начальная страница газеты
    start_link = 'http://www.vpravda.ru'
    # приветствие и объем корпуса
    max_words = hello(start_link)
    # счетчик слов
    total_word_count = 0
    # создание файла для метаданных и запись заголовка
    metadata = 'path\tauthor\theader\tcreated\tsphere\ttopic\tstyle\taudience_age\t' + \
    'audience_level\taudience_size\tsource\tpublication\tpubl_year\tmedium\tcountry\tregion\tlanguage'
    write_meta('w',metadata)
    # список ссылок на все статьи газеты
    all_links = get_all_links(start_link)
    # счетчик скачанных статей
    n = 0
    print('Всего статей в газете:',len(all_links))
    for link in all_links:
        # собирает ссылку на статью
        full_link = start_link + link
        # скачивает статью и мета-информацию
        title,article_text,author,year,month,time,category,index,word_count = get_article(full_link)
        # записывает это в файл .txt и в таблицу, подает майстему
        write_down(title,article_text,author,year,month,time,category,index,full_link)
        n += 1
        total_word_count += word_count
        print('Статья %d. Слов %d.'% (n,total_word_count)) # для визуализации объема корпуса
        # завершает работу по достижении 100к слов
        if total_word_count > max_words:
            print('Общий размер корпуса: %d слов(а).' % total_word_count)
            break
    print('Вы скачали и обработали %d из %d статей с сайта %s' % (n,len(all_links),start_link))


if __name__ == '__main__':
    main()
