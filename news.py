import pandas as pd
from datetime import datetime, timedelta

import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
print('현재 경로:', os.path.abspath('.'))

class NewsHelper:
    
    def __init__(self) -> None:
        self.df = self.read_data('./preprocessed.csv')
        self.start_date = pd.to_datetime((datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'))
        # self.start_date = '2023-2-1'
        self.year = self.start_date.split('-')[0]
        self.month = self.start_date.split('-')[1]
        self.week_number = self.get_week_number()
        self.cluster_result = {}
        self.text = ''
        pass
        
    def read_data(self, file_path):
        
        """
        
        전처리, 클러스터링 완료된 데이터 불러오기
        
        """
        
        df = pd.read_csv(file_path)
        df['writed_at'] = df['writed_at'].apply(lambda x: pd.to_datetime(x))
        
        from ast import literal_eval
        df['token_important'] = df['token_important'].map(literal_eval)
        
        print('데이터 불러오기 완료!')
        
        return df
        
    def get_week_number(self):
    
        date_value = pd.to_datetime(self.start_date)
        return str((date_value.isocalendar()[1] - date_value.replace(day=1).isocalendar()[1] + 1))
    
    def summarize(self):
        
        """
        
        클러스터링 결과를 바탕으로 클러스터별 주요 키워드 및 요약 결과 저장
        
        """
        
        from collections import Counter
        from gensim.summarization.summarizer import summarize
        stopword = ['은', '는', '이', '가', '등', '고', '와', '해', '된']
        
        cluster_labels = list(self.df['cluster_label'].unique())
        cluster_labels.remove(-1)
        cluster_labels = sorted(cluster_labels)
        
        for label in cluster_labels:
            cluster_data = self.df[self.df['cluster_label'] == label]
            
            # 중요 키워드 추출 (빈도 기반)
            cluster_tokens = [token for tokens in cluster_data['token_important'].to_list() for token in tokens]
            token_count_dict = Counter(cluster_tokens)
            token_top_20 = dict([token for token in token_count_dict.most_common() if not token[0] in stopword][:20])
            self.cluster_result[label] = {'keyword' : token_top_20}
            
            # 문서 요약
            summarize_result = ' '.join(cluster_data['content'].to_list())
            while True:
                summarize_result = summarize(summarize_result, ratio=0.1)
                if len(summarize_result.split('\n')) <= 10:
                    break
            
            summarize_result = list(set(summarize_result.split('\n')))
            self.cluster_result[label].update({'summarization' : summarize_result})
        
        print('요약 완료!')
        
        return self.cluster_result

    
    # def wordcloud(self):
        
    #     from wordcloud import WordCloud
        
    #     for label in self.cluster_result:
    #         wordcloud = WordCloud(font_path='../font/NanumSquareR.ttf',
    #                               background_color='white',
    #                               max_font_size=70).generate_from_frequencies(self.cluster_result[label]['keyword'])
    #         plt.figure(figsize=(6, 6))
    #         plt.imshow(wordcloud, interpolation='bilinear')
    #         plt.axis('off')
    #         plt.savefig(f'../wordcloud/cluster{result}.png')
    
    
    def write_text(self):
        
        """
        
        뉴스 요약 결과를 바탕으로 뉴스레터 메일 본문 텍스트 작성
        
        """
        
        title = f'''
        
        💌 {self.year}년 {self.month}월 {self.week_number}주차 뉴스 요약 💌
            
        '''
        
        self.text += title
        
        for label in self.cluster_result:
            
            keyword = ' '.join(self.cluster_result[label]['keyword'])
            summarization = '\n    '.join(self.cluster_result[label]['summarization'])
            
            content = f'''
            
            ✅ 주요 키워드 {label + 1} : {keyword}
            
            ➔ 내용 요약
            
            {summarization}
            
            '''
            
            self.text += content
        
        with open('mail_text.txt', 'w') as f:
            f.write(self.text)
            
        print('뉴스레터 작성 완료!')
            
        return self.text
    
    def send_email(self):
        
        """
        
        뉴스 요약 결과를 메일로 발송
        
        """
        
        import smtplib
        import email
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText

        SMTP_SERVER = 'smtp.naver.com'
        SMTP_PORT = 465
        SMTP_USER = 'jennyjhh@naver.com'
        SMTP_PASSWORD = open('./config', 'r').read().strip()
        
        to_users = ['jennyjhh@naver.com', 'dlagmlsk8@gmail.com']
        target_addr = ','.join(to_users)
        
        with open('mail_text.txt', 'r') as f:
            contents = f.read()
        
        subject = contents.split('\n')[2].strip()
        text = MIMEText(contents)
        
        msg = MIMEMultipart('alternative')
        msg['From'] = SMTP_USER
        msg['To'] = target_addr
        msg['Subject'] = subject
        msg.attach(text)
        
        smtp = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        smtp.login(SMTP_USER, SMTP_PASSWORD)
        smtp.sendmail(SMTP_USER, target_addr, msg.as_string())
        smtp.close()
        
        print('메일 발송 완료!')
    
    def delete_news(self):
        
        """
        
        뉴스레터 발송 후 이전 일주일 뉴스 데이터만 남기고 불필요한 데이터 삭제
        
        """
        start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d') 
        start_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d') 
        self.df = self.df[self.df['writed_at'].between(start_date, end_date)]
        self.df.to_csv('./news.df.csv', index=False)
        return self.df


if __name__ == '__main__':
    
    news = NewsHelper()
    
    news.summarize()
    news.write_text()
    news.send_email()
    news.delete_news()