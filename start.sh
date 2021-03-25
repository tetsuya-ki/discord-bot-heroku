#!/bin/sh

# first
#source venv/bin/activate
# pip install -r requirements.txt
# pip install flask
# python assitantbot.py

poetry install
poetry run python assitantbot.py