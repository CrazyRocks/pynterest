"""
Модуль для загрузки ссылок фотографий из соцсети pinterest.ru

Иногда программа выдаёт ошибку , так как не может использовать выбранный proxy .
В этом случае следует попробовать ещё раз . Пока не успеваю исправить .
"""

import os
import sys
import requests
import requests.cookies
import urllib
import json
import csv
import time
import datetime

from proxy_search import get_new_proxy

HOME_URL = 'https://www.pinterest.ru'
PIN_ID_URL = 'https://www.pinterest.ru/_ngjs/resource/UserExperienceResource/get/'
LOGIN_URL = 'https://accounts.pinterest.com/v3/login/handshake/'
NEW_COOKIE_URL = 'https://www.pinterest.ru/resource/HandshakeSessionResource/create/'
GET_IMGS_URL = 'https://www.pinterest.ru/_ngjs/resource/UserHomefeedResource/get/?source_url=&data\
                 ={{"options":{{"bookmarks":["{0}"],"isPrefetch":false,"field_set_key":"hf_grid",\
                 "in_nux":false,"prependPartner":false,"prependUserNews":false,"repeatRequestBookmark":"",\
                 "static_feed":false}},"context":{{}}}}&_={1}'
Origin = HOME_URL
Referer = HOME_URL + '/'
USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) \
             Chrome/73.0.3683.103 Safari/537.36 OPR/60.0.3255.70'
HOME_URL_0 = HOME_URL[8:]
FOLDER_URLS = 'URLS'
CHECK_LIST = ['https://www.pinterest.ru/_ngjs/resource/UserHomefeedResource/get',
              'https://www.pinterest.ru/resource/BaseSearchResource/get/']

