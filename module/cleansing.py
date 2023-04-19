def cleansing(text:str, writer:str=None) -> str:  # 통합 클렌징 코드
        import re
        
        # 특수기호 제거
        text = re.sub('[▶△▶️◀️▷ⓒ■◆●©️]', '', text)
        # ·ㆍ■◆△▷▶▼�"'…※↑↓▲☞ⓒ⅔
        
        text = text.replace('“','"').replace('”','"')
        text = text.replace("‘","'").replace("’","'")

        # 인코딩오류 해결 (공백으로 치환)
        text = re.sub('[\xa0\u2008\u2190]', ' ', text)

        # URL제거를 위해 필요없는 문구 처리
        text = text.replace('https://', '')
        # 이메일 처리, URL 제거
        # '[\w\.-]+(\@|\.)[\w\.-]+\.[\w\.]+'
        text = re.sub('([\w\-]+(\@|\.)[\w\-.]+)', '', text)

        # 기자 제거
        # [~~~ 이데일리 ~~ 기자 ~~~]
        if writer:
            left_s, right_s, not_left, not_right = ('[\(\{\[\<]', '[\)\}\]\>]', '[^\(\{\[\<]', '[^\)\}\]\>]')
            try:
                text = re.sub('%s%s+%s%s+?%s'%(left_s, not_right, writer, not_left, right_s), '', text)
            except:
                pass

        # ., 공백, 줄바꿈 여러개 제거 
        # \s -> 공백( ), 탭(\t), 줄바꿈(\n)
        text = re.sub('[\.]{2,}', '.', text)
        text = re.sub('[\t]+', ' ', text)
        text = re.sub('[ ]{2,}', ' ', text)
        text = re.sub('[\n]{2,}', '\n', text)

        return text
