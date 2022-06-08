import requests
import pandas as pd
from bs4 import BeautifulSoup

_user_agent = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
            + '(KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36')

def _get_sise_last_index(code):
    url = f'https://finance.naver.com/item/sise_day.naver?code={code}'
    soup = BeautifulSoup(requests.get(url, headers={'User-Agent': _user_agent}).text, 'lxml')
    navi = soup.find('table', {'class': 'Nnavi'})

    last_url = navi.find('td', {'class': 'pgRR'}).find('a').attrs['href']
    last_index = int(last_url.split('=')[-1])

    return last_index

def get_sise_data(code):
    page_end = _get_sise_last_index(code)

    df = pd.DataFrame(columns=['시가', '종가', '고가', '저가'])
    df.index.name = '날짜'

    for page in range(1, page_end + 1):
        url = f'https://finance.naver.com/item/sise_day.naver?code={code}&page={page}'
        soup = BeautifulSoup(requests.get(url, headers={'User-Agent': _user_agent}).text, 'lxml')
        table = soup.find('table', {'class': 'type2'})

        for e in [i for i in table.find_all('tr') if i.attrs != {}]:
            날짜, 종가, _, 시가, 고가, 저가, __ = map(lambda x: x.text, e.find_all('td'))
            if 날짜.encode() == b'\xc2\xa0': continue

            시가, 종가, 고가, 저가 = map(lambda x: int(x.replace(',', '')), [시가, 종가, 고가, 저가])
            df = df.append(pd.Series([시가, 종가, 고가, 저가], ['시가', '종가', '고가', '저가'], name=날짜))

    return df