from konlpy.tag import Okt

def tokenize(text):
    
    stopword = ['의','이','로','두고','들','를','은','과','수','했다','것','있는','한다','하는','그','있다','할','이런','되기','해야','있게','여기', '와', '과']
    okt = Okt()
    
    word_token = okt.pos(text)
    result = [w for w in word_token if not w[0] in stopword]
    
    return result
