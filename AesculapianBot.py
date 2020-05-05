from bot.bot import Bot
from bot.handler import *
from aiml_bot import BotClientMod
import json
import traceback
import get_places_api as places
import get_covid_data
from googletrans import Translator
import datetime
import dateparser
from spellchecker import suggest
from input_parser import *
translator = Translator()
TOKEN = ''


bot = Bot(TOKEN)
aiml_bot = BotClientMod()

def replacing(answer):
    answer = answer.replace('BASICTHEMES001 ', '')
    return answer


def formating(date):
    date = str(date).split('-')
    m = int(date[1])
    a = ['Января', 'Февраля', 'Марта', 'Апреля', 'Мая', 'Июня', 'Июля', 'Августа', 'Сентября', 'Октября', 'Ноября',
         'Декабря']
    return date[2]+' '+a[m % 12-1]+' '+date[0]

def main_keyborad():
    markup_row1 = "{}".format(json.dumps([[
        {"text": "Симптомы COVID-19", "callbackData": "SYMPTOMS", "style": "attention"},
        {"text": "Пути передачи COVID-19", "callbackData": "SPREADING", "style": "attention"}],
        [{"text": "Профилактика COVID-19", "callbackData": "PROFILACTIC", "style": "primary"},
        {"text": "Мифы о COVID-19", "callbackData": "MYTHS", "style": "primary"},
        {"text": "Статистика по COVID-19", "callbackData": "STATISTIC", "style": "primary"}],
        [{"text": "Ближайшие Аптеки", "callbackData": "PHARMINIT", "style": "attention"},
         {'text': "Ближайшие больницы","callbackData": "HOSPITALINIT", "style": "attention" }]]))
    return markup_row1


def buttons_answer_cb(bot, event):
    try:
        print(event.data['from']['userId'])
        category = event.data['callbackData']
        answer = aiml_bot.get_answer(event.data['from']['userId'], category)
        bot.answer_callback_query(event.data['queryId'], '')
        if category in ['SYMPTOMS', 'PROFILACTIC', 'SPREADING']:
            bot.send_text(chat_id=event.data['from']['userId'], text=answer, inline_keyboard_markup=main_keyborad())
        else:
            bot.send_text(chat_id=event.data['from']['userId'], text=answer)

    except Exception:
        print(traceback.format_exc())


def file_cb(event, file, deletable_id):
    print(file[1])
    text = f"Интерактивная Карта: {file[2]}\n\n"
    c = 0
    for i in file[1]:
        c += 1
        name = i['Name']
        address = i['Address']
        phone = i['Phone']
        dist = i['Distance']
        time = i['Duration']
        site = 'Отсутствует' if i['Site'] is None else i['Site']
        text += f"Номер: {c}\n" \
                f"{name}\n" \
                f"Телефон: {phone}\n" \
                f"Адрес: {address}\n" \
                f"Расстояние: {dist}\n" \
                f"Примерное время пути: {time}\n" \
                f"Сайт: {site}\n\n"
    answer = aiml_bot.get_answer(event.from_chat, 'BASICTHEMES001')
    text += replacing(answer)
    bot.delete_messages(event.from_chat, deletable_id)
    bot.send_file(event.from_chat, file=file[0], caption=text, inline_keyboard_markup=main_keyborad())


