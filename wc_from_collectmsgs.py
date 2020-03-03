# generate wordcloud from collect_msgs.json
# - https://github.com/amueller/word_cloud
# - https://teratail.com/questions/147091
from janome.tokenizer import Tokenizer
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import json
from pathlib import Path


def get_wakati_words(tokenizer, text):
    # make word list (名詞抽出)
    words_list = []
    tokens = tokenizer.tokenize(text, stream=True)
    for token in tokens:
        word = token.surface
        partofSpeech0 = token.part_of_speech.split(',')[0]
        partofSpeech1 = token.part_of_speech.split(',')[1]
        # extract
        if partofSpeech0 == '名詞':
            if (partofSpeech1 != "非自立") and (partofSpeech1 != "代名詞") and (partofSpeech1 != "数"):
                words_list.append(word)
    # return wakati string
    wakati_words = ' '.join(words_list)
    return wakati_words


def main():
    # load user messages
    collect_msgs_fpath = 'collect_msgs.json'
    print('load {0} ...'.format(collect_msgs_fpath))
    with open(collect_msgs_fpath, 'r', encoding='utf-8') as f:
        msgs_by_usr = json.load(f)
    # preproccess
    outdir = './wordcloud_img'
    p = Path(outdir)
    if p.exists() == False:
        p.mkdir()
    t = Tokenizer()  # tokenizer のイニシャライズは一回に留める
    stop_words = ['さん', 'お願い', 'そう']  # 都度追加
    print('stop words are : {0} ...'.format(stop_words))
    # generate
    user_num = len(msgs_by_usr.keys())
    for i, (k, v) in enumerate(msgs_by_usr.items()):
        # output file name
        wc_png_fname = outdir + '/' + str(k) + '.png'
        # join lines
        msg_online = ''.join(v)
        # 分かち書きした文字列を取得
        wakati_str = get_wakati_words(t, msg_online)
        # font path
        fontpath = './rounded-l-mplus-1c-regular.ttf'
        # chk
        if wakati_str == '':
            print('message string is empty ({0})'.format(str(k)))
            continue
        # generate
        wordcloud = WordCloud(
            font_path=fontpath,
            width=900, height=600,  # default w:400, h:200
            background_color='white',
            stopwords=set(stop_words),
            max_words=500,   # default=200
            collocations=False  # default = True
        ).generate(wakati_str)
        # save image
        print('output wordcloud img({0}/{1}): {2} ...'.format((i + 1), user_num, wc_png_fname))
        wordcloud.to_file(wc_png_fname)


if __name__ == "__main__":
    main()
