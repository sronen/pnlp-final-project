# -*- coding: utf-8 -*-

import re
import codecs
import os, sys, time
import corpus_os
import shutil
import string

from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import stopwords

# These are the NLTK English stopwords
#STOPWORDS = set(['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', 'should', 'now'])
#STOPWORDS = stopwords.words('english')

# Tokens must be at least this long or they're discarded
MIN_TOKEN_LENGTH = 3

# Add the ones you wish to preserve, e.g., 'éèëóő...'
NON_ENGLISH_CHARS = ''

def translate_non_alphanumerics(to_translate, translate_to=u'_', 
		chars_to_remove=u'!"#%\'()*+,-./:;<=>?@[\]^_`’{|}~'):
	# http://stackoverflow.com/questions/1324067/how-do-i-get-str-translate-to-work-with-unicode-strings
    translate_table = dict((ord(char), translate_to) for char in chars_to_remove)
    return to_translate.translate(translate_table)


def get_clean_terms(s, decap=True, lemmatize=True, language='english', stopwords_file='None'):
	'''
	Clean the passed string an return the remaining words as a list of terms.
	Removes punctuation, possessives, too-short words, stopwords,
	and numbers. 
	Adapted from DataIAP 2012 by Adam Marcus and Eugene Wu,
	https://github.com/dataiap/dataiap/tree/master/day4/get_terms.py
	'''

	# TODO: cleaning should be done in a single pass for efficiecy.
	# But this is simpler...
	st = s.decode('utf-8')

	# Remove numbers (" \d+"), English possesives ("['s? ]") , and punctuation, in this order
	#st = re.sub("\d+|\'s|[:;,?!#$%()\'\"\.]\| - ", "", s.decode('utf-8'), re.UNICODE)
	
	if language == 'english':
		# Remove English possesives
		st = st.replace('\'s ', ' ').replace('s\' ', ' ') 

	# Remove punctuation and digits: list chars to delete
	to_delete = u'!"#%\'()*+,–-./:;<=>?@[\]^_`’{|}~'+string.digits
#	st = translate_non_alphanumerics(st, u' ', to_delete) # replace with space
	st = translate_non_alphanumerics(st, u' ', to_delete) # replace with space


	orig_terms = st.split()

	# NE removal approximation:
	# Remove ALL capitalized words
	if decap==True:
		terms = filter(lambda term: term[0].islower(), orig_terms)
	else:
		terms = orig_terms

	'''
	# Remove capitalized words not at the beginning of a sentence
	terms = []
	prev_term = "." # allows us to get the first word in the article
	for term in orig_terms:
		if term[0].islower() or prev_term[-1]==".":
			# only add lowercase words or any words after a period
			# print "ADDED: term: %s, Prev term %s" % (term, prev_term) # Debug printouts
			terms.append(term)
		prev_term = term
	'''

	# Convert to lowercase
	terms = map(lambda term: term.lower(), terms)

	# Remove words that are too short. TODO: adjust for unicode?
	terms = filter(lambda term: len(term) >= MIN_TOKEN_LENGTH, terms)
	
	# Remove Stopwords.
	terms = remove_stopwords(language, terms, stopwords_file)

	# Lemmatize words if chosen
	if lemmatize==True:
		terms = lemmatize_or_stem(language, terms)

	# Remove stopwords again, post-lemmatization/stemming
	terms = remove_stopwords(language, terms, stopwords_file)

	return terms

def lemmatize_or_stem(language, terms):
	if language == 'english':
		lem = WordNetLemmatizer()
		terms = map(lambda term: lem.lemmatize(term), terms )
	elif language == 'french':
		from nltk.stem.snowball import FrenchStemmer
		stemmer = FrenchStemmer()
		terms = map(lambda term: stemmer.stem(term), terms)
	elif language == 'spanish':
		from nltk.stem.snowball import SpanishStemmer
		stemmer = SpanishStemmer()
		terms = map(lambda term: stemmer.stem(term), terms)
	return terms

def remove_stopwords(language, terms, stopwords_file):
	# Remove stopwords. Use stopwords_file instead of nltk.corpus, if available.
	# Note that nltk.corpus's stopwords are quite incomplete for non-English.
	if stopwords_file == None:
		STOPWORDS = set(stopwords.words(language))
	else:
		f = open(stopwords_file, 'r')
		for line in f.readlines():
			split = line.split()
			if len(split) == 0:
				continue
			word = split[0]
			STOPWORDS.add(word)
	"""if language == 'en':
		STOPWORDS = set(stopwords.words('english'))
	elif language == 'fr':
		STOPWORDS = set(stopwords.words('french'))
		files = 'stop-words/stop-words-french.txt', 'stop-words/stop-words-french2.txt'
		for filename in files:
			f = open(os.path.dirname(__file__) + '/' + filename, 'r')
			for line in f.readlines():
				split = line.split()
				if len(split) == 0:
					continue
				word = split[0]
				STOPWORDS.add(word)"""
	return filter(lambda term: term.encode('utf-8') not in STOPWORDS, terms)

def create_category_file(root_path, category_name, clean_root_path=None, lem_flag=True, decap_flag=True):
	'''
	Create a single file containing clean tokens for all documents in the 
	passed folder. Assume the folder does not contain any sub-folders.
	-Input: path of corpus root, name of category (=folder in corpus), and
	 path for storing the clean files (default is root_path)
	-Output: file named <categoty_name>.txt in the corpus root
	-Return: number of documents processed.
	'''
	if clean_root_path==None:
		clean_root_path=root_path
	
	category_path = os.path.join(root_path, category_name)
	document_list = corpus_os.get_items_in_folder(category_path)
	
	folder_terms = []
	
	# Get all terms in folder (repetitions must be preserved!)
	for i, doc in enumerate(document_list):
		fin = codecs.open(os.path.join(category_path, doc), 'rU')
		doc_text = fin.read()
		folder_terms.extend(get_clean_terms(doc_text, lemmatize=lem_flag, decap=decap_flag))
		# Add EOL to distinguish between text from different articles
		folder_terms.append('\n')
	
	num_docs = i+1
		
	# Concatenate and write to file
	folder_text_clean = ' '.join(folder_terms)
	
	clean_file_path = os.path.join(clean_root_path, category_name+'.txt' )
	fout = codecs.open(clean_file_path, 'w')
	fout.write(folder_text_clean) # There's already an EOL at the end
	fout.close()
	
	return num_docs


