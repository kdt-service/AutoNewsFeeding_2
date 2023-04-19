from crawler_heen import Crawler
from crawler_heen import DataManager

if __name__ == '__main__':
    # 객체지향 프로그래밍 -> 컴포넌트 단위로 관리
    my_crawler = Crawler()
    my_crawler.naver_crawler()
    my_crawler.news_df 

    my_data_manager = DataManager()
    my_data_manager.add_new_data(my_crawler.news_df)
    my_data_manager.save_data('./news_df.csv')