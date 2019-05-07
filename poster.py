"""
Модуль для загрузки фотографий на компьютер и последующей публикации в группе
"""

import vk_api
import httplib2
import csv
import os

class VK_process :
    def __init__ ( self , number , password , user_id , group_id , application_id ,  access_key , FOLDER_PCTRS , FOLDER_URLS , FILE_NAME  , version = '5.92'  ) :
        self.NUMBER =   number
        self.PASSWORD = password
        self.USER_ID = user_id
        self.GROUP_ID = group_id
        self.APPLICATION_ID = application_id
        self.VERSION = version
        self.ACCESS_KEY = access_key
        self.HERE = os.getcwd()
        self.FOLDER_PCTRS = FOLDER_PCTRS
        self.FOLDER_URLS = FOLDER_URLS
        self.FILE_NAME = FILE_NAME
        if not self.FOLDER_PCTRS in os.listdir('.') :
            os.mkdir(self.FOLDER_PCTRS )
        os.chdir('./'+self.FOLDER_PCTRS)
        if not FILE_NAME in os.listdir('.') :
            os.mkdir(self.FILE_NAME)
        os.chdir('..')

    def _AuthentificationHandler ( self , remember_my_device = True ) :
        # ОБРАБОТКА ДВУХФАКТОРНОЙ АУТЕНТИФИКАЦИИ
        KEY = str(input('ВВЕДИТЕ КОД ПОДТВЕРЖДЕНИЯ : '))
        return KEY , remember_my_device

    def _CaptchaHandler ( self , captcha ) :
        # ОБРАБОТКА КАПЧИ
        # ввод кода с картинки по адресу
        KEY = input("ВВЕДИТЕ КОД С КАПЧИ {0}: ".format(captcha.get_url())).strip()
        return captcha.try_again(key)

    def activate_api (self) :
        self.PROCESS = vk_api.vk_api.VkApi (login = self.NUMBER ,
                                            password = self.PASSWORD ,
                                            auth_handler = self._AuthentificationHandler,
                                            captcha_handler = self._CaptchaHandler ,
                                            api_version = self.VERSION ,
                                            app_id = self.APPLICATION_ID ,
                                            scope = 8196 ,
                                            client_secret = self.ACCESS_KEY )
        self.PROCESS.auth( token_only = True )
        self.METHODS = self.PROCESS.get_api()

    def activate_upload_object (self) :
        self.UPLOAD_OBJECT = vk_api.upload.VkUpload ( self.METHODS )

    def _download_picture ( self , url ) :
        h = httplib2.Http('.cache')
        response, content = h.request(url)
        if response.status != 200 :
            print (url,'.'*10,'WRONG')
            return
        name = '{0}/{1}/{2}/{3}'.format(self.HERE,self.FOLDER_PCTRS,self.FILE_NAME,url[7:].replace('/','_'))
        out = open(name , "wb")
        out.write(content)
        out.close()
        print(url,'.'*10,'OK')
        return name

    def _upload_photo ( self , name ) :
        response = self.UPLOAD_OBJECT.photo_wall ( name , user_id = self.USER_ID , group_id = self.GROUP_ID )
        attachments = "photo{0}_{1}_{2}".format(self.USER_ID,response[0]['id'],response[0]['access_key'])
        id = self.METHODS.wall.post(message=None,owner_id=-self.GROUP_ID,from_group=1,attachments=attachments)
        return id

    def _write_id ( self , data ) :
        with open ( self.HERE+'/'+self.FOLDER_URLS+'/'+self.FILE_NAME+"_POST_ID.csv" , 'a') as file :
            order = [ 'id' , 'url' ]
            writer = csv.DictWriter ( file , fieldnames = order )
            writer.writerow (data)

    def upload_csv_dict ( self ) :
        with open (self.HERE+'/'+self.FOLDER_URLS+'/'+self.FILE_NAME , 'r' ) as file :
            fieldnames = [ 'orig' , '170x' , '736x' , '474x' , '236x' ]
            reader = csv.DictReader (file,fieldnames=fieldnames)
            for row in reader :
                name = self._download_picture ( row['474x'] )
                id = self._upload_photo ( name )
                self._write_id ({'id':id,'url':name})
