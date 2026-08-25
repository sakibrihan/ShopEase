#!/usr/bin/env bash
# exit on error
set -o errexit

python -m pip install -r requirements.txt
python manage.py collectstatic --no-input

# Copy media files so WhiteNoise can serve them in production
cp -r media/ staticfiles/media/

python manage.py migrate
