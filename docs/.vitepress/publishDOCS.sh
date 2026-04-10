#!/usr/bin/env sh
set -e

# Sync changelog
cp ./CHANGELOG.md ./docs/changelog.md

# Build
npm run docs:build

# Deploy to gh-pages
cd docs/.vitepress/dist
git init
git add -A
git commit -m 'deploy'
git push -f git@github.com:bnznamco/django-structured-metaobjects.git master:gh-pages

cd -
