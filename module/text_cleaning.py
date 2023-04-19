import re

def text_cleaning(text):
    
    pattern = '▲'
    text = re.sub(pattern, ' ', text)
    
    pattern = '\[*\(*\w+ ?= ?\w+\)*\]* ?\w+ ?\w+ \= '
    text = re.sub(pattern, '', text)
    
    pattern = r'(출처|사진(제공)?)=[a-zA-Z가-힣0-9]*'
    text = re.sub(pattern, ' ', text)
    
    pattern = '글 / .*'
    text = re.sub(pattern, ' ', text)

    pattern = '\<.*무단전재 및 재배포 금지.*\>'
    text = re.sub(pattern, ' ', text)

    pattern = '.*\[.*자료사진.*\]'
    text = re.sub(pattern, ' ', text)

    pattern = '.*\[.* 재판매 및 DB ?금지\.*\]'
    text = re.sub(pattern, ' ', text)

    pattern = r'\((\w+)\)'
    text = re.sub(pattern, r' \1', text)

    pattern = '\(*\[*[\w]+ ?= ?[\w]+ ?기자\]*\)*'
    text = re.sub(pattern, '', text)

    pattern = '해외투자 \'한경 글로벌마켓\'과 함께하세요 한국경제신문과 WSJ, 모바일한경으로 보세요'
    text = re.sub(pattern, '', text)

    pattern = '제보는 카톡 okjebo'
    text = re.sub(pattern, '', text)
    
    pattern = '\[서울경제\]'
    text = re.sub(pattern, '', text)
    
    pattern = '\n'
    text = re.sub(pattern, ' ', text)
    
    pattern = ' {2,}'
    text = re.sub(pattern, ' ', text)
    
    text = text.strip()
    
    return text