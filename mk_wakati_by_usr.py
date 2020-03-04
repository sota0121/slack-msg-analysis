# collect_msgs.json を読み込んで
# corpus_by_usr.json を出力する
# -------------------------------
# corpus_by_usr.json の仕様↓↓
# {
#  'usr_id0': 'wakati string0(all msgs of this usr)',
#  'usr_id1': 'wakati string1(all msgs of this usr)',
#  ...
# }
# -------------------------------
import json
from janome.tokenizer import Tokenizer
from tqdm import tqdm


def load_msgs_by_user(fpath):
    print('load {0} ...'.format(fpath))
    with open(fpath, 'r', encoding='utf-8') as f:
        msgs_by_usr = json.load(f)
        return msgs_by_usr


def get_wakati_string(tokenizer, stop_words, text):
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
    # remove stopwords
    words_list = [x for x in words_list if x not in stop_words]
    # return wakati string
    wakati_string = ' '.join(words_list)
    return wakati_string


def main():
    # ---------------------------------------------------
    # load collect_msgs.json
    # ---------------------------------------------------
    msgs_by_user = load_msgs_by_user('collect_msgs.json')
    # ---------------------------------------------------
    # do wakati
    # ---------------------------------------------------
    print('make wakati string by user ...')
    stop_words = ['さん', 'お願い', 'そう', '参加', 'gt', '&', '...', ';', ':']
    print('stopwords are {0} ...'.format(stop_words))
    t = Tokenizer()
    wakati_by_usr = {}
    for (uname, umsgs) in msgs_by_user.items():
        print('user: {0} ... '.format(uname))
        wakati_umsgs = []
        for umsg in tqdm(umsgs, desc='[do wakati]'):
            wakati_umsg = get_wakati_string(t, stop_words, umsg)
            wakati_umsgs.append(wakati_umsg)
        wakati_umsgs_oneline = ' '.join(wakati_umsgs)
        wakati_by_usr[uname] = wakati_umsgs_oneline
    # ---------------------------------------------------
    # output wakati_by_usr.json
    # ---------------------------------------------------
    print('output wakati_by_usr.json ...')
    with open('wakati_by_usr.json', 'w', encoding='utf-8') as f:
        json.dump(wakati_by_usr, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    main()
