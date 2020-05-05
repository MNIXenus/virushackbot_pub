import telebot
import requests
import logging

from aiml_bot import BotClientMod
from math import ceil
from doc_prepr import *
from compare_logic import *
token = "token: 001.0323860545.1694051326:752470364"
logging.disable(level=100) #set 50 for debugging

telebot.console_output_handler = logging.StreamHandler()
aiml_bot = BotClientMod()

with open('tok', 'r') as tok:
    tlg_bot = telebot.TeleBot(tok.read())
    tlg_bot.compare_flag = False

def get_proxy():
    global proxies_provider
    global proxies
    if 'proxies_provider' not in globals():
        proxies_provider = 'https://www.proxy-list.download/api/v1/get?type=socks5'
        try:
            proxies = [i for i in requests.get(proxies_provider).text.split()]
            print('Proxies list recieved.')
        except ConnectionError:
            print('Unable to get proxies list, check your internet connection')
    for each in proxies:
        yield(each)
get_proxy_instance = get_proxy()
def ConnectionResolve():
    print('Connection troubles, trying to apply proxies...')
    telebot.apihelper.proxy = {'https': 'socks5h://{}'.format(next(get_proxy_instance))}
    print(telebot.apihelper.proxy['https'])
    run_bot()


class Client(dict):
    def __init__(self):
        self['first_bank'] = None
        self['second_bank'] = None
        self['first_tariff'] = None
        self['second_tariff'] = None
        self['condition'] = None


def run_bot():
    global clients
    clients = {}
    try:
        tlg_bot.polling(timeout=1000, none_stop=True, interval = 1)
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        ConnectionResolve()



@tlg_bot.message_handler(commands=['start'])
def start_message_1(message):
    answer = aiml_bot.get_answer(message.chat.id, 'Привет')
    print(message.chat.id)

    tlg_bot.send_message(message.chat.id, answer)

@tlg_bot.message_handler(commands=['compare'])
def start_message(message):
    #clients[str(message.chat.id)] = Client()
    clients[str(message.chat.id)]['compare_flag'] = True
    count_banks = ceil(len(banks_tariff) / 3)

    keyboard_bank = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True,
                                                      one_time_keyboard=True,
                                                      selective=True,
                                                      row_width=count_banks,
                                                      )
    banks = split(list(banks_tariff), 3)
    for i in banks:
        keyboard_bank.add(*i)

    tlg_bot.send_message(message.chat.id,
                     aiml_bot.get_answer(message.chat.id, 'GREET') + aiml_bot.get_answer(message.chat.id, 'CHOOSE BANK').format('первый'),
                     reply_markup=keyboard_bank,
                     )

    clients[str(message.chat.id)]['condition'] = 'sending_first_bank'

@tlg_bot.message_handler(content_types=['text'])
def send_text(message):
    if str(message.chat.id) not in clients.keys():
        clients[str(message.chat.id)] = Client()
        clients[str(message.chat.id)]['compare_flag'] = False
    if clients[str(message.chat.id)]['compare_flag']:
        if message.text in banks_tariff and clients[str(message.chat.id)]['condition'] == 'sending_first_bank':

            tariffs = banks_tariff[message.text]
            clients[str(message.chat.id)]['first_bank'] = message.text
            count_tariffs = ceil(len(tariffs) / 3)

            keyboard_tariff = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True,
                                                                one_time_keyboard=True,
                                                                selective=True,
                                                                row_width=count_tariffs,
                                                                )
            tariffs = split(tariffs, 3)
            for i in tariffs:
                keyboard_tariff.add(*i)

            tlg_bot.send_message(message.chat.id,
                             aiml_bot.get_answer(message.chat.id, 'CHOOSE TARIFF').format(message.text),
                             reply_markup=keyboard_tariff)

            clients[str(message.chat.id)]['condition'] = 'sending_first_tariff'

        elif clients[str(message.chat.id)]['condition'] == 'sending_first_tariff' and message.text in banks_tariff[clients[str(message.chat.id)]['first_bank']]:

            clients[str(message.chat.id)]['first_tariff'] = message.text
            banks = [i for i in banks_tariff if i != clients[str(message.chat.id)]['first_bank']]
            count_banks = ceil(len(banks) / 3)
            keyboard_bank = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True,
                                                              one_time_keyboard=True,
                                                              selective=True,
                                                              row_width=count_banks,
                                                              )
            banks = split(list(banks), 3)
            for i in banks:
                keyboard_bank.add(*i)

            tlg_bot.send_message(message.chat.id,
                             aiml_bot.get_answer(message.chat.id, 'CHOOSE BANK').format('второй'),
                             reply_markup=keyboard_bank,
                             )

            clients[str(message.chat.id)]['condition'] = 'sending_second_bank'

        elif message.text in banks_tariff and clients[str(message.chat.id)]['condition'] == 'sending_second_bank':

            tariffs = banks_tariff[message.text]
            clients[str(message.chat.id)]['second_bank'] = message.text
            count_tariffs = ceil(len(tariffs) / 3)

            keyboard_tariff = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True,
                                                                one_time_keyboard=True,
                                                                selective=True,
                                                                row_width=count_tariffs,
                                                                )
            tariffs = split(tariffs, 3)
            for i in tariffs:
                keyboard_tariff.add(*i)

            tlg_bot.send_message(message.chat.id,
                             aiml_bot.get_answer(message.chat.id, 'CHOOSE TARIFF').format(message.text),
                             reply_markup=keyboard_tariff)

            clients[str(message.chat.id)]['condition'] = 'sending_second_tariff'

        elif clients[str(message.chat.id)]['condition'] == 'sending_second_tariff' and message.text in banks_tariff[clients[str(message.chat.id)]['second_bank']]:
            clients[str(message.chat.id)]['second_tariff'] = message.text
            tlg_bot.send_photo(message.chat.id,
                               make_img_from_html(clients[str(message.chat.id)]['first_tariff'], clients[str(message.chat.id)]['first_bank'], clients[str(message.chat.id)]['second_tariff'],
                                                  clients[str(message.chat.id)]['second_bank']))
            clients[str(message.chat.id)]['compare_flag'] = False
            clients[str(message.chat.id)]['condition'] = ''
        else:
            clients[str(message.chat.id)]['compare_flag'] = False
            clients[str(message.chat.id)]['condition'] = ''
            answer = aiml_bot.get_answer(message.chat.id, message.text)
            tlg_bot.send_message(message.chat.id, answer, parse_mode="html")
            print(answer)

    else:
        answer = aiml_bot.get_answer(message.chat.id, message.text)
        tlg_bot.send_message(message.chat.id, answer, parse_mode = "html")
        print(answer)


if __name__ == "__main__":
    run_bot()
