import json
import urllib.request

all_users = "elmiram, maryszmary, lizaku, nevmenandr, ancatmara, roctbb, akutuzov, agricolamz, lehkost, kylepjohnson, mikekestemont, demidovakatya, shwars, JelteF, timgraham, arogozhnikov, jasny, bcongdon, whyisjake"
users = all_users.split(', ')
users_info = {}
for user in users:
    url = 'https://api.github.com/users/%s/repos' % user
    response = urllib.request.urlopen(url)
    text = response.read().decode('utf-8')  # читаем ответ в строку
    data = json.loads(text) # превращаем джейсон-строку в объекты питона
    l =len(data)
    users_info.update({user: l})
print(users_info)
from operator import itemgetter
print(sorted(users_info.items(), key=itemgetter(1)))
