from sklearn.feature_extraction.text import CountVectorizer
from janome.tokenizer import Tokenizer
# from scipy.sparse import csr

# https://mocobeta.github.io/janome/api/janome.html#module-janome.tokenizer
# http://www.nltk.org/book-jp/ch12.html
# https://qiita.com/shino00/items/3fc2f5c676fb5e4d1a49


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

    def morphological_info(self, text):
        wgen = self.tokenizer.tokenize(text, stream=True)
        mi_arr = []
        for w in wgen:
            mi = [w.surface, w.part_of_speech]
            mi_arr.append(mi)
        return mi_arr
    
    def frequency_info(self, text, part_of_speech='名詞'):
        word_freq_dic = {}
        wgen = self.tokenizer.tokenize(text, stream=True)
        for w in wgen:
            word = w.surface
            ps = w.part_of_speech
            # 指定した品詞のみ処理対象とする
            if ps.find(part_of_speech) < 0:
                continue
            if word not in word_freq_dic.keys():
                word_freq_dic[word] = 0
            word_freq_dic[word] += 1
        return word_freq_dic

    def get_X_array(self):
        return self.X.toarray()
    
