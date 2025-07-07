#!/bin/bash

cd /Users/seyi./Dev/parsn

# Run fetcher
python3 fetcher.py

# Git commit and push
git add .
git commit -m "🤖 Auto update" || echo "No changes"
git push
