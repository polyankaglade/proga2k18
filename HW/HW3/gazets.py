import re
import os
import urllib.request
from bs4 import BeautifulSoup
#link = "http://www.vpravda.ru/politika/delegaciya-iz-germanii-pobyvala-u-volgogradskogo-vechnogo-ognya-60334"
#link = "http://www.vpravda.ru/obshchestvo/volgogradcam-obyasnili-kak-ne-dopustit-u-rebenka-cifrovogo-slaboumiya-61211"

def open_link(link):
    #connect to that page
    f = urllib.request.urlopen(link)
    #read it all in
    myfile = f.read()
    #build a document model
    soup = BeautifulSoup(myfile,'html.parser')
    #print the page verbatim
    # print(myfile)

    #pretty-print the html
    #print(soup.prettify())
    return soup

def get_all_links(start_link):
    all_links = []
    link = start_link + '/archive'
    # открывает страницу архива газеты
    soup = str(open_link(link))
    # ищет все ссылки на дни, в которые что-либо публиковалось
    archive_days = re.findall('<td class="day.*?"><a href="(.+?)">',soup)
    #print(archive_days[0:20])
    #print(len(archive_days))
    for day in archive_days[0:2]:
        # собирает ссылку на архив за определенный день
        day_link = start_link + str(day)
        # открывает архив за этот день
        day_soup = open_link(day_link)
        # вырезает блок основного контента
        article_links = day_soup.findAll(id='content')
        article_links = str(article_links[0])
        # ищет все ссылки на собственно статьи
        article_links = re.findall('field-content"><a href="(.+?)">',article_links)
        # добавляет все ссылки в общий список
        for article_link in article_links: 
            all_links.append(article_link)
    #print(all_links)
    return all_links


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
    # вся информация о статье и сама статья размечены одним классом
    important = soup.findAll(attrs={"class" : "field-item even"})
    # если картинки нет:
    if len(important) == 4:
        time = important[0].get_text()
        time_clean = re.search('(\d{2})\.(\d{2})\.(\d{4})',time) # отделяет месяц и год
        time_general = time_clean.group()
        year = time_clean.group(3)
        month = time_clean.group(2)
        preview = important[1].get_text() # первое предложение с сутью статьи
        text = important[2].get_text()
        author = important[3].get_text()
        # проверяет наличие автора статьи
        if len(author) > 0:
            author_clean = re.search('[а-яА-ЯёЁ\s]*',author)
            author_clean = author_clean.group()
        else:
            author_clean = 'None'
    # если картинка есть
    elif len(important) == 5:
        time = important[0].get_text()
        time_clean = re.search('(\d{2})\.(\d{2})\.(\d{4})',time)
        time_general = time_clean.group()
        year = time_clean.group(3)
        month = time_clean.group(2)
        preview = important[2].get_text()
        text = important[3].get_text()
        author = important[4].get_text()
        if len(author) > 0:
            author_clean = re.search('[а-яА-ЯёЁ\s]*',author)
            author_clean = author_clean.group()
        else:
            author_clean = 'None'
    
    # склеивает первую строку с основной стаьей
    article_text = preview + '\n' + text
    return title_clean,article_text,author_clean,year,month,time_general,category_clean,index

def write_meta(regime,metadata):
    dirname = './gazety'
    meta = os.path.join(dirname,'metadata.csv')
    with open(meta,regime,encoding='utf-8') as m:
        m.write(metadata)

def write_down(article,full_link):
    title,article_text,author,year,month,time,category,index = article
    # собирает всё, что надо записать в одну строку
    full_article = '@au %s\n@ti %s\n@da %s\n@topic %s\n@url %s\n%s' % (author,title,time,category,full_link,article_text)
    # собирает путь
    dirname = './gazety'
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
    metadata = '\n%s\t%s\t%s\t%s\tпублицистика\t%s\tнейтральный\tн-возраст\tн-уровень\tгородская\t%s\tВолгоградская Правда\t%s\tгазета\tРоссия\tВолгодонский регион\tru' % (filepath,author,title,time,category,full_link,year)
    # записывает метаданные в таблицу csv
    write_meta('a',metadata)

def main():
    metadata = 'path\tauthor\theader\tcreated\tsphere\ttopic\tstyle\taudience_age\taudience_level\taudience_size\tsource\tpublication\tpubl_year\tmedium\tcountry\tregion\tlanguage'
    write_meta('w',metadata)
    # начальная страница газеты
    start_link = 'http://www.vpravda.ru'
    # список ссылок на все статьи газеты
    all_links = get_all_links(start_link)
    # счетчик скачанных статей
    n = 0
    for link in all_links: #[0:3]
        # собирает ссылку на статью
        full_link = start_link + link
        # скачивает статью и мета-информацию
        article = get_article(full_link)
        # записывает это в файл .txt и в таблицу
        write_down(article,full_link)
        n += 1
    print('Вы скачали %d из %d статей с сайта %s' % (n,len(all_links),start_link))

if __name__ == '__main__':
    main()
