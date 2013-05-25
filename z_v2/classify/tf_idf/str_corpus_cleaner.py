# -*- coding: utf-8 -*-

import re
import codecs
import os, sys, time
import corpus_os
import shutil
import string

from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import stopwords
import subprocess

# These are the NLTK English stopwords
#STOPWORDS = set(['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', 'should', 'now'])
#STOPWORDS = stopwords.words('english')

ENGLISH_FREELING = False

# Tokens must be at least this long or they're discarded
MIN_TOKEN_LENGTH = 3
NUMBERS = set(['1','2','3','4','5','6','7','8','9','0'])

# Add the ones you wish to preserve, e.g., 'éèëóő...'
NON_ENGLISH_CHARS = ''

def translate_non_alphanumerics(to_translate, translate_to=u'_', 
		chars_to_remove=u'!"#%\'()*+,-./:;<=>?@[\]^_`’{|}~'):
	# http://stackoverflow.com/questions/1324067/how-do-i-get-str-translate-to-work-with-unicode-strings
    translate_table = dict((ord(char), translate_to) for char in chars_to_remove)
    return to_translate.translate(translate_table)

def construct_british_dict(british_english_file='british_english_translations.txt'):
	"""Create dictionary of british -> american"""
	british_dict = dict()

	# format of file: en-US || en-GB {|| possibly extra junk}
	f = open(british_english_file, 'r')
	for line in f.readlines():
		line_split = line.split(' || ')
		us_english = line_split[1]
		british_english = line_split[2]
		british_dict[british_english] = us_english
	return british_dict

BRITISH_DICT = construct_british_dict()

def convert_british_english(terms, british_dict=BRITISH_DICT):
	"""Convert all british words in terms to english words, using the dict as the translator.
	Look up each word in text, and replace any found british words with their american counterpart"""
	for i in range(len(terms)):
		if terms[i] in british_dict:
			terms[i] = british_dict[terms[i]]
	return terms

def get_clean_terms(s, decap=True, lemmatize=True, language='english', stopwords_file='None'):
	'''
	Clean the passed string and return the remaining words as a list of terms.
	Lemmatizes and does NER using FreeLing, and removes NEs.
	Removes punctuation, possessives, too-short words, stopwords,
	and numbers. 
	Adapted from DataIAP 2012 by Adam Marcus and Eugene Wu,
	https://github.com/dataiap/dataiap/tree/master/day4/get_terms.py
	'''

	# TODO: cleaning should be done in a single pass for efficiecy.
	# But this is simpler...
	st = s.decode('utf-8')

	terms = st.split()
	orig_terms = terms
	orig_st = st

	if language == 'spanish' or (language == 'english' and ENGLISH_FREELING):
		"""Lemmatizing before doing any processing ensures the best named entity recognition."""
		# Lemmatize words if chosen
		if lemmatize==True:
			done = False
			while not done:
				# FreeLing segfaults randomly ~1% of the time. Just re-run if that happens.
				done = True
				terms = lemmatize_or_stem(language, orig_terms)
				if len(terms) == 0:
					print 'EXCEPTION'
					print ' '.join(terms)
					done = False
					#return []

	st = ' '.join(terms)

	if language == 'english':
		# Remove English possesives
		st = st.replace('\'s ', ' ').replace('s\' ', ' ') 


	#st = st.decode('utf-8')

	# Remove punctuation and digits: list chars to delete
	to_delete = u'!"#%\'()*+,–-./:;<=>?@[\]^_`’{|}~'+string.digits
	st = translate_non_alphanumerics(st, u' ', to_delete) # replace with space

	# Remove numbers (" \d+"), English possesives ("['s? ]") , and punctuation, in this order
	#st = re.sub("\d+|\'s|[:;,?!#$%()\'\"\.]\| - ", "", s.decode('utf-8'), re.UNICODE)

	terms = st.split()

	#if decap==True:
	# NE removal approximation:
	# Remove ALL capitalized words
	if language=='english' and not ENGLISH_FREELING:
		terms = filter(lambda term: term[0].islower(), terms)

	# Convert to lowercase
	terms = map(lambda term: term.lower(), terms)

	# Remove words that are too short. TODO: adjust for unicode?
	terms = filter(lambda term: len(term) >= MIN_TOKEN_LENGTH, terms)
	
	# Remove Stopwords.
	terms = remove_stopwords(language, terms, stopwords_file)

	# split words on - and _
	new_terms = list()
	for term in terms:
		split_words = term.replace('-', ' ').replace('_', ' ').split()
		if len(split_words) == 1:
			new_terms.append(split_words[0])
		else:
			new_terms += split_words
	terms = new_terms

	if (language == 'english' and not ENGLISH_FREELING and lemmatize==True):
		terms = lemmatize_or_stem(language, terms)

	if language == 'english':
		terms = convert_british_english(terms)

	return terms