def message_cb(bot, event):
    try:
        if event.text != '/start':
            answer = aiml_bot.get_answer(event.from_chat, suggest(event.text))
            if answer.startswith('STATINIT'):
                a = lemmatize(event.text)
                print(get_countries(a))
                # # answer = answer.replace(' ', '')
                # answer = answer.split('$')
                # print(answer[2].strip()[:-1])
                # # print(dateparser.parse('первое мая'))
                # date = str(dateparser.parse(answer[2].strip()[:-1]))[:-8]
                # print(date)
                # country = answer[1].strip()
                # print(country)
                # if date != '':
                #     data = get_covid_data.get_report_ru(country, date)
                # else:
                #     data = get_covid_data.get_report_ru(country)
                #     date = datetime.datetime.now().date() - datetime.timedelta(days=1)
                # print(data)
                # confirmed = data['confirmed']
                # deaths = data['deaths']
                # recovered = data['recovered']
                # active = data['active']
                # fatality_rate = data['fatality_rate']
                # date = formating(date)
                # text = f"""На {date} в {country} было подтверждено {confirmed} случаев заражения.\nПроизошло {deaths} смертей.\nВылечилось {recovered}.\nКоличество больных составляет {active} человек.\nСмертность составляет {fatality_rate}."""
                # # text = aiml_bot.get_answer(event.from_chat, f'GETSTATTEMPLATE {str(date)} {country} {confirmed} {deaths} {recovered} {active} {fatality_rate}')
                # bot.send_text(chat_id=event.from_chat, text=text+'\nЧто еще я могу для вас сделать?', inline_keyboard_markup=main_keyborad())
                # # answer = aiml_bot.get_answer(event.from_chat, 'BASICTHEMES001')
                # # bot.send_text(event.from_chat, replacing(answer), inline_keyboard_markup=main_keyborad())

            elif answer.startswith('PHARMINIT'):
                a = bot.send_text(chat_id=event.from_chat, text='Пожалуйста, подождите, ищу наилучшие варианты...')
                deletable_id = a.json()['msgId']
                answer = answer.split('$')
                print(answer[1].strip())
                pic = places.get_nearby_places(answer[1][:-1].strip(), get_image=True)
                if pic != 0:
                    file_cb(event, pic, deletable_id)
                else:
                    answer = aiml_bot.get_answer(event.from_chat, 'PHARMERR')
                    bot.edit_text(event.from_chat, deletable_id, str(answer))

            elif answer.startswith('HOSPITALINIT'):
                a = bot.send_text(chat_id=event.from_chat, text='Пожалуйста, подождите, ищу наилучшие варианты...')
                deletable_id = a.json()['msgId']
                answer = answer.split('$')
                print(answer[1].strip())
                pic = places.get_nearby_places(answer[1][:-1].strip(), build_type='Hospital', radius=700, get_image=True, zoom=14)
                if pic != 0:
                    file_cb(event, pic, deletable_id)
                else:
                    answer = aiml_bot.get_answer(event.from_chat, 'HOSPITALERR')
                    bot.edit_text(event.from_chat, deletable_id, replacing(answer))

            elif 'BASICTHEMES001' in answer:
                answer = answer.replace('BASICTHEMES001', '')
                bot.send_text(event.from_chat, answer, inline_keyboard_markup=main_keyborad())
            else:
                bot.send_text(chat_id=event.from_chat, text=replacing(answer))

        else:
            print(event)
            answer = aiml_bot.get_answer(event.from_chat, 'Привет')
            bot.send_text(chat_id=event.from_chat, text=replacing(answer), inline_keyboard_markup=main_keyborad())

    except Exception:
        print(traceback.format_exc())


