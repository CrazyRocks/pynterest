"""
Модуль управления.
"""

from pinterest import Pynterest
from poster import VK_process


# Почта аккаунта на pinterest.ru
MAIL = 'mail'
# Пароль от аккаунта pinterest.ru
PIN_PASSWORD = 'password'

# id группы ВК , админом которой Вы являетесь
GROUP_ID = None
# id приложения вк
APPLICATION_ID = None
# Ваш id
USER_ID = None
# Номер телефона
NUMBER = None
# Пароль от вк
VK_PASSWORD = None
# Версия vk api
VERSION = '5.92'
# сервисный ключ доступа приложения
ACCESS_KEY = None
# папка для сохранения картинок ( относительный путь )
FOLDER_PCTRS = 'pictures'
# папка для сохранения csv со ссылками не картинки ( относительный путь )
FOLDER_URLS = 'URLS'

FOLDER_PCTRS = 'pictures'
FOLDER_URLS = 'URLS'
print('ПОИСК ФОТОГРАФИЙ')

P = Pynterest (MAIL, PIN_PASSWORD)
P.login()
# 'cat' - запрос , N - количество фотографий
P.parse_searched_page ('cat', N=40)
FILE_NAME = P.FILENAME

print('ПУБЛИКАЦИЯ ФОТОГРАФИЙ')

V = poster.VK_process (NUMBER, VK_PASSWORD, USER_ID, GROUP_ID, APPLICATION_ID, ACCESS_KEY, FOLDER_PCTRS, FOLDER_URLS, FILE_NAME, VERSION)
V.activate_api ()
V.activate_upload_object ()
V.upload_csv_dict ()
