"""
    Пока для простоты сделал mapper только на 3 основных типа компаний:
        Аптеки, Всё для здоровья, Больницы и поликлиники.

    В боте юзать функцию 'get_nearby_places'.
    :argument
        location - Строка адреса, введённая пользователем. Форматирования не требует.
        count - Количество объектов, которые нужно вернуть *5 объектов по умолчанию
        build_type - Тип компании:
            Pharmacy [Аптеки] *Выбрано по умолчанию
            Health [Всё для здоровья]
            Hospital [Больницы и поликлиники]
        radius - Радиус поиска (в метрах) *200 метров по умолчанию
        get_image - Если True, то вернёт картинку с текущим местоположением юзверя
        и найденными компаниями *False по умолчанию

    :return
        На возврат список словарей со следующими полями:
        Name - Название компании
        Address - Адрес компании (в нормальном готовом виде)
        Phone - Телефон компании
        Site - Сайт компании (если есть)
        Distance - Дистанция пешком до компании
        Duration - Время ходьбы до компании

        Если get_image - True, тогда вернёт ещё и img - PIL Image object.
    Функция может вернуть 0, если объектов с заданными параметрами найдено не будет.
    ПРЕДЛОЖЕНИЕ! Если вернулся 0, то предлагаем пользователю увеличить радиус поиска!!!
    Как вариант ответа от пользователя - 2 кнопки: "Да" и "Нет". Если "Да", то не спрашивать
    радиус, на который нужно увеличить, а просто вручную увеличивать на условные 200 метров...
################################################################################################

    Также добавил функцию 'get_locations_img'.
    Функция возвращает картиночку с картой и меткой в том месте, какой адресс был введён.
    :argument
        location - Строка адреса, введённая пользователем. Форматирования не требует.

    :return
        img - PIL Image object.

    :return
        img - PIL Image object.
        
    В самой функции есть закомментированная строка. Если её раскомментить, то картиночка сохранится в корень
    Сделано для тестирования. Внизу файла есть 2 закомментированные строки вызова функций.
"""

from googleplaces import GooglePlaces, types, lang
import requests
from PIL import Image
import requests
from io import BytesIO

YOUR_API_KEY = 'insertyourtok'

google_places = GooglePlaces(YOUR_API_KEY)

mapper = {
    'Pharmacy': types.TYPE_PHARMACY,
    'Health': types.TYPE_HEALTH,
    'Hospital': types.TYPE_HOSPITAL,
    'Clinic': types.TYPE_DOCTOR,
}


def get_nearby_places(location, count=5, build_type='Pharmacy', radius=200, get_image=False, zoom=15):
    query_result = google_places.nearby_search(
        location=location, keyword=build_type,
        radius=radius, types=[mapper[build_type]],
        language=lang.RUSSIAN)

    if query_result.has_attributions:
        print(query_result.html_attributions)

    results = []
    icount = 0
    for place in query_result.places:
        place.get_details()

        if place.name is not None and place.formatted_address is not None and (
                place.local_phone_number is not None or place.international_phone_number):
            iplace = {
                'Name': place.name,
                'Address': place.formatted_address,
                'Phone': place.international_phone_number \
                    if place.international_phone_number is not None \
                    else place.local_phone_number
            }
            # if place.website is not None:
            #     iplace['Site'] = place.website
            # else:
            dist, dur, value = get_distance(location, place.formatted_address)
            if value > radius*8:
                continue
            iplace['Site'] = place.website
            iplace['Distance'] = dist
            iplace['Duration'] = dur

            results.append(iplace)
            icount += 1

        else:
            continue

        if count == icount:
            break

    if len(results) > 0:
        if get_image:
            markers = [f'size:mid|color:yellow|label:{i + 1}|' + results[i]['Address'] for i in range(len(results))]
            markers.append(location)
            return get_locations_img(markers, zoom), results,\
                   f'https://www.google.com/maps/search/?api=1&query={build_type}+{location.replace(" ", "+")}'
        return results
    return 0


def get_distance(origin, destination):
    url = 'https://maps.googleapis.com/maps/api/distancematrix/json'
    params = {
        'origins': origin,
        'destinations': destination,
        'key': YOUR_API_KEY,
        'language': lang.RUSSIAN,
        'mode': 'walking'
    }
    response = requests.request("GET", url, params=params).json()

    return response['rows'][0]['elements'][0]['distance']['text'], response['rows'][0]['elements'][0]['duration'][
        'text'], response['rows'][0]['elements'][0]['distance']['value']



def get_locations_img(location, zoom, markers=False):
    url = 'https://maps.googleapis.com/maps/api/staticmap'
    params = {
        'center': location,
        'zoom': zoom,
        'size': '500x400',
        'key': YOUR_API_KEY,
        'language': lang.RUSSIAN,
        'markers': markers if markers else location
    }
    response = requests.request('GET', url, params=params)
    img = Image.open(BytesIO(response.content)).convert('RGB')

    # img.save('test.jpg')
    return response.content

