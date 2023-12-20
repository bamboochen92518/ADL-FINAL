import requests
from bs4 import BeautifulSoup


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
    stock_type = soup.find('h1', class_= "Mb(12px) Fz(24px) Lh(32px) Fw(b)").get_text().split('上市')[1].split('分類行情')[0]
    print(stock_type)
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
    for code in stock_code:
        url = f"https://finance.yahoo.com/quote/{code}/history?p={code}"
        print(url)
        response = requests.get(url)
        if response.status_code != 200:
            print(response.status_code)
            print(f"找不到{code}的歷史股價")
            continue
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        # find type
        stock_price_csv_path = soup.find('a', class_= "Fl(end) Mt(3px) Cur(p)").get('href')
        destination_path = f'./stock_price/{code}.csv'
        stock_price_csv = requests.get(stock_price_csv_path)
        if stock_price_csv.status_code == 200:
            with open(destination_path, 'wb') as file:
                file.write(stock_price_csv.content)
            print(f'檔案已成功下載到 {destination_path}')
        else:
            print(f'無法下載檔案。狀態碼: {response.status_code}')
