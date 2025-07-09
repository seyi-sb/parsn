#!/bin/bash

# Exit immediately on any error
set -e

# Navigate to project directory
cd /home/ubuntu/parsn

# Make sure we're on main branch
git checkout main

# Pull latest changes from GitHub
git fetch origin
git reset --hard origin/main

# Run your fetcher script to generate new index.html and articles.json
python3 fetcher.py

# Stage and commit any new changes
git add articles.json index.html
git commit -m "🤖 Auto update from EC2"

# Push to GitHub
git push origin main