bot.dispatcher.add_handler(BotButtonCommandHandler(callback=buttons_answer_cb))
bot.dispatcher.add_handler(MessageHandler(callback=message_cb))
bot.start_polling()
bot.idle()
# d = 'STATINIT Австралия 2020-04-03'
# d = d
# print(d)
# q = get_covid_data.get_report_ru(d[:-11], d[-11:])
# print(q)
# q = {'data': [{'date': '2020-04-03', 'confirmed': 91, 'deaths': 1, 'recovered': 18, 'confirmed_diff': 4, 'deaths_diff': 0, 'recovered_diff': 7, 'last_update': '2020-04-03 22:52:45', 'active': 72, 'active_diff': -3, 'fatality_rate': 0.011, 'region': {'iso': 'AUS', 'name': 'Australia', 'province': 'Australian Capital Territory', 'lat': '-35.4735', 'long': '149.0124', 'cities': []}}, {'date': '2020-04-03', 'confirmed': 2389, 'deaths': 12, 'recovered': 4, 'confirmed_diff': 91, 'deaths_diff': 2, 'recovered_diff': 0, 'last_update': '2020-04-03 22:52:45', 'active': 2373, 'active_diff': 89, 'fatality_rate': 0.005, 'region': {'iso': 'AUS', 'name': 'Australia', 'province': 'New South Wales', 'lat': '-33.8688', 'long': '151.2093', 'cities': []}}, {'date': '2020-04-03', 'confirmed': 22, 'deaths': 0, 'recovered': 0, 'confirmed_diff': 1, 'deaths_diff': 0, 'recovered_diff': 0, 'last_update': '2020-04-03 22:52:45', 'active': 22, 'active_diff': 1, 'fatality_rate': 0, 'region': {'iso': 'AUS', 'name': 'Australia', 'province': 'Northern Territory', 'lat': '-12.4634', 'long': '130.8456', 'cities': []}}, {'date': '2020-04-03', 'confirmed': 873, 'deaths': 4, 'recovered': 8, 'confirmed_diff': 38, 'deaths_diff': 0, 'recovered_diff': 0, 'last_update': '2020-04-03 22:52:45', 'active': 861, 'active_diff': 38, 'fatality_rate': 0.0046, 'region': {'iso': 'AUS', 'name': 'Australia', 'province': 'Queensland', 'lat': '-28.0167', 'long': '153.4000', 'cities': []}}, {'date': '2020-04-03', 'confirmed': 396, 'deaths': 0, 'recovered': 46, 'confirmed_diff': 29, 'deaths_diff': 0, 'recovered_diff': 40, 'last_update': '2020-04-03 22:52:45', 'active': 350, 'active_diff': -11, 'fatality_rate': 0, 'region': {'iso': 'AUS', 'name': 'Australia', 'province': 'South Australia', 'lat': '-34.9285', 'long': '138.6007', 'cities': []}}, {'date': '2020-04-03', 'confirmed': 74, 'deaths': 2, 'recovered': 5, 'confirmed_diff': 2, 'deaths_diff': 0, 'recovered_diff': 0, 'last_update': '2020-04-03 22:52:45', 'active': 67, 'active_diff': 2, 'fatality_rate': 0.027, 'region': {'iso': 'AUS', 'name': 'Australia', 'province': 'Tasmania', 'lat': '-41.4545', 'long': '145.9707', 'cities': []}}, {'date': '2020-04-03', 'confirmed': 1085, 'deaths': 7, 'recovered': 476, 'confirmed_diff': 49, 'deaths_diff': 2, 'recovered_diff': 54, 'last_update': '2020-04-03 22:52:45', 'active': 602, 'active_diff': -7, 'fatality_rate': 0.0065, 'region': {'iso': 'AUS', 'name': 'Australia', 'province': 'Victoria', 'lat': '-37.8136', 'long': '144.9631', 'cities': []}}, {'date': '2020-04-03', 'confirmed': 400, 'deaths': 2, 'recovered': 92, 'confirmed_diff': 0, 'deaths_diff': 0, 'recovered_diff': 28, 'last_update': '2020-04-03 22:52:45', 'active': 306, 'active_diff': -28, 'fatality_rate': 0.005, 'region': {'iso': 'AUS', 'name': 'Australia', 'province': 'Western Australia', 'lat': '-31.9505', 'long': '115.8605', 'cities': []}}]}
# q = [{'date': '2020-04-03', 'confirmed': 91, 'deaths': 1, 'recovered': 18, 'confirmed_diff': 4, 'deaths_diff': 0,
#       'recovered_diff': 7, 'last_update': '2020-04-03 22:52:45', 'active': 72, 'active_diff': -3,
#       'fatality_rate': 0.011,
#       'region': {'iso': 'AUS', 'name': 'Australia', 'province': 'Australian Capital Territory', 'lat': '-35.4735',
#                  'long': '149.0124', 'cities': []}},
#      {'date': '2020-04-03', 'confirmed': 2389, 'deaths': 12, 'recovered': 4, 'confirmed_diff': 91, 'deaths_diff': 2,
#       'recovered_diff': 0, 'last_update': '2020-04-03 22:52:45', 'active': 2373, 'active_diff': 89,
#       'fatality_rate': 0.005,
#       'region': {'iso': 'AUS', 'name': 'Australia', 'province': 'New South Wales', 'lat': '-33.8688',
#                  'long': '151.2093', 'cities': []}},
#      {'date': '2020-04-03', 'confirmed': 22, 'deaths': 0, 'recovered': 0, 'confirmed_diff': 1, 'deaths_diff': 0,
#       'recovered_diff': 0, 'last_update': '2020-04-03 22:52:45', 'active': 22, 'active_diff': 1, 'fatality_rate': 0,
#       'region': {'iso': 'AUS', 'name': 'Australia', 'province': 'Northern Territory', 'lat': '-12.4634',
#                  'long': '130.8456', 'cities': []}},
#      {'date': '2020-04-03', 'confirmed': 873, 'deaths': 4, 'recovered': 8, 'confirmed_diff': 38, 'deaths_diff': 0,
#       'recovered_diff': 0, 'last_update': '2020-04-03 22:52:45', 'active': 861, 'active_diff': 38,
#       'fatality_rate': 0.0046,
#       'region': {'iso': 'AUS', 'name': 'Australia', 'province': 'Queensland', 'lat': '-28.0167', 'long': '153.4000',
#                  'cities': []}},
#      {'date': '2020-04-03', 'confirmed': 396, 'deaths': 0, 'recovered': 46, 'confirmed_diff': 29, 'deaths_diff': 0,
#       'recovered_diff': 40, 'last_update': '2020-04-03 22:52:45', 'active': 350, 'active_diff': -11, 'fatality_rate': 0,
#       'region': {'iso': 'AUS', 'name': 'Australia', 'province': 'South Australia', 'lat': '-34.9285',
#                  'long': '138.6007', 'cities': []}},
#      {'date': '2020-04-03', 'confirmed': 74, 'deaths': 2, 'recovered': 5, 'confirmed_diff': 2, 'deaths_diff': 0,
#       'recovered_diff': 0, 'last_update': '2020-04-03 22:52:45', 'active': 67, 'active_diff': 2, 'fatality_rate': 0.027,
#       'region': {'iso': 'AUS', 'name': 'Australia', 'province': 'Tasmania', 'lat': '-41.4545', 'long': '145.9707',
#                  'cities': []}},
#      {'date': '2020-04-03', 'confirmed': 1085, 'deaths': 7, 'recovered': 476, 'confirmed_diff': 49, 'deaths_diff': 2,
#       'recovered_diff': 54, 'last_update': '2020-04-03 22:52:45', 'active': 602, 'active_diff': -7,
#       'fatality_rate': 0.0065,
#       'region': {'iso': 'AUS', 'name': 'Australia', 'province': 'Victoria', 'lat': '-37.8136', 'long': '144.9631',
#                  'cities': []}},
#      {'date': '2020-04-03', 'confirmed': 400, 'deaths': 2, 'recovered': 92, 'confirmed_diff': 0, 'deaths_diff': 0,
#       'recovered_diff': 28, 'last_update': '2020-04-03 22:52:45', 'active': 306, 'active_diff': -28,
#       'fatality_rate': 0.005,
#       'region': {'iso': 'AUS', 'name': 'Australia', 'province': 'Western Australia', 'lat': '-31.9505',
#                  'long': '115.8605', 'cities': []}}]
# for i in q:
#     print(i['confirmed'])