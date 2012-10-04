readme.txt

(note: Download Mallet from http://mallet.cs.umass.edu/download.php)


1) Get the articles

Run: python featured_article_downloader.py corpus_path

Creates a folder containing bio articles in relatively plain text (there are still some tags), with a sub-folder for each category; each aritlce is stored in its own text file.=


2) Run classifier: TF*IDF
**************************


A) Convert articles to clean text (remove the tags)

Run: article_cleaner.py src_dir target_dir

-Cleans notes and other tags that are still found in the plain text files retrieved from Wikipedia. Stored the output in target_dir.
-Note that we use make_clean_dataset_directory()

B) Classify

Run: python eval_class.py corpus_root

-corpus_os.split_training_and_test()
Split corpus into training and test and store each part in a _training_ or _test_ sub-folders respectively. 

-str_corpus_cleaner.create_corpus_files()
Prepare the training set: clean (remove punctuation, possessives, too-short words stopwords, and numbers;  lemmatize remaining tokens). Then, for each category, create one file that contains the text of all of its articles. Output files are stored in _training_/_eval_

-str_corpus_cleaner.create_corpus_files_separate()
**This is not a part of the script, but used with Mallet**
Prepare the training set: clean (remove punctuation, possessives, too-short words stopwords, and numbers;  lemmatize remaining tokens. Then create a file for each article that contains the clean text.

-train_and_test()
Calculate the TF*IDFs for the training and return the results (train_and_test()). 

-eval_stats()
Compare results to reference and compute recall, precision, and f-measure. 

3) Run Classifier: Naive Bayes
********************************

A) Clean and store the relatively-plain text:
-From a python shell, run: article_cleaner.make_paragraph_dataset()
-Pickle the result using pickle.dump(). Name the pickled file paragraph_data.pkl

B) Run the classifier: 
python paragraph_classifier.py [number_repeitions] 
