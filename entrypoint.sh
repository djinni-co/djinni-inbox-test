#!/bin/sh

python -m spacy download en_core_web_sm | true
python manage.py calculate_similarity_scores  | true
python manage.py runserver:8000
