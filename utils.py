import requests
from bs4 import BeautifulSoup
import os
import pandas as pd
import json
from urllib.parse import quote
from time import sleep
from fake_useragent import UserAgent
import csv
from bisect import bisect_right
from tqdm import tqdm


def get_stock_name_and_code(sectorID):
    # 41: 電腦週邊, 46: 資訊服務, 40: 半導體, 38: 生技, 1: 水泥
    # https://tw.stock.yahoo.com/class/
    stock_name = list()
    stock_code = list()
    url = f"https://tw.stock.yahoo.com/class-quote?sectorId={sectorID}&exchange=TAI"
    response = requests.get(url)
    if response.status_code != 200:
        print("sectorID 對應的類股不存在")
        return stock_name, stock_code
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')

    # find type
    stock_type = soup.find('h1', class_="Mb(12px) Fz(24px) Lh(32px) Fw(b)").get_text().split('上市')[1].split('分類行情')[0]

    # find stock name
    target_divs = soup.find_all('div', class_='Lh(20px) Fw(600) Fz(16px) Ell')
    for div in target_divs:
        text_content = div.get_text()
        stock_name.append(text_content)

    # find stock code
    target_divs = soup.find_all('span', class_='Fz(14px) C(#979ba7) Ell')
    for div in target_divs:
        text_content = div.get_text()
        stock_code.append(text_content)

    # debug
    '''
    for i in range(len(stock_name)):
        print(f"name = {stock_name[i]}, code = {stock_code[i]}")
    '''

    return stock_name, stock_code


def download_stock_price_csv(stock_code):
    for code in tqdm(stock_code, total=len(stock_code), desc='Downloading stock price'):
        url = f"https://finance.yahoo.com/quote/{code}/history?p={code}"
        # print(url)
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print(response.status_code)
            print(response.url)
            print(f"找不到{code}的歷史股價")
            continue

        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        # find type
        stock_price_csv_path = soup.find('a', class_="Fl(end) Mt(3px) Cur(p)").get('href')
        temperature_path = './stock_price/tmp.csv'
        destination_path = f'./stock_price/{code}.csv'
        stock_price_csv = requests.get(stock_price_csv_path, headers=headers)

        if stock_price_csv.status_code == 200:
            with open(temperature_path, 'wb') as file:
                file.write(stock_price_csv.content)
            if os.path.exists(destination_path):
                df_a = pd.read_csv(destination_path)
                df_b = pd.read_csv(temperature_path)
                df_merged = pd.concat([df_a, df_b], ignore_index=True)
                df_merged.drop_duplicates(subset=['Date'], keep='last', inplace=True)
                df_merged.to_csv(destination_path, index=False)
                os.remove(temperature_path)
            else:
                os.rename(temperature_path, destination_path)
        else:
            print(f'無法下載{code}的歷史股價。狀態碼：{stock_price_csv.status_code}')


def get_news_from_yahoo(sectorID):
    stock_name, stock_code = get_stock_name_and_code(sectorID)
    seq_len = 1024
    news_list = []
    cnt = 0
    for comp in stock_name:
        page = 0
        while True:
            url = 'https://tw.finance.yahoo.com/news_search.html?ei=Big5&q=' + quote(comp.encode('big5hkscs')) + f'&pg={page+1}'
            # print(url)

            try:
                list_req = requests.get(url)
            except:
                break

            soup = BeautifulSoup(list_req.content, "html.parser")
            get_all_news = soup.find('table', {'id': 'newListTable'})
            single_news_tag_array = get_all_news.find_all('table')

            # get all news title, body, links
            all_news_title = []
            all_news_body = []
            all_news_links = []
            for news in single_news_tag_array:
                title_tags = news.find_all('a', {'class': 'mbody'})
                if len(title_tags) >= 2:
                    title = title_tags[-1].get_text()
                    all_news_title.append(title)
                body = news.find_all('span', {'class': 'mbody'})
                if len(body) >= 2:
                    all_news_body.append(body[0].get_text())
                a_tags = news.find_all('span', {'class': 'mbody'})
                for tag in a_tags:
                    link = tag.find('a')
                    if link is not None:
                        all_news_links.append(link['href'])

            for i in range(len(all_news_title)):
                arti_cont = ""
                # print('文章標題: '.format(all_news_title[i]))
                # print('內文: {}'.format(all_news_body[i]))
                # print('詳全文網址: {}'.format(all_news_links[i]))

                text_url = format(all_news_links[i])
                l_req = requests.get(text_url)
                soup = BeautifulSoup(l_req.content, "html.parser")

                content_array = soup.find('div', {'class': 'caas-body'}).find_all('p')
                pub_time = soup.find('time')
                # print(pub_time.get_text())
                for item in content_array:
                    if len(arti_cont) < seq_len:
                        # print(item.get_text())
                        arti_cont += item.get_text() + "\n"

                news_list.append({
                    "title": all_news_title[i],
                    "content": arti_cont,
                    "time": pub_time.get_text(),
                    "stock_name": comp,
                    "stock_code": stock_code[cnt]
                })
            page += 1
        output_file = f"./stock_news/{stock_code[cnt]}_news.json"
        with open(output_file, 'w', encoding='utf-8') as json_file:
            json.dump(news_list, json_file, indent=4, ensure_ascii=False)
        cnt += 1


