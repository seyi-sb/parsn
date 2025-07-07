#!/bin/bash

cd /Users/your-username/path/to/parsn

# Run fetcher
/usr/bin/python3 fetcher.py

# Git commit and push
git add .
git commit -m "🤖 Auto update at $(date '+%Y-%m-%d %H:%M')" || echo "No changes"
git push
