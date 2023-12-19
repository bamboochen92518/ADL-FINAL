# https://search.ltn.com.tw/list?keyword=%E5%8F%B0%E7%A9%8D%E9%9B%BB&start_time=20041201&end_time=20231219&sort=date&type=business&page=1&fbclid=IwAR0FbdQnHhosAzmEZwe_GHVXLvMi8PQY23EThcIcLaeKxgZooY-0GdRzX1k
import requests
import json
from bs4 import BeautifulSoup
from urllib.parse import quote

# param
stock_name=['大立光', '台積電', '聯發科']
stock_code=['3008.TW', '2330.TW', '2454.TW']
start_time, end_time = '20041201', '20231219'
page_num = 2
#

seq_len = 1024
#請求網站
news_list = []
for comp in stock_name:
    cnt = 0
    for page in range(page_num):
        url = 'https://search.ltn.com.tw/list?keyword=' + quote(comp.encode('utf-8')) + '&start_time=' + start_time + '&end_time=' + end_time + '&sort=date&type=business&page=' + '1'
        try:
            list_req = requests.get(url)
        except:
            break
        soup = BeautifulSoup(list_req.content, "html.parser")

        news_table = soup.find('ul', {'class': 'list boxTitle', 'data-desc': '列表'})
        news_body = news_table.find_all('li')

        for item in news_body:
            data = ['', '', '']
            cur_link = item.find('a')['href']
            cur_title = item.find('img')['title']
            # print(cur_link, cur_title)
            data[0] = str(cur_title)

            news_content = requests.get(cur_link)
            soup = BeautifulSoup(news_content.content, "html.parser")
            main_txt = soup.find('div', {'class': 'text'}).find_all('p')
            pub_time = soup.find('span', {'class': 'time'}).get_text()
            # print(main_txt)
            data[2] = str(pub_time)
            for subtext in main_txt:
                if subtext.find('img'):
                    continue
                text_body = subtext.get_text()
                if '點我訂閱' in str(text_body):
                    break
                else:
                    data[1] += str(text_body)
            news_list.append({'title': data[0], 'content': data[1], 'time': data[2], 'stock_name': comp, 'stock_code': stock_code[cnt]})
                    

with open('train.json', 'w', encoding='utf-8') as json_file:
    json.dump(news_list, json_file, indent=4, ensure_ascii=False)