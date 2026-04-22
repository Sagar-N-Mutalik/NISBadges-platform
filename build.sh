#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
# Your new custom command
python manage.py create_superuser_if_not_exists

# Optional: Seed the other team members
python manage.py seed_users