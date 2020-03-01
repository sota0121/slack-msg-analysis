from sklearn.feature_extraction.text import CountVectorizer
from janome.tokenizer import Tokenizer
# from scipy.sparse import csr


# テキストの集合をベクトル化する
class vectorizer:
    def __init__(self):
        self.features = []
        self.X = 0
        self.lines = []
        self.tokenizer = Tokenizer()  # Tokenizerオブジェクトの生成コストは高いので一度だけ

    def vectorize_line(self, text):
        # 分かち書き
        corpus = []
        words = self.tokenizer.tokenize(text, wakati=True)
        for w in words:
            corpus.append(w)
        executer = CountVectorizer()
        self.X = executer.fit_transform(corpus)
        self.features = executer.get_feature_names()
    
    def get_X_array(self):
        return self.X.toarray()
    
