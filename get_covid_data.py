import io
import requests
import datetime
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from functools import lru_cache
import bs4
import json


def get_regions():
    regions_url = 'https://covid-api.com/api/regions'
    response = requests.request("GET", regions_url).json()
    return {i['name']: i['iso'] for i in response['data']}


def get_report(iso, date=datetime.datetime.now().date() - datetime.timedelta(days=2)):
    report_url = 'https://covid-api.com/api/reports'
    response = requests.request("GET", report_url, params={'date': date, 'iso': iso}).json()

    res = {'date': date}
    for i in response['data']:
        res['confirmed'] = res.get('confirmed', 0) + i['confirmed']
        res['deaths'] = res.get('deaths', 0) + i['deaths']
        res['recovered'] = res.get('recovered', 0) + i['recovered']
        res['confirmed_diff'] = res.get('confirmed_diff', 0) + i['confirmed_diff']
        res['deaths_diff'] = res.get('deaths_diff', 0) + i['deaths_diff']
        res['recovered_diff'] = res.get('recovered_diff', 0) + i['recovered_diff']
        res['active'] = res.get('active', 0) + i['active']
        res['active_diff'] = res.get('active_diff', 0) + i['active_diff']

    res['fatality_rate'] = res.get('deaths', 0) / res.get('confirmed', 1)

    return res


def get_total_report(date=datetime.datetime.now().date() - datetime.timedelta(days=1)):
    report_url = 'https://covid-api.com/api/reports/total'
    response = requests.request("GET", report_url, params={'date': date}).json()
    return response['data']

# print(get_regions())
# print(get_report("AUS"))


# получение списка стран, словарь "русское название: ISO" в reg_iso_ru
with open('countries.txt', 'r', encoding='utf-8') as countries_file:
    countries_list = countries_file.read().split('\n')
    countries_dict = {}
    for i in countries_list:
        country = i.split('\t')
        countries_dict[country[1]] = country[0]

reg_dict = get_regions()
reg_iso_ru = {}

for i in reg_dict.keys():
    if i in countries_dict.keys():
        reg_iso_ru[countries_dict[i].lower()] = reg_dict[i]
    else:
        print(f"MISMATCH: {i}")


def get_report_ru(country, *kwargs):
    iso = reg_iso_ru[country]
    return get_report(iso, kwargs)


def get_total_report_ru(country, *kwargs):
    iso = reg_iso_ru[country]
    return get_total_report(iso, kwargs)


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + datetime.timedelta(n)


def get_dynamic_plot(country, end_date=False, start_date=False):

    if not end_date or end_date == datetime.datetime.now().date():
        end_date = datetime.datetime.now().date() - datetime.timedelta(days=2)
    if not start_date:
        start_date = end_date - datetime.timedelta(days=7)

    if start_date > end_date:
        start_date, end_date = end_date, start_date

    data = pd.DataFrame()
    countdate = 0
    for date in daterange(start_date, end_date):
        idata = get_report_ru(country, date.strftime('%Y-%m-%d'))

        idata['date'] = date.strftime('%Y-%m-%d')

        idata = pd.DataFrame({k: [v] for k, v in idata.items()})
        data = data.append(pd.DataFrame(idata)).reset_index(drop=True)[['date', 'confirmed',
                                                                        'recovered', 'deaths', 'active']]

        countdate += 1

    if len(data) == 0:
        return 0

    data = data.rename(columns={
        'confirmed': 'Заражённых всего',
        'active': 'Заражённых сейчас',
        'recovered': 'Выздоровевших',
        'deaths': 'Умерших'
    })

    data = pd.melt(data, id_vars=['date'], value_vars=['Заражённых всего', 'Заражённых сейчас',
                                                       'Выздоровевших', 'Умерших'])

    data = data.rename(columns={'variable': 'Легенда'})

    plt.figure()
    if 10 < countdate <= 20:
        height = 8
    elif 20 < countdate <= 30:
        height = 12
    elif 30 < countdate:
        height = 15
    else:
        height = 5

    g = sns.catplot(x='date', y='value', hue='Легенда', data=data, kind='point', height=height)

    (g.set_axis_labels("", "Кол. человек")
     .set_xticklabels(rotation=60)
     .despine(left=True))

    buf = io.BytesIO()
    g.savefig(buf, format='jpg')
    # g.savefig('test.jpg')

    return buf.getvalue(), get_report_ru(country, end_date.strftime('%Y-%m-%d'))


def get_ru_regions_data(*regions):
    data = requests.get("https://стопкоронавирус.рф/information/").text

    doc = bs4.BeautifulSoup(data, "html.parser")
    objs = json.loads(doc.select_one('cv-spread-overview')[':spread-data'])
    res = []
    if len(regions) > 0:
        for obj in objs:
            if obj['title'] not in regions:
                continue
            res.append({
                'name': obj['title'],
                'confirmed': obj['sick'],
                'recovered': obj['healed'],
                'deaths': obj['died'],
                'active': obj['sick'] - obj['healed'] - obj['died'],
                'confirmed_diff': obj['sick_incr'],
                'recovered_diff': obj['healed_incr'],
                'deaths_diff': obj['died_incr'],
                'active_diff': obj['sick_incr'] - obj['healed_incr'] - obj['died_incr'],
                'fatality_rate': obj['died'] / obj.get('sick', 1)
            })
    else:
        for obj in objs:
            res.append({
                'name': obj['title'],
                'confirmed': obj['sick'],
                'recovered': obj['healed'],
                'deaths': obj['died'],
                'active': obj['sick'] - obj['healed'] - obj['died'],
                'confirmed_diff': obj['sick_incr'],
                'recovered_diff': obj['healed_incr'],
                'deaths_diff': obj['died_incr'],
                'active_diff': obj['sick_incr'] - obj['healed_incr'] - obj['died_incr'],
                'fatality_rate': obj['died'] / obj.get('sick', 1)
            })

    return res


# print(get_dynamic_plot('Россия'))

