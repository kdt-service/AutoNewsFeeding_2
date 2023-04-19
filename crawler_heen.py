# crontab에서 실행 시 경로가 /home/ubuntu로 바뀜
# 현재 파일의 경로로 수정
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
print('현재 경로:', os.path.abspath('.'))

#필요 모듈 임포트
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
# from cleansing import cleansing
from datetime import datetime, timedelta

#----------------------------------------------------------
class Crawler:

    def __init__(self) -> None:
        
        # 마지막 뉴스 url dict 가져오기
        with open('./naver_news_url', 'r') as f:
            tmp = [l.rstrip().split(',') for l in f.readlines()]
            self.SUB_CATEGORY_URL = {int(k): v for k, v in tmp}

    def naver_crawler(self):
    
        # 소요시간 측정
        start_time = time.time()
        
        #-------------------------------------------------
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'}

        sub_category_num = [731,226,227,230,732,283,229,228] #IT/과학 서브카테고리 

        cate_list = []
        for sub_num in sub_category_num:
            news_list = []
            sub_names = [l.rstrip().split(',') for l in open('./sub_category', 'r', encoding='utf-8').readlines()]
            self.SUB_CATEGORY_DICT = {int(k): v for k, v in sub_names}
            
            URL = "https://news.naver.com/main/list.naver?mode=LS2D&mid=shm&sid2={}&sid1=105".format(sub_num) #IT/과학
            print('--------------------------------------------------------------')
            print(f'서브카테고리({self.SUB_CATEGORY_DICT[sub_num]}) 크롤링 중~')
            
            date = datetime.now()

            breaker_3 = False
            breaker_url = False
            breaker_2 = False
            
            while True: #date 주기
                if breaker_3 == True:
                    break
                
                date_str = datetime.strftime(date, '%Y%m%d')
                print(f'{date_str} 크롤링 중')
                
                first_URL = URL + f'&date={date_str}'
                print(f'first url: {first_URL}')
                use_URL = first_URL + '&page={}'

                page = 1
                
                #총 페이지 수 구하기
                while True:
                    response = requests.get(use_URL.format(page), headers=headers)    
                    soup = BeautifulSoup(response.text, 'html.parser')
                    print(response)
                    try: 
                        if soup.select_one('.next').text == '다음':
                            page += 10
                    except:
                        break
                
                page_breaker = False
                page_breaker2 = False
                
                while True:
                    if breaker_2 == True:
                        breaker_3 = True
                        break
                    
                    if page_breaker == True:
                        breaker_3 = True
                        #date = date - timedelta(days=1)
                        break
                    
                    if page_breaker2 ==True:
                        breaker_3 = True
                        break
                    
                    if page >= 2:
                        for_pages = soup.find(class_="paging" )
                        try:
                            pages = for_pages.find_all('a')
                            plus_page = len(pages) - 1
                        except: pass
                    else:
                        try:
                            for_pages = soup.find(class_="paging" )
                            pages = for_pages.find_all('a')
                            plus_page = len(pages)
                        except:
                            plus_page = 0

                    total_page = page + plus_page
                    print(f'총 페이지는? {total_page} !!!!! ')

                    for page in range(1,total_page+1):
                        
                        if breaker_url == True:
                            print('동일 URL breaker 발동!!!!!!!!!!!!!!!!!!!')
                            breaker_2 = True
                            break

                        response = requests.get(use_URL.format(page), headers=headers)   
                        # print(f'사용 url: {use_URL.format(page)}') 
                        soup = BeautifulSoup(response.text, 'html.parser')

                        url_in = soup.select('div[id="main_content"] li') #한 페이지 최대 20개
                        url_list = []
                        for li in url_in:
                            url_one = li.select_one('dt a[href]').attrs['href'] #기자와 작성시간 알기 위해 기사 링크 추가
                            url_list.append(url_one)
                        #print(f'{page}페이지 링크 다 가져옴!!') 

                        for url in url_list: #한 링크씩 들어가기

                            if url == self.SUB_CATEGORY_URL[sub_num]: #최신뉴스까지만!
                                print(f'[{self.SUB_CATEGORY_DICT[sub_num]}] 최신까지 크롤링 완료')
                                breaker_url = True
                                break
                            response = requests.get(url, headers=headers)
                            time.sleep(0.5)
                            soup = BeautifulSoup(response.text, 'html.parser')
                            #print(f'그냥 url: {url}')
                            #print(f'딕셔너리 url: {self.SUB_CATEGORY_URL[sub_num]}')
                                
                            news_dict = {}
                            news_dict['platform'] = '네이버'
                            news_dict['main_category'] = 'IT/과학'
                            sub_name = self.SUB_CATEGORY_DICT[sub_num]
                            news_dict['sub_category'] = '{}'.format(sub_name)

                            try: news_dict['title'] = soup.select_one('.media_end_head_headline').text.strip()
                            except:
                                try: news_dict['title'] = soup.select_one('h2[id="title_area"]').text.strip()
                                except:
                                    try: news_dict['title'] = soup.select_one('.title').text.strip()
                                    except: news_dict['title'] = None
                            try: news_dict['content'] = soup.select_one('div[id="newsct_article"]').text.strip()
                            except:
                                try: news_dict['content'] = soup.select_one('div[id="dic_area"]').text.strip()
                                except:
                                    try: news_dict['content'] = soup.select_one('div[id="articeBody"]').text.strip()
                                    except:
                                        try: news_dict['content'] = soup.select_one('.news_end').text.strip()
                                        except: news_dict['content'] = None
                            try: news_dict['writer'] = soup.select_one('.media_end_head_journalist_name').text.strip()
                            except:
                                try: news_dict['writer'] = soup.select_one('.byline_s').text[:6]
                                except:
                                    try: news_dict['writer'] = soup.select_one('.byline').text[:3].strip()
                                    except: news_dict['writer'] = None
                            try: news_dict['writed_at'] = soup.select_one('.media_end_head_info_datestamp_bunch').text.strip()
                            except:
                                try: news_dict['writed_at'] = soup.select_one('.author em').text.strip()
                                except: 
                                    try: news_dict['writed_at'] = soup.select_one('.info').text.strip()
                                    except:news_dict['writed_at'] = soup.select_one('.media_end_head_info_datestamp_time').text.strip()
                            news_dict['url'] = url

                            # df_one = pd.DataFrame(news_dict, index = [0])
                            news_list.append(news_dict)
                            
                            #print('한 기사 넣기 완료')
                        #print(f'{page}페이지 완료!')   
                        if page == total_page:
                            page_breaker2 = True 
                        
                    if total_page == 1:
                        page_breaker = True

                date = date - timedelta(days=1)
                print(f'{date_str} 크롤링 완료!')
            
            
            if news_list:
                df_cate1 = pd.DataFrame(news_list)
                    
                df_cate1.drop_duplicates(['title','content'], inplace=True) #혹시 모를 중복 제거
                df_cate1.sort_values('writed_at', inplace=True) #정렬
                # print(df_cate1[['writed_at', 'url']])
                # print(df_cate1.iloc[-1]['url'])
                self.SUB_CATEGORY_URL[sub_num] = df_cate1.iloc[-1]['url']
                
                with open('./naver_news_url', 'w', encoding='utf-8') as f: #마지막 url 저장
                    for sub_num1, sub_url in self.SUB_CATEGORY_URL.items():
                        f.write(f'{sub_num1},{sub_url}\n')
                
                cate_list.append(df_cate1) #카테고리 하나 데이터들 리스트에 넣기
        
        df = pd.concat(cate_list, ignore_index=True) 
            
        # crontab에서 10분단위 스케줄링, 카테고리 2개의 경우 소요시간 0초
        print('소요시간 :', int(time.time() - start_time), '초')
        
        #데이터프레임 전처리
        ##  [writed_at] YYYY-MM-DD HH:MM:SS 형식으로 변경
        df['writed_at'] = df['writed_at'].str.replace('오후', 'PM')
        df['writed_at'] = df['writed_at'].str.replace('오전', 'AM')
        df['writed_at'] = df['writed_at'].str.replace('입력', '')
        df['writed_at'] = df['writed_at'].str[:23]
        df['writed_at'] = df['writed_at'].str.replace('기사 ', '')
        df['writed_at'] = pd.to_datetime(df['writed_at'], format='%Y.%m.%d. %p %I:%M')
        df['writed_at'] = df['writed_at'].apply(lambda x : x.strftime('%Y-%m-%d %H:%M:%S') )

        ## [platform] Naver -> 네이버
        df['platform'] = df['platform'].apply(lambda x: x.replace('Naver', '네이버'))
        
        df['title'] = df['title'].apply(lambda x : x.replace('\n', ' ')[:160]) #title 클렌징
        
        # df['content'] = df.apply(lambda x: cleansing(x['content'], x['writer'] if x['writer'] else ''), axis=1) #content 클렌징
        
        df['url'] = ''
                    
        self.news_df = df

        return df                            
        

import pandas as pd
class DataManager:
    """
    데이터를 관리하는 객체
    """

    def __init__(self) -> None:
        # 기존 데이터를 읽어옴
        try:
            self.df = pd.read_csv('./news_df.csv')
        except:
            self.df = pd.DataFrame([])

    def add_new_data(self, new_data):
        df_list = [self.df, new_data]
        self.df = pd.concat(df_list, ignore_index=True)
        return
    
    def save_data(self, file_path):
        self.df.to_csv(file_path, index=False)
        print('최신뉴스 파일 저장 완료!')
        return

if __name__ == '__main__':
    # 객체지향 프로그래밍 -> 컴포넌트 단위로 관리
    my_crawler = Crawler()
    my_crawler.naver_crawler()
    my_crawler.news_df 

    my_data_manager = DataManager()
    my_data_manager.add_new_data(my_crawler.news_df)
    my_data_manager.save_data('./news_df.csv')