import requests
import json
from bs4 import BeautifulSoup
from urllib.parse import quote
from utils import get_stock_name_and_code

# param
stock_name, stock_code = get_stock_name_and_code(41)
page_num = 10

seq_len = 1024
#請求網站
news_list = []
cnt = 0
for comp in stock_name:
    for page in range(page_num):
        # 要抓取的網址
        url = 'https://tw.finance.yahoo.com/news_search.html?ei=Big5&q=' + quote(comp.encode('big5hkscs')) + f'&pg={page+1}'
        print(url)

        try:
            list_req = requests.get(url)
        except:
            break
        #將整個網站的程式碼爬下來

        soup = BeautifulSoup(list_req.content, "html.parser")
        get_all_news = soup.find('table', { 'id': 'newListTable' })
        single_news_tag_array = get_all_news.find_all('table')
        # get all news title
        all_news_title = []
        for news in single_news_tag_array:
            title_tags = news.find_all('a', { 'class': 'mbody' })
            if len(title_tags) >= 2:
                title = title_tags[-1].get_text()
                all_news_title.append(title)

        all_news_body = []
        for news in single_news_tag_array:
            body = news.find_all('span', { 'class': 'mbody' })
            if len(body) >= 2:
                all_news_body.append(body[0].get_text())

        all_news_links = []
        for news in single_news_tag_array:
            a_tags = news.find_all('span', { 'class': 'mbody' })
            for tag in a_tags:
                link = tag.find('a')
                if link != None:
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
                if(len(arti_cont) < seq_len):
                    # print(item.get_text())
                    arti_cont += item.get_text() + "\n"

            news_list.append({"title": all_news_title[i], "content": arti_cont, "time": pub_time.get_text(), "stock_name": comp, "stock_code": stock_code[cnt]})
            # news["title"] = title
            # print(arti_cont, "\n\n")
            # break
    cnt += 1

with open('train.json', 'w', encoding='utf-8') as json_file:
    json.dump(news_list, json_file, indent=4, ensure_ascii=False)
