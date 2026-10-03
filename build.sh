#!/usr/bin/env bash
# Script de build execute par Render a chaque deploiement.
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --noinput

# Base SQLite recreee a chaque deploiement (voir config/settings.py) :
# on rejoue les migrations puis on regenere le jeu de donnees de demo.
python manage.py migrate
python manage.py seed_demo
