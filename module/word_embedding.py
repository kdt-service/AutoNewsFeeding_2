import numpy as np
from gensim.models import FastText

def embedding(df):
    
    token_list = df['token_important'].to_list()
    ft_model = FastText(token_list,
                        vector_size=50,
                        window=4,
                        min_count=1,
                        alpha=0.025,
                        sg=1,
                        epochs=10,
                        min_n=2,
                        max_n=4)
    
    df['wv_total'] = df['token_important'].apply(lambda x: get_sentence_mean_vector(x, ft_model))
    
    return df

def get_sentence_mean_vector(morphs, model):
    vector = []
    for i in morphs:
        try:
            vector.append(model.wv[i])
        except KeyError as e:
            pass
    try:
        return np.mean(vector, axis=0)
    except IndexError as e:
        pass