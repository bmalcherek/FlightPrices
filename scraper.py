from bs4 import BeautifulSoup
import pandas as pd
import re
import numpy as np
from datetime import date, timedelta, datetime
import time
import requests


def getProxies():
    proxiesUrl = 'https://free-proxy-list.net/'
    request = requests.get(proxiesUrl).text
    soup = BeautifulSoup(request,'html.parser')
    proxies = set()
    proxiesTable = soup.find(id='proxylisttable')
    # save proxies in list
    for proxyRow in proxiesTable.tbody.find_all('tr'):
        proxies.add(str(proxyRow.find_all('td')[0].string) + ':' + str(proxyRow.find_all('td')[1].string))
    return proxies

def getWorkingProxy():
    proxies = getProxies()
    for proxy in proxies:
        try:
            print(f'Trying {proxy}')
            requests.get('https://httpbin.org/ip', proxies={"http": proxy, "https": proxy}, timeout=3)
            print('SUCCESS!')
            return proxy
        except:
            print('FAIL')


# proxy = getWorkingProxy()
#
# proxies = {
#     'http': proxy,
#     'https': proxy
# }


def scrape(origin, destination, date, headers):

    url = f'https://www.kayak.pl/flights/{origin}-{destination}/{date}?sort=bestflight_a&fs=stops=0'
    print(url)

    r = requests.get(url, headers=headers)

    with open(f'requests/request-{origin}-{destination}-{date}.html', 'w', encoding='utf-8') as f:
        f.write(r.text)

    # r = ''
    #
    # with open('request.html', 'r', encoding='utf-8') as f:
    #     r = f.read()

    soup = BeautifulSoup(r.text, 'lxml')
    if soup.find_all('p')[0].getText() == "Please confirm that you are a real KAYAK user.":
        print('BOT ERROR')
    #
    # else:
    prices = list()
    operators = list()
    iata_origin = list()
    iata_destination = list()

    departure_times = [departure_time.text for departure_time in soup.find_all('span', attrs={'class': 'depart-time base-time'})]
    arrival_times = [arrival_time.text for arrival_time in soup.find_all('span', attrs={'class': 'arrival-time base-time'})]

    regex = re.compile('Common-Booking-MultiBookProvider (.*)multi-row Theme-featured-large(.*)')
    for price in soup.find_all('div', attrs={'class': regex}):
        price = price.find('span', attrs={'class': 'price option-text'}).text[1:]
        prices.append(price)

    # for price in soup.find_all('div', attrs={'class': 'Common-Booking-MultiBookProvider featured-provider cheapest multi-row Theme-featured-large'}):
    #     price = price.find('span', attrs={'class': 'price option-text'}).text
    #     currency = price[-3:-1]
    #     price = price[1:-2][:-2]
    #
    #     prices.append(f'{price} {currency}')

    for operator in soup.find_all('div', attrs={'class': 'section times'}):
        operators.append(operator.find('div', attrs={'class': 'bottom'}).text)

    for iata in soup.find_all('div', attrs={'class': 'section duration'}):
        iata_origin.append(iata.find('div', attrs={'class': 'bottom'}).find('span').text)

    for iata in soup.find_all('div', attrs={'class': 'section duration'}):
        iata_destination.append(iata.find('div', attrs={'class': 'bottom'}).find_all('span')[2].text)

    data = {
        'origin': iata_origin,
        'destination': iata_destination,
        'date': date,
        'departure_time': departure_times,
        'arrival_time': arrival_times,
        'price': prices,
        'operator': operators
    }

    df = pd.DataFrame(data)

    print(df)


# origin = 'BER'
# destination = 'BCN'
# date = '2019-07-10'

origins = ['BER', 'WRO', 'POZ']
destinations = ['BCN', 'LON']
dates = ['2019-09-01', '2019-09-02']


agents = ["Firefox/66.0.3", "Chrome/73.0.3683.68", "Edge/16.16299"]

requests_count = 0

for origin in origins:
    for destination in destinations:
        for date in dates:
            headers = {
                'User-Agent': agents[requests_count % len(agents)]
            }
            requests_count += 1
            scrape(origin, destination, date, headers)
            time.sleep(15)
