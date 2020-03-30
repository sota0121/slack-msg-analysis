cd ./d010_data/
pipenv run python slack_msg_extraction.py
cd ../d020_intermediate/
pipenv run python cleaning.py
pipenv run python group_msg_by_user.py
cd ../d030_processing/
pipenv run python morphological_analysis.py
pipenv run python normalization.py
pipenv run python stopword_removal.py
cd ../d031_features/
pipenv run python important_word_extraction.py
cd ../d070_visualization/
pipenv run python wordcloud_from_score.py
cd ../../