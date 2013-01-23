#!/bin/bash

# Copy script and namelist to to output dir
mkdir par_corpus/
cp download_articles.py par_corpus/
cp merge_and_delete.py par_corpus/
cp $1 par_corpus/

# run script
cd par_corpus/
python download_articles.py $1

# clean up
python merge_and_delete.py $1
rm download_articles.py
rm merge_and_delete.py