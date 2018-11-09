import urllib.request
from urllib.request import Request, urlopen


def open_link(answ):
    link = 'https://suggest.yandex.ru/suggest-ya.cgi?srv=morda_ru_desktop&wiz=TrWth&uil=ru&fact=1&v=4&icon=1&lr=213&hl=1&bemjson=1&html=1&platform=desktop&rich_nav=1&show_experiment=222&show_experiment=224&verified_nav=1&rich_phone=1&safeclick=1&skip_clickdaemon_host=1&yu=7308116141541767940&callback=jQuery2140006796098868012024_1541769483220&part=animal'
    try:
        req = Request(link, headers={'User-Agent': 'Mozilla/5.0'})
        #connect to that page
        f = urlopen(req)
    except urllib.error.HTTPError:
        print('An Error occured')
        print(link)
    else:
        