class Pynterest () :
    def __init__ (self, username_or_email, password) :
        self.LOGIN = username_or_email
        self.PASSWORD = password
        self.Logged_In = False
        self.SESSION = requests.Session()
        self.HEADERS = {'User-Agent': USER_AGENT, 'Referer': Referer, 'Origin': Origin}
        self.COOKIES = None
        self.HELP_COOKIES = None
        self.DATA = None
        self.PARAMETERS = None
        self.URL = HOME_URL
        self.RESPONSE = None
        self.Pinterest_InstallID = None
        self.MAX = 15
        self.IMGS = 0
        self.continue_extraction = True
        self.DATE = '{0}_{1}_{2}'.format(datetime.date.today().year,datetime.date.today().month,datetime.date.today().day)
        for i in range (3) :
            try :
                self.PROXY = get_new_proxy (MAX=30)
                print('ПОДКЛЮЧИЛСЯ К PROXY')
                break
            except :
                print('НЕ УДАЛОСЬ ПОДКЛЮЧИТЬСЯ К PROXY...')
        if not FOLDER_URLS in os.listdir('.') :
            os.mkdir(FOLDER_URLS)
        self.FOLDER_PATH = os.getcwd()+'/'+FOLDER_URLS+'/'

    def _Check_Response_Code(self) :
        code = self.RESPONSE.status_code
        if code == 200 :
            if not (CHECK_LIST[0] in self.URL or CHECK_LIST[1] in self.URL) :
                print (self.URL,'.'*10,'OK')
        elif code == 429 :
            print('ПРЕВЫШЕНО КОЛИЧЕСТВО ЗАПРОСОВ К СЕРВЕРУ. ИЗМЕНЕНИЕ IP')
            self.PROXY = get_new_proxy (self.MAX)
            self._Request ()
        elif code == 401 :
            print ('САЙТ ЗАМЕТИЛ ПОДОЗРИТЕЛЬНУЮ АКТИВНОСТЬ НА ВАШЕЙ СТРАНИЦЕ. ИЗМЕНИТЕ ПАРОЛЬ')
            sys.exit(1)
        elif code == 404 :
            print ('СТРАНИЦА НЕ НАЙДЕНА. ВОЗМОЖНО ВОЗНИКЛА ОШИБКА В ЗАПРОСЕ')
            sys.exit(1)

    def _Request (self) :
        self.RESPONSE = self.SESSION.request (self.METHOD, self.URL, headers = self.HEADERS, cookies = self.COOKIES,
                                                   params = self.PARAMETERS, proxies = self.PROXY, data = self.DATA )
        self._Check_Response_Code ()

    def _get_Pinterest_InstallId (self) :
        self.URL = PIN_ID_URL
        self.COOKIES = self.RESPONSE.cookies
        self.HEADERS = {'user-agent': USER_AGENT,
                        'referer': Referer,
                        'accept': 'application/json, text/javascript, */*, q=0.01',
                        'accept-encoding': 'gzip, deflate, br',
                        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
                        'dnt': 1,
                        'x-app-version': 'c4f4136',
                        'x-pinterest-appstate': 'active',
                        'x-requested-with': 'XMLHttpRequest'}
        self.PARAMETERS = {'source_url':'/',
                           'data':'{"options":{"placement_ids":[1000154],"extra_context":{}},"context":{}}',
                           '_':str(int(time.time()*1000))}
        self.METHOD = 'get'
        self._Request ()
        second_request_text = self.RESPONSE.text
        N = second_request_text.find('"user":{"unauth_id"')
        self.Pinterest_InstallID = second_request_text.split('"')[5]

    def _auth (self) :
        self.HELP_COOKIES = self.COOKIES
        self.COOKIES = self.RESPONSE.cookies
        self.URL = LOGIN_URL
        self.HEADERS = {'User-Agent': USER_AGENT,
                        'Referer': Referer,
                        'Origin': Origin,
                        'Content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                        'DNT' : 1,
                        'X-Pinterest-InstallId' : self.Pinterest_InstallID}
        self.DATA = {'username_or_email': self.LOGIN , 'password': self.PASSWORD}
        self.PARAMETERS = None
        self.METHOD = 'post'
        self._Request ()
        self.TOKEN = self.RESPONSE.json()['data']

    def _get_logged_in_cookies ( self ) :
        self.COOKIES = self.HELP_COOKIES
        self.URL = NEW_COOKIE_URL
        self.HEADERS = {'accept': 'application/json, text/javascript, */*, q=0.01',
                        'accept-encoding': 'gzip, deflate, br',
                        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
                        'content-length': 160,
                        'content-type': 'application/x-www-form-urlencoded',
                        'dnt': 1,
                        'origin': Origin,
                        'referer': Referer,
                        'user-agent': USER_AGENT,
                        'x-app-version': '7e3785e',
                        'x-csrftoken': self.COOKIES['csrftoken'],
                        'x-pinterest-appstate': 'active',
                        'x-requested-with': 'XMLHttpRequest'}
        self.DATA = {'data':json.dumps({ "options":{"token":self.TOKEN,"isRegistration":'false'},
                                         "context":{}}).replace(' ','') ,
                     'source_url' : '/'}
        self.METHOD = 'post'
        self._Request ()
        self.Logged_In = True

    def _go_home (self) :
        if self.Logged_In :
            self.COOKIES = self.RESPONSE.cookies
        if self.URL == HOME_URL :
            return
        self.URL = HOME_URL
        self.PARAMETERS = None
        self.DATA = None
        self.HEADERS = {'Accept': 'text/html, application/xhtml+xml, aplication/xml; q=0.9, */*; q=0.8',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'Accept-Language': 'en-US,en;q=0.5',
                        'Connection': 'keep-alive',
                        'Host': HOME_URL_0,
                        'Upgrade-Insecure-Requests': 1,
                        'User-Agent': USER_AGENT}
        self.METHOD = 'get'
        self._Request ()

    def _save_img_url (self, img) :
        with open (self.FOLDER_PATH+self.FILENAME, 'a') as file :
            order = ['orig', '170x', '736x', '474x', '236x']
            writer = csv.DictWriter (file, fieldnames=order)
            writer.writerow (img)

    def _Find_In_HTML (self, text, N) :
        Continue = True
        while Continue :
            if self.IMGS == N :
                self.continue_extraction = False
                return
            N_start = text.find('src="https://i.pinimg.com/')
            N_stop = text.find('src="https://i.pinimg.com/', N_start+1)
            if N_stop == -1 :
                N_stop = text.find ('script', N_start+1)
                Continue = False
            L = text[N_start:N_stop].split('"')
            if not ('https://i.pinimg.com/' in L[3]) :
                text = text[N_stop:]
                continue
            hrefS = L[1:4:2]
            variants = hrefS[1].split(' ')
            l = [i for i in variants[0:7:2]]
            l.append(hrefS[0])
            print(variants[6])
            order = ['236x', '474x', '736x', 'orig', '170x']
            D = {order[i] : l[i] for i in range(5)}
            self._save_img_url (D)
            self.IMGS += 1
            text = text [N_stop:]
        Position = text.rfind('nextBookmark')
        NextBookmark = text [Position:Position+1100].split('"')[2]
        if len(NextBookmark) <  50 :
            Position = text.find('nextBookmark')
            NextBookmark = text [Position:Position+1100].split('"')[2]
        return NextBookmark

    def _Find_In_Json (self, text, N) :
        resource_response = json.loads(text)['resource_response']
        for one in resource_response['data'] :
            if self.IMGS == N :
                self.continue_extraction = False
                return
            D = dict ()
            for type in one['images'].keys() :
                if type == 'orig' :
                    print(one['images']['orig']['url'])
                #size = '|' + 'width'+str(types[t]['width'])+'|'+'height'+str(types[t]['height'])
                size = ''
                D[type] = one['images'][type]['url']+size
            self._save_img_url (D)
            self.IMGS += 1
        return resource_response['bookmark']

    def _json_analys ( self , N ) :
        JS = json.loads(self.RESPONSE.text)
        for img in JS['resource_response']['data']['results'] :
            if self.IMGS == N :
                self.continue_extraction = False
                return
            D = dict ()
            types = img['images']
            for t in types :
                if t == 'orig' :
                    print(img['images']['orig']['url'])
                #size = '|' + 'width'+str(types[t]['width'])+'|'+'height'+str(types[t]['height'])
                size = ''
                D [t] = types[t]['url'] + size
            self._save_img_url(D)
            self.IMGS += 1
        NextBookmark = JS['resource']['options']['bookmarks'][0]
        return NextBookmark

    def login ( self ) :
        # Зайти на сайт после создания объекта и передачи логина (почты) и пароля
        self.METHOD = 'get'
        self._Request ( )
        self._get_Pinterest_InstallId ( )
        self._auth ( )
        self._get_logged_in_cookies ( )
        self._go_home ( )

    def parse_home_page (self, N=30 ) :
        # Скачать изображения с домашней страницы пользователя (N штук)
        self.FILENAME = 'IMAGES_{}_from_home_page.csv'.format(self.DATE)
        self._go_home ()
        self.continue_extraction = True
        self._Find_In_HTML (self.RESPONSE.text ,N)
        NextBookmark = self._Find_In_HTML (self.RESPONSE.text ,N)
        while self.continue_extraction :
            self.URL = GET_IMGS_URL.format (NextBookmark, str(int(time.time()*1000)))
            self.COOKIES = self.COOKIES
            self.DATA = None
            self.PARAMETERS = None
            self.HEADERS = {'Accept':'application/json, text/javascript, */*, q=0.01',
                            'Accept-Encoding':'gzip, deflate, br',
                            'Accept-Language':'en-US,en;q=0.5',
                            'Connection':'keep-alive',
                            'Host':HOME_URL_0,
                            'Referer':Referer,
                            'User-Agent' : USER_AGENT,
                            'X-APP-VERSION':'7e3785e',
                            'X-Pinterest-AppState':'active',
                            'X-Requested-With':'XMLHttpRequest'}
            self.METHOD = 'get'
            self._Request ()
            NextBookmark = self._Find_In_Json (self.RESPONSE.text, N)

    def parse_searched_page (self, query, N=30 ) :
        # Скачать изображения , найденные pinterest.ru по запросу query (N штук)
        self.FILENAME = 'IMAGES_{0}_{1}.csv'.format(self.DATE,query.replace(' ','_'))
        self.URL = 'https://www.pinterest.ru/resource/BaseSearchResource/get/'
        self.COOKIES = self.COOKIES
        self.DATA = None
        self.PARAMETERS = {'source_url': '/search/pins/?{}'.format(urllib.parse.urlencode ( { 'q': query , 'rs' : 'typed' , 'term_meta[]' : '{}|typed'.format(query) } )) ,
                           'data':'{{"options":{{"isPrefetch":false,"article":null,"auto_correction_disabled":false,"corpus":null"customized_rerank_type":null,"filters":null,"page_size":null,\
                                   "query":"{0}","query_pin_sigs":null,"redux_normalize_feed":true,"rs":"typed","scope":"pins","source_id":null}},"context":{{}}}}'.format(query),
                           '_':str(int(time.time()*1000))}
        
        self.HEADERS = {'accept': 'application/json, text/javascript, */*, q=0.01',
                        'accept-encoding': 'gzip, deflate, br',
                        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
                        'dnt': 1 ,
                        'referer': Referer,
                        'user-agent': USER_AGENT,
                        'x-app-version': '7e3785e',
                        'x-pinterest-appstate': 'active',
                        'x-requested-with': 'XMLHttpRequest'}
        self.METHOD = 'get'
        self._Request ()
        NextBookmark = self._json_analys (N)
        while self.continue_extraction :
            self.PARAMETERS = None
            self.HEADERS = {'accept': 'application/json, text/javascript, */*, q=0.01',
                            'accept-encoding': 'gzip, deflate, br',
                            'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
                            'content-length': 2397,
                            'content-type': 'application/x-www-form-urlencoded',
                            'dnt': 1,
                            'origin': Origin,
                            'referer': Referer,
                            'user-agent': USER_AGENT,
                            'x-app-version': '7e3785e',
                            'x-csrftoken': self.COOKIES['csrftoken'] ,
                            'x-pinterest-appstate': 'background',
                            'x-requested-with': 'XMLHttpRequest'}
            self.DATA = {'source_url': '/search/pins/?{}'.format(urllib.parse.urlencode ( { 'q': query , 'rs' : 'typed' , 'term_meta[]' : '{}|typed'.format(query) } )) ,
                         'data' : '{{"options":{{"bookmarks":["{0}"],"isPrefetch":false,"article":null,"auto_correction_disabled":false,"corpus":null,\
                                    "customized_rerank_type":null,"filters":null,"page_size":null,"query":"{1}","query_pin_sigs":null,\
                                    "redux_normalize_feed":true,"rs":"typed","scope":"pins","source_id":null}},"context":{{}}}}'.format(NextBookmark,query)}
            self.METHOD = 'post'
            self._Request ()
            NextBookmark = self._json_analys(N)
