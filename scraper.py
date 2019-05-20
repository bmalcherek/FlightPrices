from bs4 import BeautifulSoup
import pandas as pd
import re
import numpy as np
from datetime import datetime
import time
import requests
from user_agent import generate_user_agent


def get_page(origin, destination, date):
    url = f'https://www.kayak.pl/flights/{origin}-{destination}/{date}?sort=bestflight_a&fs=stops=0;providers=-ONLY_DIRECT'
    headers = {
        'User-Agent': generate_user_agent(device_type="desktop", os=('mac', 'linux', 'win'))
    }

    print(f'{url}\n{headers}')

    try:
        r = requests.get(url, headers=headers)
    except requests.exceptions.ProxyError:
        return 'FAIL'

    soup = BeautifulSoup(r.text, 'lxml')
    if soup.find_all('p')[0].getText() == "Potwierdź, że jesteś użytkownikiem KAYAK.":
        print('BOT DETECTED')
        return 'fail'

    if soup.find_all('p')[0].getText() == "Please confirm that you are a real KAYAK user.":
        print("Kayak thinks I'm a bot, which I am ... so let's wait a bit and try again")
        return 'fail'

    with open(f'requests/request-{origin}-{destination}-{date}.html', 'w', encoding='utf-8') as f:
        f.write(r.text)

    return 'success'


def scrape(origin, destination, date):
    r = ''
    with open(f'requests/request-{origin}-{destination}-{date}.html', 'r', encoding='utf-8') as f:
        r = f.read()
    soup = BeautifulSoup(r, 'lxml')

    prices = list()
    operators = list()
    iata_origin = list()
    iata_destination = list()
    currencies = list()

    departure_times = [departure_time.text for departure_time in
                       soup.find_all('span', attrs={'class': 'depart-time base-time'})]
    arrival_times = [arrival_time.text for arrival_time in
                     soup.find_all('span', attrs={'class': 'arrival-time base-time'})]

    regex = re.compile('Common-Booking-MultiBookProvider (.*)multi-row Theme-featured-large(.*)')
    for price in soup.find_all('div', attrs={'class': regex}):
        price = price.find('span', attrs={'class': 'price option-text'}).text[1:]
        prices.append(int(price[:-4]))
        currencies.append(price[-3:-1])

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
        'operator': operators,
        'currency': currencies,
        'price': prices
    }

    df = pd.DataFrame(data)

    return df

