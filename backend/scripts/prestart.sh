#! /usr/bin/env bash

set -e
set -x

# Let the DB start
python app/backend_pre_start.py

# Run migrations
alembic upgrade head

# Create initial data in DB (superuser)
python app/initial_data.py

# Seed development data (demo tenant, users, company, locations)
python app/db/seeds.py
