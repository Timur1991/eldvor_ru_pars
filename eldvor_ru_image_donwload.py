from bs4 import BeautifulSoup
import requests
import json
import random
from time import sleep
import time
import fake_useragent
import os
# pip install lxml
# pip install openpyxl

# одна из первых моих работ
# получаем изображения товаров по выбранной категории
# по всем категориям не получается, из за превышения количества запросов (в будущем надо исправлять)

url = 'https://eldvor.ru/'

user = fake_useragent.UserAgent().random
headers = {
    'user_agent': user
              }

domen = 'https://eldvor.ru'


req = requests.get(url, headers=headers)
src = req.text


# def build_dict_and_save_in_json(src):
#     """ Создаем словарь вида 'название категории': 'ссылка на нее' и сохраняем в json"""
#     soup = BeautifulSoup(src, 'lxml')
#     all_categories = soup.find_all('div', class_='index-section__header')
#
#     all_categories_dict = {}
#     for item in all_categories:
#         item_text = item.find('a').text.strip()  # получаем название ссылки
#         item_href = domen + item.find('a').get('href')  # получаем ссылку
#         all_categories_dict[item_text] = item_href + '?av=v_nalichii&av=pod_zakaz'
#
#     # сохранение словаря в файл json
#     with open('all_categories_dict.json', 'w', encoding='utf-8') as file:
#         json.dump(all_categories_dict, file, indent=4, ensure_ascii=False)
#
#
# # создаем json файл с названием раздела и ссылкой на него
# build_dict_and_save_in_json(src)

# загрузка ранее созданного файла json в переменную all_categories
with open('all_categories_dict.json', encoding='utf-8') as file:
    all_categories = json.load(file)

category_count = 1
count = 0

for category_name, category_href in all_categories.items():
    if category_count == 1:
        # для всех разделов
        #req = requests.get(url=category_href, headers=headers)

        # для определенного раздела
        req = requests.get('https://eldvor.ru/electronics/pribory-ucheta/?av=v_nalichii', headers=headers)
        src = req.text

        # получаем количество страниц в разделе
        page = 1
        soup = BeautifulSoup(src, 'html.parser')
        pagination = soup.find_all('div', class_='bx-pagination-container row')
        goods = []
        if pagination:
            pages = pagination[-1].text.split('\n')
        else:
            pages = 1
        print(pages[-5])

        # парсим страницу за страницей
        #for page in range(1, int(pages[-5]) + 1):

        # парсим выбранный диапазон
        for page in range(1, 2):

            # парсим все категории
            #responce = requests.get(f'{category_href}&PAGEN_1={page}', headers=headers).text

            # парсим выбранную категорию (ссылку берем в json файле)
            responce = requests.get(f'https://eldvor.ru/electronics/pribory-ucheta/?av=v_nalichii&PAGEN_1={page}', headers=headers).text

            soup = BeautifulSoup(responce, 'lxml')
            items = soup.find('div', class_='table_cell_top content-goods-cell').find_all('div', class_='b-goods-item')
            print(f'Парсинг страницы {page} из {pages[-5]}...')

            image_count_on_page = 1

            for image in items:
                    image_link = image.find('a', class_='b-goods-item-img').get('href')
                    image_name = image.find('div', class_='info-a').get_text(strip=True).split(' ')[-1]
                    download_storage = requests.get(f'{domen}{image_link}').text
                    download_soup = BeautifulSoup(download_storage, 'lxml')
                    download_block = download_soup.find('div', class_='product__images')

                    # если нет изображения у позиции (нет ссылки на нее) то записываем название позиции в txt файл
                    try:
                        result_link = download_block.find('a', class_='m-lightbox').get('href')
                    except AttributeError:
                        print(f'Позиция с кодом "{image_name}" не имеет изображения!')
                        with open(f'no_image/not_a_image.txt', 'a') as file:
                            file.write(f'{domen}{image_link} \n')
                        continue

                    # получаем изображение, если ошибка, повторяем с изображения на котором прервалась работа
                    while True:
                        try:
                            image_bytes = requests.get(f'{domen}{result_link}').content
                            #sleep(random.randrange(1, 3))
                            #time.sleep(2)
                            break
                        except Exception as ex:
                            print(f' {ex} Ошибка соединения c .{image_name}..')
                            # pause = time.sleep(30)
                            for sec in range(1, 31):
                                time.sleep(1)
                                print(f'запустится через {sec}...')

                    if os.path.exists(f"image/{image_name}.jpg"):
                    #if os.path.exists(f"image/{image_name}.jpg"):
                        print(f"Это {image_name} изображение уже скачено ({image_count_on_page} из {len(items)} на странице)")
                        #time.sleep(1)
                        image_count_on_page += 1
                        continue
                    else:
                        #сохраняем наше полученное изображение
                        with open(f'image/{image_name}.jpg', 'wb') as file:
                            file.write(image_bytes)
                        print(f'Изображение {image_name}" - успешно скачано! ({image_count_on_page} из {len(items)} на странице)')
                        #sleep(random.randrange(2, 6))
                        #time.sleep(1)
                    image_count_on_page += 1

            # добавляем задержку между страницами
            sleep(random.randrange(2, 4))
            page += 1
        category_count += 1
        #sleep(random.randrange(4, 8))

