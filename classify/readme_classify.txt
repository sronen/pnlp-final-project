readme.txt

(note: Download Mallet from http://mallet.cs.umass.edu/download.php)


1) Get the articles

Run: python featured_article_downloader.py corpus_path

Creates a folder containing bio articles in relatively plain text (there are still some tags), with a sub-folder for each category; each aritlce is stored in its own text file.

French: python featured_article_downloader.py french english_path french_path (requires you to have already downloaded the English articles. This script goes and downloads the French versions of all those articles.)


2) Clean the text: 

str_corpus_cleaner.create_corpus_files_separate()

**This is not a part of the script, but used with Mallet**
Prepare the training set: clean (remove punctuation, possessives, too-short words stopwords, and numbers;  lemmatize remaining tokens. Then create a file for each article that contains the clean text.

Older files can be found under z_v2 or z_v1