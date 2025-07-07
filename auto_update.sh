#!/bin/bash
echo "----- Auto update started at $(date '+%Y-%m-%d %H:%M:%S') -----" >> /Users/seyi./Dev/parsn/cron.log

cd /Users/seyi./Dev/parsn

# Run fetcher
python3 fetcher.py

# Git commit and push
git add .
git commit -m "🤖 Auto update" || echo "No changes"
git push
