# Text Processing : Cleaning text noise
# 現段階のクリーニング対象
# - url link (<https://...>): regex >> "(<)http.+(>)"
# - reaction (:grin:) : regex >> "(:).+\w(:)"
# - html kw (&lt;, 	&gt;, &amp;, &nbsp;, &ensp;, &emsp;, &ndash;, &mdash;) : regex >> "(&).+?\w(;)"
# - mention (<@XXXXXX>) : regex >> "(<)@.+\w(>)"
import re
import pandas as pd


def clean_msg(msg: str) -> str:
    # sub 'url link'
    result = re.sub(r'(<)http.+(>)', '', msg)
    # sub 'mention'
    result = re.sub(r'(<)@.+\w(>)', '', result)
    # sub 'reaction'
    result = re.sub(r'(:).+\w(:)', '', result)
    # sub 'html key words'
    result = re.sub(r'(&).+?\w(;)', '', result)
    return result


def clean_msg_ser(msg_ser: pd.Series) -> pd.Series:
    cleaned_msg_list = []
    for i, msg in enumerate(msg_ser):
        cleaned_msg = clean_msg(str(msg))
        cleaned_msg_list.append(cleaned_msg)
    cleaned_msg_ser = pd.Series(cleaned_msg_list)
    return cleaned_msg_ser


def main():
    input_root = '../../data/020_intermediate'
    output_root = input_root
    # 1. load messages.csv (including noise)
    msgs_fpath = input_root + '/' + 'messages.csv'
    df_msgs = pd.read_csv(msgs_fpath)
    # 2. clean message string list
    ser_msg = df_msgs.msg
    df_msgs.msg = clean_msg_ser(ser_msg)
    # 3. save it
    msgs_cleaned_fpath = output_root + '/' + 'messages_cleaned.csv'
    df_msgs.to_csv(msgs_cleaned_fpath, index=False)


if __name__ == "__main__":
    main()