def get_news_from_ltn(sectorID, start_time, end_time):
    stock_name, stock_code = get_stock_name_and_code(sectorID)
    ua = UserAgent()
    headers = {'User-Agent': ua.random}

    for i in range(len(stock_name)):
        name = stock_name[i]
        code = stock_code[i]
        news_list = []
        page = 0
        print(f"正在抓取「{name}」的相關新聞")

        while True:
            url = 'https://search.ltn.com.tw/list?keyword=' + quote(name.encode('utf-8')) + '&start_time=' + start_time + '&end_time=' + end_time + '&sort=date&type=business&page=' + str(page + 1)
            print(url)

            try:
                list_req = requests.get(url, headers=headers)
            except:
                break

            if list_req.status_code != 200:
                # print(list_req.status_code)
                break
            soup = BeautifulSoup(list_req.content, "html.parser")

            news_table = soup.find('ul', {'class': 'list boxTitle', 'data-desc': '列表'})

            # 如果查無結果的話，會抓不到任何內容，所以需要特判
            try:
                news_body = news_table.find_all('li')
            except:
                break

            for item in news_body:
                # 'title': data[0], 'content': data[1], 'time': data[2]
                data = ['', '', '']

                cur_link = item.find('a')['href']
                cur_title = item.find('img')['title']
                data[0] = str(cur_title)

                news_content = requests.get(cur_link, headers=headers)
                soup = BeautifulSoup(news_content.content, "html.parser")
                main_txt = soup.find('div', {'class': 'text'}).find_all('p')
                pub_time = soup.find('span', {'class': 'time'}).get_text()
                data[2] = str(pub_time)

                for subtext in main_txt:
                    if subtext.find('img'):
                        continue
                    text_body = subtext.get_text()
                    if '點我訂閱' in str(text_body):
                        break
                    else:
                        data[1] += str(text_body)
                news_list.append({
                    'title': data[0],
                    'content': data[1],
                    'time': data[2],
                    'stock_name': name,
                    'stock_code': code
                })
                sleep(0.1)
            page += 1

        output_file = f"./stock_news/{code}_news.json"
        with open(output_file, 'w', encoding='utf-8') as json_file:
            json.dump(news_list, json_file, indent=4, ensure_ascii=False)
        sleep(0.1)


