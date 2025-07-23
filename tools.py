import datetime
import os

import pytz
import requests
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
url = os.environ.get('URL')
if os.environ.get('AM_I_IN_A_DOCKER_CONTAINER', False):
    path = '/etc/randomizer/'
else:
    path = ''

for filename in ['log.txt', 'quires.txt', 'userids.txt']:
    if not os.path.isfile(f'{path}data/{filename}'):
        # Создаем файл, если он не существует
        with open(f'{path}data/{filename}', 'w', encoding='utf-8') as fl:
            fl.write('1')


def send_message(chat_id: int | str, message, keyboard=None) -> bool:
    # print(switch_safe_mode, switch_authorize_all, switch_entire_authorization, switch_message_deletion)
    if keyboard is None:
        send_body = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'HTML'
        }
    else:
        send_body = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'HTML',
            'reply_markup': keyboard
        }
    r = requests.post(url + 'sendMessage', json=send_body)
    return True if r.json()['ok'] else False


def delete_message(chat_id, message_id) -> None:
    requests.post(url + f'deleteMessage?chat_id={chat_id}&message_id={message_id}')


def append_log(msg, ping: int = None) -> None:
    try:
        with open(f'{path}data/log.txt', 'a', encoding='utf-8') as f:
            if not ping:
                f.write(f'[{datetime.datetime.now(pytz.timezone("Europe/Moscow")).strftime("%H:%M:%S.%fffff")}]: {msg}' + '\n')
            else:
                f.write(f'[{datetime.datetime.now(pytz.timezone("Europe/Moscow")).strftime("%H:%M:%S")}]<b>({ping}s.)</b> : {msg}' + '\n')
        print(msg)
    except Exception as e:
        with open(f'{path}data/log.txt', 'a', encoding='cp1251') as f:
            f.write(f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}]: {msg}' + '\n')
            f.write(f'^^^^^caught exception {e}' + '\n')
