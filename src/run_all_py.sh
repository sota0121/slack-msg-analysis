#!/bin/bash
cd ./d010_data/
python slack_msg_extraction.py
cd ../d020_intermediate/
python group_msg_by_user.py
python cleaning.py
cd ../d030_processing/
python morphological_analysis.py
python normalization.py
python stopword_removal.py
cd ../d031_features/
python important_word_extraction.py
cd ../d070_visualization/
python wordcloud_from_score.py
cd ../../