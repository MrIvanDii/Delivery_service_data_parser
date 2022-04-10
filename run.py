import time
from pprint import pprint
import requests
from fake_useragent import UserAgent
import multiprocessing
import httplib2
from apiclient import discovery
from oauth2client.service_account import ServiceAccountCredentials
import os

# fake useragent
ua = UserAgent()

# Файл, полученный в Google Developer Console
CREDENTIALS_FILE = '../../../Desktop/source/creds.json'

# ID Google Sheets документа (можно взять из его URL)
spreadsheet_id = '..._...-....-...-...'

# Авторизуемся и получаем service — экземпляр доступа к API
credentials = ServiceAccountCredentials.from_json_keyfile_name(
    CREDENTIALS_FILE,
    ['https://www.googleapis.com/auth/spreadsheets',
     'https://www.googleapis.com/auth/drive'])

httpAuth = credentials.authorize(httplib2.Http())

service = discovery.build('sheets', 'v4', http=httpAuth)

COUNT = 25


def get_data(height, weight, width, length, country, zip_code):
    try:
        headers = {
            'accept': 'application / json, text / plain, * / *',

            # token аккаунта
            'authorization': '............................................',

            'user-agent': ua.random
        }

        r = requests.get(
            f'https://api.packlink.com/v1/services?platform=PRO&platform_country=UN&from%5Bcountry%5D=DE&from%5Bzip'
            
            f'%5D=04827&packages%5B0%5D%5Bheight%5D={height}&packages%5B0%5D%5Blength%5D='
            
            f'{length}&packages%5B0%5D%5Bweight%5D={weight}&packages%5B0%5D%5Bwidth%5D='
            
            f'{width}&sortBy=totalPrice&source=PRO&to%5Bcountry%5D={country}&to%5Bzip%5D={zip_code}',

            headers=headers)

        price = r.json()[0]['base_price']

        return price

    except Exception as ex:
        return ''


def install():
    os.system('pip install -r requirements.txt')


def put_data(height, weight, width, length, i, country, sheet):

    try:

        price_data = []

        zip_codes = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=f"'{sheet}'!A{i}:A{i + COUNT - 1}",
            majorDimension='ROWS'
        ).execute()

        for zip_code in zip_codes['values']:

            zip_code = zip_code[0]

            price = get_data(height, weight, width, length, country, zip_code)

            price_data.append([price])


        values = service.spreadsheets().values().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={
                "valueInputOption": "USER_ENTERED",
                "data": [
                    {"range": f"'{sheet}'!{column}{i}:{column}{i + COUNT - 1}",
                     "majorDimension": "ROWS",
                     "values": price_data}
                ]
            }
        ).execute()


        print(f"[INFO] - Данные внесены! ({i + COUNT - 1}/{end})")

        return True

    except Exception as ex:
        return False


def main(sheet, column, start, end):

    countries = {
        'USA': 'US',
        'Japan': 'JP',
        'Canada': 'CA',
        'Australia': 'AU',
        'Brazil': 'BR',
        'Argentina': 'AR',
        'Mexico': 'MX'
    }

    unit = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=f"'pass'!{column}2:{column}5",
        majorDimension='ROWS'
    ).execute()


    unit = unit['values']

    weight = unit[0][0]

    length = unit[1][0]

    width = unit[2][0]

    height = unit[3][0]

    country = countries[sheet]

    for i in range(start, end + 1, COUNT):

        result = put_data(height, weight, width, length, i, country, sheet)

        while not result:
            print('Отдых ...')
            time.sleep(10)
            result = put_data(height, weight, width, length, i, country, sheet)


if __name__ == '__main__':

    sheet = input('введите название таблицы: ')

    column = input("введите столбец для редактирования: ")

    start = int(input("Начало: "))

    end = int(input("Конец: "))

    main(sheet, column, start, end)