def get_news_from_ettoday(sectorID):
    stock_name, stock_code = get_stock_name_and_code(sectorID)
    ua = UserAgent()
    headers = {'User-Agent': ua.random}

    # 請求網站
    for i in range(len(stock_name)):
        name = stock_name[i]
        code = stock_code[i]
        news_list = []
        page = 0
        print(f"正在抓取「{name}」的相關新聞")

        while True:
            url = f'https://www.ettoday.net/news_search/doSearch.php?keywords={name}&idx=1&kind=17&daydiff=3&page={page + 1}'
            print(url)

            try:
                list_req = requests.get(url, headers=headers)
            except:
                break

            if list_req.status_code != 200:
                print(list_req.status_code)
                break

            soup = BeautifulSoup(list_req.content, "html.parser")
            news_table = soup.find_all('div', {'class': 'box_1'})

            # 如果查無結果的話，會抓不到任何內容，所以需要特判
            if len(news_table) == 0:
                break

            for item in news_table:
                # 'title': data[0], 'content': data[1], 'time': data[2]
                data = ['', '', '']

                cur_link = item.find('a')['href']
                news_content = requests.get(cur_link, headers=headers)
                soup = BeautifulSoup(news_content.content, "html.parser")
                cur_title = soup.find('h1', {'class': 'title', 'itemprop': 'headline'}).get_text()
                data[0] = cur_title

                main_txt = soup.find('div', {'class': 'story', 'itemprop': 'articleBody'}).find_all('p')
                pub_time = soup.find('time', {'itemprop': 'datePublished'}).get_text()
                pub_time = pub_time.replace(' ', '')
                pub_time = pub_time.replace('\n', '')
                pub_time = pub_time[:10] + ' ' + pub_time[10:]
                data[2] = str(pub_time)

                for subtext in main_txt:
                    text_body = subtext.get_text()
                    if text_body.find('（圖／') != -1 or text_body.find('img alt="') != -1:
                        continue
                    data[1] += str(text_body)
                news_list.append({
                    'title': data[0],
                    'content': data[1],
                    'time': data[2],
                    'stock_name': name,
                    'stock_code': code
                })
                sleep(0.1)
            page += 1

        output_file = f"./stock_news/{code}_news.json"
        with open(output_file, 'w', encoding='utf-8') as json_file:
            json.dump(news_list, json_file, indent=4, ensure_ascii=False)
        sleep(0.1)


def add_label():
    if not os.path.exists('stock_data/'):
        os.mkdir('stock_data/')
    for file in os.listdir('stock_news'):
        json_file_name = f'stock_news/{file}'
        json_data = []
        with open(json_file_name, 'r', encoding='utf8') as json_file:
            json_data = json.load(json_file)

        for data in json_data:
            stock_code = data['stock_code']

        csv_file_name = f'stock_price/{stock_code}.csv'
        csv_data = []
        with open(csv_file_name, 'r', newline='', encoding='utf8') as csv_file:
            csv_reader = csv.reader(csv_file)
            for row in csv_reader:
                csv_data.append(row)

        stock_result = dict()
        sz = len(csv_data)
        for idx in range(2, sz):
            time_stamp = f'{csv_data[idx][0]} 12:59'
            pre_result = csv_data[idx - 1][5]
            cur_result = csv_data[idx][5]
            # 0: 漲, 1:  跌 / 持平
            if pre_result >= cur_result:
                stock_result[time_stamp] = 0
            else:
                stock_result[time_stamp] = 1

        new_json_data = []
        for data in json_data:
            stock_code = data['stock_code']
            time_stamp = data['time'].replace('/', '-')
            title = data['title']
            content = data['content']
            stock_name = data['stock_name']
            sorted_keys = sorted(list(stock_result.keys()))
            key_index = bisect_right(sorted_keys, time_stamp)
            if key_index == len(sorted_keys):
                continue
            next_close_time = sorted_keys[key_index]
            new_json_data.append({
                "title": title,
                "content": content,
                "time": time_stamp,
                "stock_name": stock_name,
                "stock_code": stock_code,
                "stock_result": stock_result[next_close_time]
            })

        stock_code = file.replace('_news.json', '')
        with open(f'stock_data/{stock_code}.json', 'w', encoding='utf8') as json_file:
            json.dump(new_json_data, json_file, ensure_ascii=False, indent=5)


def split_data_to_train_and_valid():
    train_data = []
    valid_data = []

    for file in os.listdir('train_data'):
        json_file_name = f'stock_data/{file}'
        json_data = []
        with open(json_file_name, 'r', encoding='utf8') as json_file:
            json_data = json.load(json_file)

        for data in json_data:
            if data["time"] >= "2023-11-01 00:00":
                valid_data.append(data)
            else:
                train_data.append(data)

    with open('train.json', 'w', encoding='utf8') as json_file:
        json.dump(train_data, json_file, ensure_ascii=False, indent=5)

    with open('valid.json', 'w', encoding='utf8') as json_file:
        json.dump(valid_data, json_file, ensure_ascii=False, indent=5)
