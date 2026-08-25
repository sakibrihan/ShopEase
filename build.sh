#!/usr/bin/env bash
# exit on error
set -o errexit

python -m pip install -r requirements.txt
python manage.py collectstatic --no-input

# Copy media files into public_root so WhiteNoise serves them at /media/
mkdir -p public_root
cp -r media/ public_root/media/

python manage.py migrate
