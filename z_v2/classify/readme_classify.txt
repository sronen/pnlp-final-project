readme.txt

(note: Download Mallet from http://mallet.cs.umass.edu/download.php)


1) Get the articles

Run: python featured_article_downloader.py corpus_path

Creates a folder containing bio articles in relatively plain text (there are still some tags), with a sub-folder for each category; each aritlce is stored in its own text file.

French: python featured_article_downloader.py french english_path french_path (requires you to have already downloaded the English articles. This script goes and downloads the French versions of all those articles.)


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
In this section, ">>" means you should run this command from your python shell.

A) Clean and store the relatively-plain text:

>> paragraph_data = article_cleaner.make_paragraph_dataset()
Pickle the result, and name it paragraph_data.pkl.
>> pickle.dump(paragraph_data, open('paragraph_data.pkl', 'w'))

B) Get a nutritional label for a specific article:

Get the "data list" for the article - essentially, this is a list of paragraphs. It is
called a data list because each paragraph is classified separately. The data list can
be found in the paragraph_data.pkl file you made earlier.
>> article_data = paragraph_data_pkl[bio_type][article_name]

Get a paragraph classifier. 
>> classifier = paragraph_classifier.get_classifier('paragraph_data.pkl')

Run the classifier on the article data:
>> paragraph_classifier.get_article_nutritional_label(article_data_list, classifier)

C) Get a breakdown of how often each nutritional label is used for a given bio type:

Run this command, where we look at num_per_cat articles in each category.
>> paragraph_classifier.get_nutritional_labels('paragraph_data.pkl', classifier, num_per_cat)

D) Evaluate the classifier:

Right now the goal is to re-classify every paragraph to the type of bio it came from. Not very useful.
-python paragraph_classifier.py [number_repetitions] 

