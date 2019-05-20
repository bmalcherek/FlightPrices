from bs4 import BeautifulSoup
import pandas as pd
import re
import numpy as np
from datetime import datetime
import time
import requests
from user_agent import generate_user_agent


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
            r = requests.get('https://www.kayak.pl/flights/BER-MAD/2019-09-01?sort=bestflight_a&fs=stops=0;providers=-ONLY_DIRECT', proxies={"http": proxy, "https": proxy}, timeout=3)
            soup = BeautifulSoup(r.text, 'lxml')
            if soup.find_all('p')[0].getText() == "Potwierdź, że jesteś użytkownikiem KAYAK.":
                print('BOT DETECTED')
                return 'FAIL'
            print('SUCCESS!')
            return proxy
        except:
            print('FAIL')
    return 'FAIL'


def get_page(origin, destination, date):
    url = f'https://www.kayak.pl/flights/{origin}-{destination}/{date}?sort=bestflight_a&fs=stops=0;providers=-ONLY_DIRECT'
    headers = {
        'User-Agent': generate_user_agent(device_type="desktop", os=('mac', 'linux', 'win'))
    }

    # cookies = {
    #     'DATA_CONSENT': 'false',
    #     'Apache': 'Vd2IGg-AAABarH$r2A-a6-V726BA',
    #     'cluster': '4',
    #     'G_ENABLED_IDPS': 'google',
    #     'kayak': 'xHE_nmXpRL7G6xY4gI7Y',
    #     'kayak.mc': 'AVWcmLZve9CC6IBYHZZ83U2u6Hob2FM7yiZb_7GXsI2leqS9sMn2DT7kPdHYUYO3RLHAWdea4C51dqIFRLW0bk2wHnKTUqnWuz'
    #                 'SvbiR64RIeRuA_7sgGYFEF5MmEOdOxCog85rtCIOTXSMv7zvteDnaPA42l4X8N18eWtAIzPFzEaRrb_V9gNqAKC7WVq_ILpTMU'
    #                 'U5p_L-pGTJIy2RM4GmRxv9ft9KEj49wf0f1l_x4uDa3NFQyK2fDJa-JSNk1tw3LZhpqVngxYYwfmz_fumLzoNKflG-s5Ok7JfFC'
    #                 'b0mv3f4PXPDvIFtKIJYEVvpdkKg',
    #     'NSC_q4-tqbslmf': 'ffffffff094fbfc345525d5f4f58455e445a4a422a59',
    #     '_pxhd': '""',
    #     'p1.med.sid': 'H-4QNu7IXvYXlE47hyJJ6VG-HB0FIPyeAw9IbxIqAwpw9XCbIFFoYMT5y_5sYNSfL',
    #     'xp-session-seg': 'control14',
    #     'vid': '2fd6884c-759b-11e9-a6f9-0242ac120009',
    #     'kykprf': '354',
    #     'p1.med.sc': '24'
    # }

    # proxy = getWorkingProxy()
    # while proxy == 'FAIL':
    #     proxy = getWorkingProxy()
    #
    # proxies = {
    #     'http': proxy,
    #     'https': proxy
    # }

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

    departure_times = [departure_time.text for departure_time in
                       soup.find_all('span', attrs={'class': 'depart-time base-time'})]
    arrival_times = [arrival_time.text for arrival_time in
                     soup.find_all('span', attrs={'class': 'arrival-time base-time'})]

    regex = re.compile('Common-Booking-MultiBookProvider (.*)multi-row Theme-featured-large(.*)')
    for price in soup.find_all('div', attrs={'class': regex}):
        price = price.find('span', attrs={'class': 'price option-text'}).text[1:]
        prices.append(price)

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

    return df

origins = ['BER', 'POZ', 'WRO', 'WAW']
destinations = ['MAD', 'BCN', 'PAR']
dates = ['2019-09-01', '2019-09-02']

requests_count = 0

# for origin in origins:
#     for destination in destinations:
#         for date in dates:
#             while get_page(origin, destination, date) != 'success':
#                 time.sleep(3)
            # print(headers)
            # requests_count += 1
            # scrape(origin, destination, date, headers)
            # time.sleep(15)
