# -*- coding: utf-8 -*-

import re
import codecs
import os, sys, time
import corpus_os

# These are the NLTK English stopwords
STOPWORDS = set(['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', 'should', 'now'])

# Tokens must be at least this long or they're discarded
MIN_TOKEN_LENGTH = 3

# Add the ones you wish to preserve, e.g., 'éèëóő...'
NON_ENGLISH_CHARS = ''

def get_clean_terms(s):
	'''
	Clean the passed string an return the remaining words as a list of terms.
	Removes punctuation, possessives, too-short words, stopwords,
	and numbers. 
	Adapted from DataIAP 2012 by Adam Marcus and Eugene Wu,
	https://github.com/dataiap/dataiap/tree/master/day4/get_terms.py
	'''
	
	# TODO: remove capitalized words not at the beginning of a sentence?
	
	s = s.lower()
	terms = s.split()
	
	# Remove puncuation
	terms = map(lambda term: term.replace("'s",'').replace("'", '').replace(".", "").replace(",", ""), terms)
	
	# Remove words that are too short
	terms = filter(lambda term: len(term) >= MIN_TOKEN_LENGTH, terms)
	
	# Remove stopwords (English)
	terms = filter(lambda term: term not in STOPWORDS, terms)
	
	# Remove numbers, preserving non-English characters in NON_ENGLISH_CHARS
	r = re.compile("^[a-zA-Z%s]+[a-zA-Z\'\-%s]*[a-zA-Z%s]+$" % \
		(NON_ENGLISH_CHARS, NON_ENGLISH_CHARS, NON_ENGLISH_CHARS), re.UNICODE)
	terms = filter(lambda term: r.match(term), terms)
	
	#terms = filter(lambda term: re.match("^[a-zA-Z]+[a-zA-Z\'\-]*[a-zA-Z]+$", term), terms)
	
	return terms


def create_category_file(root_path, category_name, clean_root_path=None):
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
		folder_terms.extend(get_clean_terms(doc_text))
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


def create_corpus_files(corpus_root, corpus_name=None):
	'''
	Create a file for each category (=sub-folder), containing clean tokens
	for all documents in that category.
	-Input: path of corpus root
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
		create_category_file(corpus_root, category, clean_root)
	
	num_cats = i+1
	
	print "\nCreated %d files under %s" % (num_cats, clean_root)
	print time.time()-st_time, "seconds\n"
		
	return num_cats, clean_root


if __name__ == "__main__":
	
	try:
		corpus_root = sys.argv[1]
	except IndexError:
		exit()
	
	num_docs = create_corpus_files(corpus_root)
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
