from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from datetime import date, timedelta, datetime
import time
import requests


origin = 'BER'
destination = 'BCN'
start_date = '2019-07-10'

headers = {
    'User-Agent': "Firefox/66.0.3"
}



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


url = f'https://www.kayak.pl/flights/{origin}-{destination}/{start_date}?sort=bestflight_a&fs=stops=0'

# r = requests.get(url, headers=headers)

# with open('request.html', 'w', encoding='utf-8') as f:
#     f.write(r.text)

r = ''

with open('request.html', 'r', encoding='utf-8') as f:
    r = f.read()

soup = BeautifulSoup(r, 'lxml')

if soup.find_all('p')[0].getText() == "Please confirm that you are a real KAYAK user.":
    print('BOT ERROR')

else:
    prices = list()

    departure_times_dirty = soup.find_all('span', attrs={'class': 'depart-time base-time'})
    arrival_times_dirty = soup.find_all('span', attrs={'class': 'arrival-time base-time'})
    prices_list = soup.find_all('div', attrs={'class': 'Common-Booking-MultiBookProvider featured-provider cheapest multi-row Theme-featured-large'})

    departure_times = [departure_time.text for departure_time in soup.find_all('span', attrs={'class': 'depart-time base-time'})]
    arrival_times = [arrival_time.text for arrival_time in soup.find_all('span', attrs={'class': 'arrival-time base-time'})]

    for price in prices_list:
        price = price.find('span', attrs={'class': 'price option-text'})

        text = price.text
        currency = text[-3:-1]
        text = text[1:-2][:-2]

        prices.append(f'{text} {currency}')

data = {
    'origin': origin,
    'destination': destination,
    'date': start_date,
    'departure_time': departure_times,
    'arrival_time': arrival_times,
    'price': prices
}

df = pd.DataFrame(data)

print(df)
