# generate wordcloud from collect_msgs.json
# - https://github.com/amueller/word_cloud
# - https://teratail.com/questions/147091
# - https://www.scss.tcd.ie/~munnellg/projects/visualizing-text.html
# - https://qiita.com/nekoumei/items/b1afca7cfb9e54303ab4
# - https://amueller.github.io/word_cloud/auto_examples/frequency.html
# - http://www.unixuser.org/~euske/doc/postag/
# - https://komei22.hatenablog.com/entry/2019/08/27/124824
# - https://scikit-learn.org/stable/modules/feature_extraction.html#text-feature-extraction
# - 「Python機械学習クックブック」―レシピ6.9：単語への重みづけ
# - https://scikit-learn.org/stable/auto_examples/model_selection/grid_search_text_feature_extraction.html#sphx-glr-auto-examples-model-selection-grid-search-text-feature-extraction-py
# - https://en.wikipedia.org/wiki/Text_corpus
# - https://qiita.com/Hironsan/items/2466fe0f344115aff177
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import json
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
from tqdm import tqdm


def load_wakati_by_user(fpath):
    with open(fpath, 'r', encoding='utf-8') as f:
        wakati_by_usr = json.load(f)
        return wakati_by_usr


def main():
    # =============================================================
    # mk output dir
    # =============================================================
    outdir = './wordcloud_img'
    p = Path(outdir)
    if p.exists() is False:
        p.mkdir()
    # =============================================================
    # load wakati string by usr (this is corpus)
    # =============================================================
    wakati_msg_fpath = 'wakati_by_usr.json'
    print('load {0} ...'.format(wakati_msg_fpath))
    wakati_table = load_wakati_by_user(wakati_msg_fpath)
    uname_list = []
    corpus = []
    for (uname, wakati_str) in wakati_table.items():
        # 分かち書き済み文字列が空のユーザーは除外
        if wakati_str == '':
            continue
        uname_list.append(uname)
        corpus.append(wakati_str)
    # =============================================================
    # tf-idf vectorize
    #  1document = 1userの全発言（分かち書き済み）
    #  idfは all documentes を対象にして計算
    # =============================================================
    tfidf_vectorizer = TfidfVectorizer(
        token_pattern='(?u)\\b\\w+\\b')
    feature_matrix = tfidf_vectorizer.fit_transform(corpus)
    print('TfidfVectorizer params ---------------------------------')
    print(tfidf_vectorizer.get_params())
    print('TfidfVectorizer stopwords ------------------------------')
    print(tfidf_vectorizer.get_stop_words())
    # =============================================================
    # make dict : 'feature' - index in feature_vec
    # =============================================================
    word_fvidx_dict = {}
    for (w, i) in sorted(tfidf_vectorizer.vocabulary_.items(), key=lambda x: x[1]):
        word_fvidx_dict[i] = w
    # =============================================================
    # make tf-idf weight score table by user
    # =============================================================
    print('make tf-idf weight score table by user ...')
    feature_matrix_arr = feature_matrix.toarray()
    ft_tble_by_usr = []
    for (uname, feature_vec) in zip(uname_list, feature_matrix_arr):
        # ユーザごとに単語-scoreのDataFrameを作る
        words = []
        scores = []
        for i in tqdm(feature_vec.nonzero()[0], desc='[{0}]'.format(uname)):
            words.append(word_fvidx_dict[i])
            scores.append(feature_vec[i])
        # 当該ユーザのDataFrameをリストに追加
        dict_word_score = dict(zip(words, scores))
        ft_tble_by_usr.append(dict_word_score)
    # =============================================================
    # generate wordcloud by user with tf-idf weight
    # =============================================================
    user_num = len(ft_tble_by_usr)
    fontpath = './rounded-l-mplus-1c-regular.ttf'
    for i, (uname, ft_tble) in enumerate(zip(uname_list, ft_tble_by_usr)):
        # output file name
        wc_png_fname = outdir + '/' + str(uname) + '.png'
        # generate word cloud
        wc = WordCloud(
            background_color='white', 
            font_path=fontpath,
            width=900, height=600,
            collocations=False
            )
        wc.generate_from_frequencies(ft_tble)
        # save image
        print('output wordcloud img({0}/{1}): {2} ...'.format(
            (i + 1), 
            user_num, 
            wc_png_fname))
        wc.to_file(wc_png_fname)


if __name__ == "__main__":
    main()