def create_corpus_files(corpus_root, corpus_name=None, lem_flag=True, decap_flag=True):
	'''
	Create a file for each category (=sub-folder), containing clean tokens
	for all documents in that category.
	-Input: path of corpus root, name of sub-folder to create and place files
	 in, flag that indicates whether words should be lemmatized
	-Output: a file for each category, named <categoty_name>.txt, located in
	 a folder named corpus_name under corpus_root (or right under it if None)
	-Return: number of categories processed.
	'''
	st_time = time.time()
	
	categories = corpus_os.get_items_in_folder(corpus_root)
	
	clean_root = os.path.join(corpus_root, corpus_name)
	try:
		os.mkdir(clean_root)
	except OSError:
		# alredy exists, delete and recreate
		shutil.rmtree(clean_root)
		os.mkdir(clean_root)
	print "\n",clean_root
	
	for i, category in enumerate(categories):
		create_category_file(corpus_root, category, clean_root, lem_flag, decap_flag)
	
	num_cats = i+1
	
	print "\nCreated %d files under %s" % (num_cats, clean_root)
	print time.time()-st_time, "seconds\n"
		
	return num_cats, clean_root


def create_corpus_files_separate(corpus_root, corpus_name=None, lem_flag=True, decap_flag=True, 
								language='english', make_new_dir=False, stopwords_file=None):
	'''
	Create a file for each article with only clean tokens.
	-Input: path of corpus root, name of sub-folder to create and place files
	 in, flag that indicates whether words should be lemmatized
	-Output: a file for each article with the original name, located in
	 a folder named corpus_name under corpus_root (or right under it if None)
	-Return: number of articles processed.
	'''
	st_time = time.time()
	
	articles = corpus_os.get_items_in_folder(corpus_root)
	if make_new_dir:
		clean_root = corpus_name
	else:
		clean_root = os.path.join(corpus_root, corpus_name)
	try:
		os.mkdir(clean_root)
	except OSError:
		# alredy exists, delete and recreate
		shutil.rmtree(clean_root)
		os.mkdir(clean_root)
	print "\nCreated folder: ",clean_root
	
	
	for i, doc in enumerate(articles):
		# Get all terms in article (repetitions must be preserved!)
		try:
			fin = codecs.open(os.path.join(corpus_root, doc), 'rU')
		except IOError:
			# If all is well, this should be the folder created by this function.
			# Should be ignored.
			print "Hey, there's a folder here! If it's the same as the folder created above, just ignore this message"
			print "%s%s" % (corpus_root, doc)

		doc_text = fin.read()
		# clean them
		article_text_clean =" ".join(get_clean_terms(doc_text, lemmatize=lem_flag, 
													decap=decap_flag, language=language, stopwords_file=stopwords_file))
		# write to a new file
		clean_file_path = os.path.join(clean_root, doc)
		fout = codecs.open(clean_file_path, 'w')
		fout.write(article_text_clean.encode('utf-8')) # There's already an EOL at the end
		fout.close()
	
	num_articles = i+1
	
	print "\nCreated %d files under %s" % (num_articles, clean_root)
	print time.time()-st_time, "seconds\n"
		
	return num_articles, clean_root


if __name__ == "__main__":
	try:
		corpus_root = sys.argv[1]
	except IndexError:
		print "Usage: python str_corpus_cleaner.py corpus_root [corpus_name=None] [lemmatize=y/n] [decap=y/n] [lang='en'/'fr']\
				[make_new_dir=n]"
		exit()
	try:
		corpus_name = sys.argv[2]
	except IndexError:
		corpus_name = None
	try:
		lem_flag = False if sys.argv[3]=="n" else True
	except IndexError:
		lem_flag = True
	try:
		decap_flag = False if sys.argv[4]=="n" else True
	except IndexError:
		lem_flag = True
	try:
		language = sys.argv[5]
	except IndexError:
		language = 'english'
	try:
		make_new_dir = False if sys.argv[6]=='n' else True
	except IndexError:
		make_new_dir=False
	try:
		stopwords_file = sys.argv[7]
	except IndexError:
		stopwords_file = None
	
	num_docs = create_corpus_files_separate(corpus_root, 
											corpus_name, 
											lem_flag=lem_flag, 
											decap_flag=decap_flag, 
											language=language,
											make_new_dir=make_new_dir,
											stopwords_file=stopwords_file)
	#path of corpus root, name of sub-folder to create and place files
	# in, flag that indicates whether words should be lemmatized
	
	#num_docs = create_corpus_files(corpus_root, corpus_name, lem_flag)
	
	'''
	# Simple test - clean a string:
	
	s = "André Kertész (2 July 1894 – 28 September 1985), born Kertész Andor, was a Hungarian-born photographer known for his groundbreaking contributions to photographic composition and the photo essay."
	
	fname = sys.argv[1]
	fin = codecs.open(fname, 'rU')
	text = fin.read()
	clean_text = get_clean_terms(text)
	
	fout = codecs.open(fname+'.clean3.txt', 'w')
	fout.write(' '.join(clean_text))
	fout.write('\n')
	fout.close()
	'''
