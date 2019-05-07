"""
Модуль парсит сайт с прокси , отбирает подходящие по scheme и возвращает 1 из выбранных
"""

import requests
from bs4 import BeautifulSoup
from random import choice


PROXY_URL = 'https://free-proxy-list.net'
# Использовать прокси для поиска прокси ? При True работает очень медленно
PROXY_FOR_PROXY = None
# Какая схема нужна ? ['yes'] = 'HTTPS' , ['no'] = 'HTTP' , ['yes','no'] = HTTP+HTTPS
NEED = ['yes']
# TIMEOUT проверки ip
TIME_OUT_CHECK = 30
# TIMEOUT поиска прокси
TIME_OUT_SEARCH = 15

# Сайты для определения ip ( изменилось или нет )
IP_HTTP_URL = 'http://httpbin.org/ip'
IP_HTTPS_URL = 'https://2ip.ua/ru/'


def get_HTML (url, proxy=None) :
    rspns = requests.get (url, proxies = proxy, timeout = TIME_OUT_SEARCH)
    if rspns.status_code != 200 :
        print ('ERROR {} . I CANT CONNECT TO THE PROXY LIST'.format(rspns.status_code))
        exit(1)
    return rspns.text


def get_proxies_list (html, MAX=50) :
    soup = BeautifulSoup (html, 'lxml')
    table_body = soup.find('table',id='proxylisttable').find('tbody')
    trs = table_body.find_all('tr', recursive=False)
    lenght = len (trs)
    iCkeck = 0
    PROXY_LIST =  []
    while (iCkeck < lenght) and len(PROXY_LIST) < MAX :
        tds = trs[iCkeck].find_all('td')
        if tds[6].text in NEED :
            DATA =   dict()
            DATA['https' if tds[6].text == 'yes' else 'http'] = '{0}:{1}'.format(tds[0].text,tds[1].text)
            PROXY_LIST.append(DATA)
        iCkeck += 1
    return PROXY_LIST


def get_new_proxy (MAX=30) :
    # Возвращает адрес прокси сервера
    global PROXY_FOR_PROXY
    hyper_text = get_HTML (PROXY_URL, PROXY_FOR_PROXY)
    P_LIST = get_proxies_list (hyper_text, MAX)
    if not P_LIST :
        print ('НЕ УДАЛОСЬ НАЙТИ PROXY')
        exit(1)
    proxy = choice (P_LIST)
    P_LIST.remove(proxy)
    #PROXY_FOR_PROXY = choice ( P_LIST ) TROUBLES
    return proxy


def ip_HTTP (proxy) :
    # Проверка ip при http соединении
    r = requests.get(IP_HTTP_URL, proxies = proxy, timeout = TIME_OUT_CHECK)
    print ('connected ', end = '')
    IP = r.json()['origin']
    try :
        return IP.split(',')[0]
    except:
        return IP


def ip_HTTPS (proxy) :
    # Проверка ip при https соединении
    r = requests.get(IP_HTTPS_URL, proxies = proxy, timeout= TIME_OUT_CHERK)
    print ('connected ', end = '')
    soup = BeautifulSoup (r.text,'lxml')
    span = soup.find('span', {'class': "copy-clipboard", 'data-toggle': "tooltip"})
    IP = span.get('data-clipboard-text')
    return IP

def test ( ) :
    # Функция для теста модуля
    global NEED
    NEED = ['yes']
    print('\n\nHTTPS PROXIES\n\n',end = '')
    for i in range (10) :
        proxy_s = get_new_proxy (MAX = 25)
        print (proxy_s)
        try :
            print (IP_HTTPS(proxy_s ))
        except :
            print ("ПРОБЛЕМЫ С ОПРЕДЕЛЕНИЕМ IP")
    NEED = ['no']
    print('\n\nHTTP PROXIES\n\n', end = '')
    for i in range ( 10 ) :
        proxy = get_new_proxy (MAX = 25)
        print (proxy)
        try :
            print (IP_HTTP ( proxy ))
        except :
            print ("ПРОБЛЕМЫ С ОПРЕДЕЛЕНИЕМ IP")

if __name__ == "__main__":
    test ( )
