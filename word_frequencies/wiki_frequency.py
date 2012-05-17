import os, sys, inspect
cmd_folder = os.path.abspath(os.path.split(inspect.getfile(inspect.currentframe() ))[0])
if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)

import time
import operator
import codecs
from collections import defaultdict, Counter

import nltk
from nltk.corpus import CorpusReader

import tf_idf
import cosine_similarity as cosine_sim
import str_corpus_cleaner, pos_corpus_cleaner


# TODO: split set to training and test, and evaluate. maybe 70:30 training:test?

def calculate_corpus_tf_idf(corpus_reader):
	'''
	Calculate TF*IDF weight for each document in given corpus.
	-Input: CorpusReader (either Tagged or PlainText )
	-Return:
	 (1) A dictionary whose keys=document name and values=dictionary
	 with terms for keys and TF*IDF weights for values
	 (2) A dictionary whose keys=terms and values=their IDF
	'''
	st_time = time.time()
		
	# Term Frequency for each category
	tfs_per_document = defaultdict(Counter)
	for document in corpus_reader.fileids():
		terms_in_document = corpus_reader.words(document)
		tfs_per_document[document] = tf_idf.tf(terms_in_document)
		
	# Inverse Document Frequency
	idfs = tf_idf.idf(tfs_per_document)
	
	# key is folder name, value is a list of (term, tfidf score) pairs
	tfidfs_per_document = defaultdict(defaultdict) 
	for document, tfs in tfs_per_document.iteritems():
	    tfidfs_per_document[document] = tf_idf.tf_idf(tfs, idfs, len(tfs_per_document))
		
	print "time to compute TF-IDF weights for corpus: %.3f sec" % (time.time()-st_time)
	return tfidfs_per_document, idfs


def classify_article_tfidf(article_words, corpus_tfidfs_per_category, corpus_idf):
	'''
	Find the category that best matches the given article among the given
	categories.
	-Input: (1) list of article terms (2) TF*IDF weights for each document in
	 corpus (3) IDF for the entire corpus
	-Return: a dictionary with match score for the article with each category
	'''
	st_time = time.time()
	
	# Find article TF and TFIDF
	article_tfs = tf_idf.tf(article_words)
	article_tfidfs = tf_idf.tf_idf(article_tfs, corpus_idf, len(corpus_tfidfs_per_category))
	
	# find best match among categories
	sim = defaultdict()
	for cat_name, cat_tfidf_scores in corpus_tfidfs_per_category.iteritems():
		cos_sim_time = time.time()
		sim[cat_name] = \
			cosine_sim.cosine_similarity_dict(article_tfidfs, cat_tfidf_scores)
		
	# sort by value (match score), descending
	match = sorted(sim.iteritems(), key=operator.itemgetter(1), reverse=True)[0]
	
	return match, sim


def print_top_terms(tfidfs, num=20):
	for document, terms in tfidfs.iteritems():
		print document
		sorted_by_count_top = sorted(terms.iteritems(), key=operator.itemgetter(1), reverse=True)[:num]
		for pair in sorted_by_count_top:
			print '  ', pair


if __name__ == "__main__":	
	try:
		root_path = sys.argv[1]
	except IndexError:
		print "Usage: python wiki_frequency.py <file or folder to load files from into corpus>"
		exit()
	
	# Initialize a plain-text corpus 
	training_corpus = nltk.corpus.PlaintextCorpusReader( \
		'../datasets/cleaned_featured_bios/_filtered_3_plus/', '.*\.txt')
	# Alternatively, use a POS-tagged corpus
	# corpus = nltk.corpus.TaggedCorpusReader( \
	#	'../datasets/cleaned_featured_bios/_filtered_3_plus/')
	
	# Calculate TF*IDF for each category and IDF for the entrie corpus
	tfidfs_per_doc, idfs = calculate_corpus_tf_idf(training_corpus)
	#print_top_terms(tfidfs_per_doc)
	
	# Initialize new article
	ar_text = codecs.open(root_path+'/'+'Media biographies/Cillian_Murphy.txt', 'rU').read()
	article_words = str_corpus_cleaner.get_clean_terms(ar_text)	
	print "STR"
	math, sim = classify_article_tfidf(article_words, tfidfs_per_doc, idfs)
		
	# Alternatively, use the POS cleaner
	article_tagged = nltk.pos_tag(nltk.wordpunct_tokenize(ar_text))
	article_taggged_clean = pos_corpus_cleaner.clean_pos(article_tagged)
	article_words = [word for (word,pos) in article_taggged_clean]
	print "POS"
	match, sim = classify_article_tfidf(article_words, tfidfs_per_doc, idfs)
