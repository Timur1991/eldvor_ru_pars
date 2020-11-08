from bs4 import BeautifulSoup
import requests
import json
import pandas as pd
from pandas import ExcelWriter
import random
from time import sleep
# pip install lxml
# pip install openpyxl


# парсим сайт eldvor.ru все позиции с каждой страницы по разделам
# полученные данные сохраяем в exel файл
# в будущем хочу вместо полуения инфы о товаре, получать фото продукции с артикулом в названии

url = 'https://eldvor.ru/'
headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 YaBrowser/20.9.1.110 Yowser/2.5 Safari/537.36'
}
domen = 'https://eldvor.ru'
file = 'goods.xlsx'

req = requests.get(url, headers=headers)
src = req.text
# print(src)

soup = BeautifulSoup(src, 'lxml')
all_headers_section = soup.find_all('div', class_='index-section__header')

all_headers_section_dict = {}
for item in all_headers_section:
    item_text = item.find('a').text.strip()  # получаем название ссылки
    item_href = domen + item.find('a').get('href')  # получаем ссылку
    # print(f'{item_text}:{item_href}')  # приводим к аккуратному форматированию
    all_headers_section_dict[item_text] = item_href + '?av=v_nalichii'

# сохранение словаря в файл json
with open('all_categories_dict.json', 'w', encoding='utf-8') as file:
    json.dump(all_headers_section_dict, file, indent=4, ensure_ascii=False)

# загрузка файла json в переменную all_categories
with open('all_categories_dict.json', encoding='utf-8') as file:
    all_categories = json.load(file)

category_count = 1
exel_count = 1

for category_name, category_href in all_categories.items():
    # if count == 0:
    # создаем список знаков, которые хотим заменить
    rep = [', ', ' ', '-']
    # пробегаемся по всем знакам списка
    for item in rep:
        # если они встречаются
        if item in category_name:
            # заменяем их на '_'
            category_name = category_name.replace(item, '_')
    print(category_name)

    req = requests.get(url=category_href, headers=headers)
    src = req.text
    # print(src)
    with open(f'data/{category_count}_{category_name}.html', 'w', encoding='utf-8') as file:
        file.write(src)

    with open(f'data/{category_count}_{category_name}.html', encoding='utf-8') as file:
        scr = file.read()

    # получаем количество страниц в разделе
    page = 1
    soup = BeautifulSoup(src, 'html.parser')
    pagination = soup.find_all('div', class_='bx-pagination-container row')
    goods = []
    if pagination:
        pages = pagination[-1].text.split('\n')
    else:
        pages = 1
    # print(pages[-5])

    # парсим страницу за страницей
    for page in range(1, int(pages[-5]) + 1):
        responce = requests.get(f'{category_href}&PAGEN_1={page}', headers=headers).text
        soup = BeautifulSoup(responce, 'lxml')
        items = soup.find('div', class_='table_cell_top content-goods-cell').find_all('div', class_='b-goods-item')
        print(f'Парсинг страницы {page} из {pages[-5]}...')

        # проходимся по каждой позиции на странице и собераем инфу
        for item in items:
            goods.append({
                'name': item.find('div', class_='b-goods-item-link').get_text(strip=True),
                'code_goods': item.find('div', class_='info-a').get_text(strip=True).split(' ')[-1],
                'price': item.find('div', class_='b-goods-item-price clearfix').get_text(strip=True).split(' ')[:1:],
                'brend': item.find('div', class_='b-goods-item-name').get_text(strip=True),
                # 'link': domen + item.find('a', class_='snippet-link').get('href'),
            })

        # добавляем задержку между страницами
        sleep(random.randrange(1, 2))
        page += 1

    print('Количество позиций: ' + str(len(goods)))

    # сохраняем в ексель, с помощью пандас
    df = pd.DataFrame(goods)
    writer = ExcelWriter(f'data/{exel_count}_{category_name}_{file}')
    df.to_excel(writer, 'Sheet1')
    writer.save()

    exel_count += 1
    category_count += 1

    # добавляем задержку между разделами
    sleep(random.randrange(4, 8))
