import json
import os
import random
import time

import requests
from flask import Flask, request
from waitress import serve

import tools

app = Flask(__name__)

if os.environ.get('AM_I_IN_A_DOCKER_CONTAINER', False):
    path = '/etc/randomizer/'
else:
    path = ''

pendingupdates_lastchecked = 0
pendingupdates_lastsent = 0
ping = 0

with open(f'{path}data/userids.txt', 'r', encoding='utf-8') as f:
    gifted_userids = f.read().split()
with open(f'{path}data/prizes.json', 'r', encoding='utf-8') as f:
    prizes = json.load(f)

weights = [float(prizes['40']['odds']), float(prizes['50']['odds']), float(prizes['80']['odds'])]
categories = ['40', '50', '80']
category_to_index = {'40': 0, '50': 1, '80': 2}
categories_messages = ['🤑Личная скидка 40% на:\n\nБейсболка "НЛО", Бейсболка "НЛО" black, Кепка "Halloween edition", Лонгслив "Серебро" boiled gray, Лонгслив "Бензин" white, Лонгслив "Серебро" black, Кепка "Пират" gray,  Оверсайз брюки бензин серые, Оверсайз брюки базовые серые, Оверсайз брюки бензин черные, Оверсайз брюки базовые черные.\n\n👽 Скидка на весь каталог 30%\n\n💚 Скидки не суммируются. Забирай выигрыш на сайте: https://invmerch.ru/collection/kosmonavtov-net\n\nакция действует до 2.12.2024',
                       '🤑 Личная скидка 50% на: \n\nФутболка "Твои глаза" v.1, Футболка "Твои глаза" v.2, Футболка "Космос нас не ждет" gray, Футболка "Космос нас не ждет" black, Футболка КН х 13 карат, Худи "Бензин", Худи "Серебро" chocolate, Худи "Бензин" chocolate, Маска "Бензин"\n\n👽 Скидка на весь каталог 30%\n\n💚 Скидки не суммируются. Забирай выигрыш на сайте: https://invmerch.ru/collection/kosmonavtov-net\n\nакция действует до 2.12.2024',
                       '🤑 Личная скидка 80% на: \n\nЛонгслив КН х 13 карат, Свитер "Chistmas Vibe" gray\n\n👽 Скидка на весь каталог 30%\n\n💚 Скидки не суммируются. Забирай выигрыш на сайте: https://invmerch.ru/collection/kosmonavtov-net\n\nакция действует до 2.12.2024']


