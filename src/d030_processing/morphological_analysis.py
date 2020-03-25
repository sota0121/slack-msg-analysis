# Text processing : Morphological Analysis
# 1. 形態素解析
# 2. 分かち書き（品詞の指定可能）
#  arg0 exclude_pos(除外対象品詞を定義した辞書) 除外を優先
#  arg1 include_pos(抽出対象品詞を定義した辞書)

from janome.tokenizer import Tokenizer
from tqdm import tqdm
import pandas as pd


exc_part_of_speech = {
    "名詞": ["非自立", "代名詞", "数"]
}
inc_part_of_speech = {
    "名詞": ["サ変接続", "一般", "固有名詞"],
}


class MorphologicalAnalysis:

    def __init__(self):
        self.janome_tokenizer = Tokenizer()

    def tokenize_janome(self, line: str) -> list:
        # list of janome.tokenizer.Token
        tokens = self.janome_tokenizer.tokenize(line)
        return tokens

    def exists_pos_in_dict(self, pos0: str, pos1: str, pos_dict: dict) -> bool:
        # Retrurn where pos0, pos1 are in pos_dict or not.
        # ** pos = part of speech
        for type0 in pos_dict.keys():
            if pos0 == type0:
                for type1 in pos_dict[type0]:
                    if pos1 == type1:
                        return True
        return False

    def get_wakati_str(self, line: str, exclude_pos: dict,
                       include_pos: dict) -> str:
        '''
        exclude/include_pos is like this
        {"名詞": ["非自立", "代名詞", "数"], "形容詞": ["xxx", "yyy"]}
        '''
        tokens = self.janome_tokenizer.tokenize(line, stream=True)  # 省メモリの為generator
        extracted_words = []
        for token in tokens:
            part_of_speech0 = token.part_of_speech.split(',')[0]
            part_of_speech1 = token.part_of_speech.split(',')[1]
            # check for excluding words
            exists = self.exists_pos_in_dict(part_of_speech0, part_of_speech1,
                                             exclude_pos)
            if exists:
                continue
            # check for including words
            exists = self.exists_pos_in_dict(part_of_speech0, part_of_speech1,
                                             include_pos)
            if not exists:
                continue
            # append(表記揺れを吸収する為 表層形を取得)
            extracted_words.append(token.surface)
        # wakati string with extracted words
        wakati_str = ' '.join(extracted_words)
        return wakati_str


def make_wakati_for_lines(msg_ser: pd.Series) -> pd.Series:
    manalyzer = MorphologicalAnalysis()
    wakati_msg_list = []
    for msg in tqdm(msg_ser, desc='[mk wakati msgs]'):
        wakati_msg = manalyzer.get_wakati_str(str(msg), exc_part_of_speech,
                                              inc_part_of_speech)
        wakati_msg_list.append(wakati_msg)
    wakati_msg_ser = pd.Series(wakati_msg_list)
    return wakati_msg_ser


def main():
    input_root = '../../data/020_intermediate'
    output_root = '../../data/030_processed'
    # 1. load messages_cleaned.csv
    msgs_cleaned_fpath = input_root + '/' + 'messages_cleaned.csv'
    df_msgs = pd.read_csv(msgs_cleaned_fpath)
    # 2. make wakati string by record
    ser_msg = df_msgs.msg
    df_msgs['wakati_msg'] = make_wakati_for_lines(ser_msg)
    # 3. save it
    msgs_wakati_fpath = output_root + '/' + 'messages_wakati.csv'
    df_msgs.to_csv(msgs_wakati_fpath, index=False)


if __name__ == "__main__":
    main()
