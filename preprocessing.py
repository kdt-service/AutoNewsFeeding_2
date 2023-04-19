import pandas as pd
from datetime import datetime, timedelta
from text_cleaning import text_cleaning
from news_tokenize import tokenize
from word_embedding import embedding, get_sentence_mean_vector

import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
print('현재 경로:', os.path.abspath('.'))

class NewsPreprocessor():
    
    def __init__(self) -> None:
        self.start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        # self.start_date = '2023-02-01'
        self.end_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        # self.end_date = '2023-02-08'
        self.df = self.read_data('./news_df.csv')

    
    def read_data(self, file_path):
        
        """
        
        크롤링된 뉴스 데이터 불러오기
        
        """
        
        df = pd.read_csv(file_path)
        df['writed_at'] = df['writed_at'].apply(lambda x: pd.to_datetime(x))
        df = df[df['writed_at'].between(self.start_date, self.end_date)]
        
        # content 결측치 데이터 삭제
        df.dropna(subset='content', axis=0, inplace=True)
        
        # content 중 특정 글자 수 이하 삭제
        df['len'] = df['content'].apply(lambda x: len(x))
        df = df[df['len'] > 119]
        df.drop(columns='len', axis=1, inplace=True)
        
        # 날짜 기준 정렬
        df.sort_values(by='writed_at', inplace=True)
        
         # 중복 기사 제거
        df.drop_duplicates(subset='title', keep='first', inplace=True)
        
        # reset_index
        df.reset_index(drop=True, inplace=True)
        
        print('데이터 불러오기 완료!')
        
        return df
        
    def preprocessing(self):
        
        """
        
        텍스트 데이터 전처리
        
        1. 텍스트 정제
        2. 품사 태깅
        3. 중요 토큰 추출
        
        """
        
        # 텍스트 정제
        self.df['content'] = self.df['content'].apply(lambda x: text_cleaning(x))
        
        # 품사 태깅
        self.df['pos'] = self.df['content'].apply(lambda x: tokenize(x))
        
        # 중요 토큰 추출
        # self.df['noun'] = self.df['pos'].apply(lambda x: [token[0] for token in x if token[1] == 'Noun'])
        # self.df['verb'] = self.df['pos'].apply(lambda x: [token[0] for token in x if token[1] == 'Verb'])
        # self.df['adverb'] = self.df['pos'].apply(lambda x: [token[0] for token in x if token[1] == 'Adverb'])
        # self.df['adjective'] = self.df['pos'].apply(lambda x: [token[0] for token in x if token[1] == 'Adjective'])
        self.df['token_important'] = self.df['pos'].apply(lambda x: [token[0] for token in x if token[1] == 'Noun' or token[1] == 'Verb' or token[1] == 'Adverb' or token[1] == 'Adjective' or token[1] == 'Alpha'])
        
        self.df['len'] = self.df['token_important'].map(len)
        self.df = self.df[self.df['len'] != 0]
        self.df.drop(columns='len', axis=1, inplace=True)
        
        print('전처리 완료!')
        
        return self.df
    
    def embedding(self):
        
        """
        
        단어 임베딩 (FastText)을 기반으로 클러스터링을 위한 뉴스 기사별 벡터 생성
        
        """
        
        self.df = embedding(self.df)
        
        print('단어 임베딩 완료!')
        
        return self.df
    
    def cluster(self):
        
        """
        
        뉴스 벡터를 기반으로 클러스터링 진행
        
        """
        
        # 클러스터링
        from sklearn.cluster import DBSCAN
        
        dbscan = DBSCAN(eps=0.5, min_samples=50)
        news_vectors = self.df['wv_total'].to_list()
        dbscan.fit(news_vectors)
        
        # 뉴스 기사별 클러스터링 결과 저장
        self.df['cluster_label'] = dbscan.labels_
        
        print('클러스터링 완료!')
        
        return self.df
    
    def save_file(self):
        
        """
        
        전처리, 클러스터링 완료된 데이터 저장
        
        """
        self.df.to_csv('./preprocessed.csv', encoding='utf-8-sig', index=False)
        
if __name__ == '__main__':
    
    preprocessor = NewsPreprocessor()
    preprocessor.preprocessing()
    preprocessor.embedding()
    preprocessor.cluster()
    preprocessor.save_file()
    print('모두 완료!')