def lemmatize_or_stem(language, terms):
	if language == 'spanish' or (language == 'english' and ENGLISH_FREELING): #TEMPORARY: EXPERIMENTING WITH ENGLISH FREELING
		# Use FreeLing
		if language == 'spanish':
			analyzeProcess = subprocess.Popen(["analyze", "-f", "/usr/local/share/FreeLing/config/es.cfg"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
		elif language == 'english':
			analyzeProcess = subprocess.Popen(["analyze", "-f", "/usr/local/share/FreeLing/config/en.cfg"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
		terms = map(lambda term: term.encode('utf-8'), terms)
		analyzeProcess.stdin.write(' '.join(terms))
		stdout, stderr = analyzeProcess.communicate()
		# Parse FreeLing output
		# Lemma is always second word of each line.
		terms = list()
		lines = stdout.split('\n')
		for line in lines:
			items = line.split(' ')
			if len(items) == 4:
				lemma = items[1]
				tag = items[2]
				"""ATTN: TAGSET IS DIFFERENT IN SPANISH AND ENGLISH. However, NP, F, Z, and W
				all mean the same thing in both tagsets."""
				# remove proper nouns, punctuation, numbers, and dates/times
				if not (tag[0:2]=='NP' or tag[0] == 'F' or tag[0] == 'Z' or tag[0] == 'W' or tag[0:3] == 'POS'):
					# if english, need to remove numbers
					include = True
					for num in NUMBERS:
						if num in lemma:
							include = False
					if include:
						terms.append(lemma)
		terms = map(lambda term: term.decode('utf-8'), terms)

	elif (language == 'english' and not ENGLISH_FREELING):
	 	lem = WordNetLemmatizer()
	 	terms = map(lambda term: lem.lemmatize(term), terms )
	elif language == 'french':
		from nltk.stem.snowball import FrenchStemmer
		stemmer = FrenchStemmer()
		terms = map(lambda term: stemmer.stem(term), terms)
	
		terms = map(lambda term: term.decode('utf-8'), terms)
	return terms

def remove_stopwords(language, terms, stopwords_file):
	# Remove stopwords. Use stopwords_file instead of nltk.corpus, if available.
	# Note that nltk.corpus's stopwords are quite incomplete for non-English.
	if stopwords_file == None:
		STOPWORDS = set(stopwords.words(language))
	else:
		# Currently, this path gets taken by Spanish and French, but not English.
		STOPWORDS = set()
		f = open(stopwords_file, 'r')
		for line in f.readlines():
			split = line.split()
			if len(split) == 0:
				continue
			word = split[0]
			STOPWORDS.add(word)

	# for spanish, add all english stopwords too
	if language == 'spanish':
		for word in stopwords.words('english'):
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
	print document_list
	
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
								language='english', make_new_dir=False, stopwords_file=None,
								article_list_file=None):
	'''
	Create a file for each article with only clean tokens.
	-Input: path of corpus root, name of sub-folder to create and place files
	 in, flag that indicates whether words should be lemmatized
	-Output: a file for each article with the original name, located in
	 a folder named corpus_name under corpus_root (or right under it if None)
	-Return: number of articles processed.
	'''
	st_time = time.time()
	
	if article_list_file == None:
		articles = corpus_os.get_items_in_folder(corpus_root)
	else:
		f = open(article_list_file, 'r')
		lines = f.read().split('\n')
		if language == 'english':
			articles = map(lambda line: line.split('\t')[0], lines)
		elif language=='spanish':
			articles = map(lambda line: line.split('\t')[1], lines)
		f.close()
		print 'Number of articles in ' +  article_list_file + ':', len(articles)

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
		print doc
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
		stopwords_file = sys.argv[7] if sys.argv[7] != 'n' else None
	except IndexError:
		stopwords_file = None
	try:
		article_list_file = sys.argv[8]
	except IndexError:
		article_list_file = None
	
	num_docs = create_corpus_files_separate(corpus_root, 
											corpus_name, 
											lem_flag=lem_flag, 
											decap_flag=decap_flag, 
											language=language,
											make_new_dir=make_new_dir,
											stopwords_file=stopwords_file,
											article_list_file=article_list_file)
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