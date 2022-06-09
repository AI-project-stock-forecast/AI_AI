import requests
import pandas as pd
import urllib.parse
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

def get_jongmok_list(name):
    name = urllib.parse.quote(name, encoding='cp949')

    res = {}
    page = 1

    while True:
        url = f'https://finance.naver.com/search/searchList.naver?query={name}&page={page}'

        try:
            soup = BeautifulSoup(requests.get(url, headers={'User-Agent': _user_agent}).text, 'lxml')
            table = soup.find('table', {'class': 'tbl_search'}).find('tbody')

            for entry in table.find_all('tr'):
                a = entry.find('td', {'class': 'tit'}).find('a')

                _name = a.text
                href = a.attrs['href'].split('=')[-1]

                res[href] = _name
        except Exception as e:
            break

        page += 1
    
    return res

def get_quant_list():
    url = 'https://finance.naver.com/sise/sise_quant.naver'

    df = pd.DataFrame(columns=['종목명', '현재가'])
    df.index.name = '종목 코드'

    soup = BeautifulSoup(requests.get(url).text, 'lxml')
    table = soup.find('table', {'class': 'type_2'})

    trs = table.find_all('tr')
    
    for tr in trs:
        try:
            NO, 종목명, 현재가, 전일비, 등락률, 거래량, 거래대금, 매수호가, 매도호가, 시가총액, PER, ROE = tr.find_all('td')

            code = 종목명.find('a').attrs['href'].split('=')[-1]

            종목명 = 종목명.find('a').text
            현재가 = int(현재가.text.replace(',', ''))

            '''
            if 전일비.find('img').attrs['src'] == 'https://ssl.pstatic.net/imgstock/images/images4/ico_down.gif':
                전일비 = -int(전일비.find('span').text.replace('\r', '').replace('\t', ''))
            else:
                전일비 = int(전일비.find('span').text.replace('\r', '').replace('\t', ''))
            등락률 = 등락률.find('span').text.replace('\r', '').replace('\t', '').replace('\n', '')
            거래량 = int(거래량.text.replace(',', ''))
            거래대금 = int(거래대금.text.replace(',', ''))
            매수호가 = int(매수호가.text.replace(',', ''))
            매도호가 = int(매도호가.text.replace(',', ''))
            시가총액 = int(시가총액.text.replace(',', ''))
            PER = PER.text
            ROE = ROE.text

            print(현재가, 전일비, 등락률, 거래량, 거래대금, 매수호가, 매도호가, 시가총액, PER, ROE)
            '''

            df = df.append(pd.Series([종목명, 현재가], ['종목명', '현재가'], name=code))

        except Exception as e:
            ...

    return df