#!/bin/bash
cd ./d010_data/
python slack_msg_extraction.py
cd ../d020_intermediate/
python make_msg_mart_table.py
python cleaning.py messages.csv
cd ../d030_processing/
python morphological_analysis.py messages_cleaned.csv
python normalization.py messages_cleaned_wakati.csv
python stopword_removal.py messages_cleaned_wakati_norm.csv
cd ../d031_features/
# [opt] --term: 'lw' for lastweek
# [opt] --term: 'lm' for lastmonth
python important_word_extraction.py 1 --term lw
cd ../d070_visualization/
python wordcloud_from_score.py important_words_tfidf_by_term.json
cd ../../