import os, sys, inspect
cmd_folder = os.path.abspath(os.path.split(inspect.getfile(inspect.currentframe() ))[0])
if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)

import nltk
from nltk.corpus import stopwords
import time
from collections import defaultdict
from collections import Counter
from nltk.corpus import PlaintextCorpusReader
from nltk.corpus import TaggedCorpusReader
from nltk.corpus import CorpusReader
import operator
import codecs
import tf_idf
import cosine_similarity as cosine_sim


# TODO: split set to training and test, and evaluate. maybe 70:30 training:test?

def calculate_corpus_tf_idf(pos_clean_root):
	'''
	Calculate TF*IDF weight for each document in given corpus.
	-Return:
	 (1) A dictionary whose keys=document name and values=dictionary
	 with terms for keys and TF*IDF weights for values
	 (2) A dictionary whose keys=terms and values=their IDF
	'''
	st_time = time.time()
	
	# Read the tagged corpus
	whole_corpus = TaggedCorpusReader(pos_clean_root, '.*\.pos.clean')
	
	# Term Frequency for each category
	tfs_per_document = defaultdict(Counter)
	for document in whole_corpus.fileids():
		terms_in_document = whole_corpus.words(document)
		tfs_per_document[document] = tf_idf.tf(terms_in_document)
		
	# Inverse Document Frequency
	idfs = tf_idf.idf(tfs_per_document)
	
	# key is folder name, value is a list of (term, tfidf score) pairs
	tfidfs_per_document = defaultdict(defaultdict) 
	for document, tfs in tfs_per_document.iteritems():
	    tfidfs_per_document[document] = tf_idf.tf_idf(tfs, idfs, len(tfs_per_document))
		
	for document, values in tfidfs_per_document.iteritems():
		print document
		print top_n_terms(values, 20)
		print
		
	print "time to compute:", time.time()-st_time
	return tfidfs_per_document, idfs


def classify_article_tfidf(article, corpus_tfidfs_per_category, corpus_idf):
	'''
	Find the category that best matches the given article among the given
	categories.
	-Input: (1) article path (2) TF*IDF weights for each document in corpus,
	 (3) IDF for the entire corpus
	-Return: a dictionary with match score for the article with each category
	'''
	st_time = time.time()
	
	ar_text = codecs.open(article, 'rU').read()
	
	article_tagged = nltk.pos_tag(nltk.wordpunct_tokenize(ar_text))
	article_taggged_clean = clean_pos(article_tagged)
	article_words = [word for (word,pos) in article_taggged_clean]
	#article_corpus = nltk.Text(article_words)
	
	# Find article TF and TFIDF
	article_tfs = tf_idf.tf(article_words)
	article_tfidfs = tf_idf.tf_idf(article_tfs, corpus_idf, len(corpus_tfidfs_per_category))
	
	# find best match among categories
	sim = defaultdict()
	for cat_name, cat_tfidf_scores in corpus_tfidfs_per_category.iteritems():
		cos_sim_time = time.time()
		sim[cat_name] = \
			cosine_sim.cosine_similarity_dict(article_tfidfs, cat_tfidf_scores)
		
	# sort by value (match score), ascending
	match = sorted(sim.iteritems(), key=operator.itemgetter(1), reverse=True)
	print "match:", match[0]
	print "time to match:", time.time()-st_time
	
	return sim


if __name__ == "__main__":	
	try:
		root_path = sys.argv[1]
	except IndexError:
		print "Usage: python wiki_frequency.py <file or folder to load files from into corpus>"
		exit()
	
	tfidfs_per_doc, idfs = wiki_frequency.calculate_corpus_tf_idf('../datasets/cleaned_featured_bios/_pos_clean_/')
	
	sim = classify_article_tfidf('../datasets/cleaned_featured_bios/Media biographies/Cillian_Murphy.txt', tfidfs_per_doc, idfs)
		
	# Finally - for each article / paragraph, run a cosine similarity of words extract with words in each category to classify?
	# get terms from article
	'''
	sim = calc_similarity(root_path+'Media biographies/Cillian_Murphy.txt', all_probs, prob_ratios)
	sim = calc_similarity(root_path+'Music biographies/AC_DC.txt', all_probs, prob_ratios)
	sim = calc_similarity(root_path+'Literature and theatre biographies/Anton_Chekhov.txt', all_probs, prob_ratios)
	sim = calc_similarity(root_path+'Sport and recreation biographies/Tim_Duncan.txt', all_probs, prob_ratios)
	sim = calc_similarity('../datasets/Tiger_Woods.txt', all_probs, prob_ratios)
	'''