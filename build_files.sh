#!/bin/bash
echo "Building static files for Vercel deployment..."
python3 -m pip install -r requirements.txt
python3 manage.py collectstatic --noinput --clear
echo "Build finished successfully."