@app.route('/', methods=['GET', 'POST'])
def firewall():
    global pendingupdates_lastchecked, pendingupdates_lastsent, ping
    if request.method == "GET":
        return 'I\'m working'
    r = request.get_json()
    with open(f'{path}data/quires.txt', 'a', encoding='utf-8') as f:
        f.write(str(r) + '\n')
    print(r)
    current_time = time.time()
    if current_time - pendingupdates_lastchecked > 60:
        pendingupdates_lastchecked = current_time
        response = requests.get(f'{tools.url}getWebhookInfo')
        if response.status_code == 200:
            pendingupdates_count = response.json().get("result", {}).get("pending_update_count", 0)
            if pendingupdates_count > 25:
                if current_time - pendingupdates_lastsent > 60 * 5:  # 3600 секунд = 1 час
                    tools.send_message(647372660, f'⭕Я заметил, что pending updates сейчас: <b>{pendingupdates_count}</b>\n{tools.url}getWebhookInfo')
                    pendingupdates_lastsent = current_time
    if 'callback_query' in r:
        chat_id = str(r['callback_query']['message']['chat']['id'])
        if chat_id == r['callback_query']['data']:
            user_id = str(r['callback_query']['from']['id'])
            first_name = str(r['callback_query']['from']['first_name'])
            requests.post(tools.url + f"answerCallbackQuery?callback_query_id={r['callback_query']['id']}")
            # if user_id not in gifted_userids:
            if True:
                available_categories = [cat for cat in categories if prizes[cat]['codes']]
                available_weights = [float(weights[categories.index(cat)]) for cat in available_categories]
                # Если нет доступных кодов во всех категориях, возвращаем None
                if not available_categories:
                    tools.send_message(user_id, 'К сожалению, все призы закончились.')
                    return 'ok'
                chosen_category = random.choices(available_categories, weights=available_weights, k=1)[0]
                if chosen_category in prizes and prizes[chosen_category]['codes']:
                    # Извлекаем и удаляем первый код
                    chosen_code = prizes[chosen_category]['codes'].pop(0)
                    tools.send_message(chat_id, f'Поздравляю! Личная скидка для тебя по промокоду <code>{chosen_code}</code>. Сейчас расскажу на что она действует!')
                    tools.send_message(user_id, categories_messages[category_to_index[chosen_category]])
                    gifted_userids.append(user_id)
                    with open(f'{path}data/userids.txt', 'w', encoding='utf-8') as f:
                        f.write(' '.join(gifted_userids))
                    with open(f'{path}data/prizes.json', 'w', encoding='utf-8') as f:
                        json.dump(prizes, f, indent=2)
                    tools.delete_message(chat_id, r['callback_query']['message']['message_id'])
                    tools.append_log(f'Выдан {chosen_category}%: {chosen_code} {first_name}({user_id})')
            else:
                tools.send_message(chat_id, 'Ты уже получил свой приз. Дай шанс остальным!')
        return 'OK'
    if 'message' in r:
        ping = round(current_time - int(r['message']['date']), 2)
        print(f'ping: {ping}s. ')
        if r['message']['chat']['type'] == 'private':
            dm_handler(r)
    return 'OK'


def dm_handler(r):
    user_id = str(r['message']['from']['id'])
    chat_id = r['message']['chat']['id']
    if 'text' in r['message']:
        msg = r['message']['text']
        match msg:
            case '/start':
                if user_id not in gifted_userids or True:
                    tools.send_message(user_id, 'Добро пожаловать! Сегодня у тебя есть уникальная возможность выиграть призы от любимой группы!', {'inline_keyboard': [[{'text': 'Попытать удачу', 'callback_data': chat_id}]]})
                else:
                    tools.send_message(chat_id, 'Ты уже получил свой приз. Дай шанс остальным!')
            case '/logs' if user_id == '647372660':
                with open(f'{path}data/log.txt', 'r', encoding='utf-8') as f:
                    log = []
                    for line in f:
                        index = line.find('{')
                        if index != -1:
                            log.append(line[:index] + '\n')
                        else:
                            log.append(line)
                    log = ''.join(log)
                    if len(log) <= 4096:
                        send_body = {
                            'chat_id': user_id,
                            'text': log,
                            'parse_mode': 'HTML'
                        }
                    else:
                        send_body = {
                            'chat_id': user_id,
                            'text': log[-4096:],
                            'parse_mode': 'HTML'
                        }
                    requests.post(tools.url + 'sendMessage', json=send_body)
            case '/stat' if user_id == '647372660':
                # Проверяем наличие кодов в каждом разделе
                for key, value in prizes.items():
                    if not value["codes"]:  # Если список кодов пуст
                        tools.send_message(user_id, f"Коды для {key}% закончились.")
                    else:
                        tools.send_message(user_id, f"Коды для {key}% ещё есть ({len(value['codes'])} шт.).")
            case _:
                tools.send_message(user_id, 'Неизвестная команда')


if __name__ == '__main__':
    if os.environ.get('AM_I_IN_A_DOCKER_CONTAINER', False):
        serve(app, host='0.0.0.0', port=8881, url_scheme='http')
    else:
        # app.run(host='192.168.1.10', port=8890)
        app.run(host='192.168.1.27', port=8890)
# TODO:
# нет кодов, категория выше, отдельная функц
# по категориям хелпа
