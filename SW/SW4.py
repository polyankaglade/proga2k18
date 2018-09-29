import requests
import re

#result = requests.get('https://yandex.ru/pogoda/moscow/')
#result = result.text
with open('weather.html',encoding='utf-8') as f:
    result = f.read()
temp = re.findall('temp fact__temp"><.+?>(.+?)<\/span>',result)
#temp_res = temp.search(result)
print('Температура сегодня:',temp[0])
obl = re.findall('fact__condition.+?>([а-яёА-ЯЁ]+?)<\/div',result)
#obl_res = obl.search(result)
print('Облачность сегодня:',obl[0])
sunset = re.findall('value_sunset">(?:<.+?>){6}(.+?)<',result)
sunrise = re.findall('value_sunrise">(?:<.+?>){6}(.+?)<',result)
#sunrise_res = sunrise.search(result)
#sunset_res = sunset.search(result)
print('Рассвет сегодня в',sunrise[0])
print('Закат сегодня в',sunset[0])
tomorrow_temp_day = re.findall('forecast-briefly-old__temp_day"><.+?>(.+?)<\/',result)
tomorrow_temp_night = re.findall('forecast-briefly-old__temp_night"><.+?>(.+?)<\/',result)
tomorrow_clouds = re.findall('forecast-briefly-old__condition">(.+?)<',result)
print('Температура завтра днем:',tomorrow_temp_day[1])
print('Температура завтра ночью:',tomorrow_temp_night[1])
print('Облачность завтра:',tomorrow_clouds[0])
