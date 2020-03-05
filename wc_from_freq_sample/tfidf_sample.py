from sklearn.feature_extraction.text import TfidfVectorizer


# sample
# generate dict{'word': score} with tf-idf
corpus = [
    '無料 ごはん おかず ごはん おかず ディナー クーポン クーポン 食事', 
    '無料 ごはん おかず ごはん おかず ランチ  クーポン クーポン 食事 昼飯',
    '']

# tf : 1doc(=corpus[i])で計算
# idf: all docs(=corpus)で計算
# つまり
# corpusの1要素を、1ユーザーの発言にすれば、
# 全ドキュメント＝全ユーザーの発言になり、
# 全ユーザーに共通発言されているものはスコアが低くなる

tfidf_vectorizer = TfidfVectorizer(
    token_pattern='(?u)\\b\\w+\\b', 
    max_features=3000)
feature_matrix = tfidf_vectorizer.fit_transform(corpus)
print('feature_matrix >> ')
print(feature_matrix)
feature_matrix_arr = feature_matrix.toarray()
print('feature_matrix_arr >> ')
print(feature_matrix_arr)

print('tfidf_vectorizer.vocabulary_ >> ')
print(tfidf_vectorizer.vocabulary_)

print('tfidf_vectorizer.get_feature_names() >> ')
print(tfidf_vectorizer.get_feature_names())

print('tfidf_vectorizer.get_params() >> ')
print(tfidf_vectorizer.get_params())
