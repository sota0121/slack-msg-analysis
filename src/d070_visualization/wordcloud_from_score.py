from wordcloud import WordCloud
import matplotlib.pyplot as plt
import json
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
from tqdm import tqdm
import sys
import argparse


def main(input_fname: str):
    input_root = '../../data/031_features'
    output_root = './wordcloud_by_user' if 'by_user' in input_fname else './wordcloud_by_term'
    p = Path(output_root)
    if p.exists() is False:
        p.mkdir()
    # -------------------------------------
    # 1. load tf-idf score dictionary
    # -------------------------------------
    d_word_score_by_user = {}
    tfidf_fpath = input_root + '/' + input_fname
    with open(tfidf_fpath, 'r', encoding='utf-8') as f:
        d_word_score_by_user = json.load(f)
    # -------------------------------------
    # 2. gen word cloud from score
    # -------------------------------------
    fontpath = './rounded-l-mplus-1c-regular.ttf'
    for uname, d_word_score in tqdm(d_word_score_by_user.items(), desc='word cloud ...'):
        # img file name is user.png
        uname = str(uname).replace('/', '-')
        out_img_fpath = output_root + '/' + uname + '.png'
        # gen
        wc = WordCloud(
            background_color='white',
            font_path=fontpath,
            width=900, height=600,
            collocations=False
            )
        wc.generate_from_frequencies(d_word_score)
        wc.to_file(out_img_fpath)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_fname", help="set input file name", type=str)
    args = parser.parse_args()
    input_fname = args.input_fname
    main(input_fname)