# https://search.ltn.com.tw/list?keyword=%E5%8F%B0%E7%A9%8D%E9%9B%BB&start_time=20041201&end_time=20231219&sort=date&type=business&page=1&fbclid=IwAR0FbdQnHhosAzmEZwe_GHVXLvMi8PQY23EThcIcLaeKxgZooY-0GdRzX1k
# https://www.ettoday.net/news_search/doSearch.php?keywords=%E5%BB%A3%E9%81%94&idx=1&kind=17&daydiff=3&page=1
import requests
import json
from bs4 import BeautifulSoup
from urllib.parse import quote
from time import sleep
import argparse
from fake_useragent import UserAgent
from utils import get_stock_name_and_code

parser = argparse.ArgumentParser(description='')
parser.add_argument('--page_num', default=1000)
parser.add_argument('--sectorID', default=41)

# 解析命令列參數
args = parser.parse_args()
# param
stock_name, stock_code = get_stock_name_and_code(args.sectorID)
start_time, end_time = '20230101', '20231219'

ua = UserAgent()
headers = {'User-Agent': ua.random}

seq_len = 1024
# 請求網站
for i in range(len(stock_name)):
    name = stock_name[i]
    code = stock_code[i]
    news_list = []
    print(f"正在抓取「{name}」的相關新聞")
    for page in range(args.page_num):
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
        if len(news_table) == 0:
            break
        # 如果查無結果的話，會抓不到任何內容，所以需要特判
        for item in news_table:
            data = ['', '', '']
            cur_link = item.find('a')['href']
            # print(cur_link, cur_title)
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
            news_list.append({'title': data[0], 'content': data[1], 'time': data[2], 'stock_name': name, 'stock_code': code})
            sleep(0.1)

    output_file = f"./ettoday_stock_news/{code}_news.json"
    with open(output_file, 'w', encoding='utf-8') as json_file:
        json.dump(news_list, json_file, indent=4, ensure_ascii=False)
    sleep(0.1)
