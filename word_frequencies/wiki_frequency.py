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
import corpus_os
import cosine_similarity as cosine_sim
import str_corpus_cleaner, pos_corpus_cleaner
import featured_article_downloader_presentation as get_wiki


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


def classify_article_words(article_words, corpus_tfidfs_per_category, corpus_idf):
	'''
	Find the category that best matches the given article among the given
	categories.
	-Input: (1) list of article terms (2) TF*IDF weights for each document in
	 corpus (3) IDF for the entire corpus
	-Return: top category and a dictionary with match score for the article
	 with each category
	'''
	st_time = time.time()
	
	# Find article TF and TFIDF
	article_tfs = tf_idf.tf(article_words)
	article_tfidfs = tf_idf.tf_idf(article_tfs, corpus_idf, len(corpus_tfidfs_per_category))
	
	# find best match among categories
	sim_scores = defaultdict()
	for cat_name, cat_tfidf_scores in corpus_tfidfs_per_category.iteritems():
		cos_sim_time = time.time()
		sim_scores[cat_name] = \
			cosine_sim.cosine_similarity_dict(article_tfidfs, cat_tfidf_scores)
		
	# sort by value (match score), descending
	match = sorted(sim_scores.iteritems(), key=operator.itemgetter(1), reverse=True)[0][0]
	
	return match, sim_scores


def classify_article_file(article_path, tfidfs_per_doc, idfs, lem_flag=False):
	'''
	classify a single article.
	-Return: matched category and similarity scores for all categories. 
	'''
	st_time = time.time()

	ar_text = codecs.open(article_path, 'rU').read()
	article_words = str_corpus_cleaner.get_clean_terms(ar_text, lem_flag)

	# Classify article
	match, all_scores = classify_article_words( \
		article_words, tfidfs_per_doc, idfs)
	match = match.split('.')[0] # remove file extension, if any

	#print "%s\t%s\t%.3e\t%.3f sec" % \
	#	( article_path.split('/')[-1].replace('.txt',''), \
	#	match[0], match[1], time.time()-st_time )

	return match, all_scores


def batch_classify_gold(root_path, tfidfs_per_doc, idfs, lem_flag=False):
	'''
	Classify all articles under the given categorized folder.
	-Return: a dictionary whose keys=article names and values=tuple of
	(suggested cateogry, real category, dict(similarity scores with categories)
	for each article. 
	'''
	class_results = defaultdict(defaultdict)

	for category_folder in corpus_os.get_items_in_folder(root_path):
		# Get articles in directory
		category_path = os.path.join(root_path, category_folder)
		category_files = corpus_os.get_items_in_folder(category_path)

		for article_file in category_files:
			# Classify article
			st_time = time.time()

			article_path = os.path.join(category_path, article_file)
			match, all_scores = classify_article_file( \
				article_path, tfidfs_per_doc, idfs, lem_flag)

			#print "%s\t%s\t%s\t(%.3e)\ttime: %.3f sec" % \
			#	( article_path.split('/')[-1].replace('.txt',''), \
			#	match, category_folder, match[1], \
			#	time.time()-st_time )

			class_results[article_file] = \
			(match, category_folder, all_scores)

	return class_results


def print_top_terms(tfidfs, num=20):
	for document, terms in tfidfs.iteritems():
		print document
		sorted_by_count_top = sorted(terms.iteritems(), key=operator.itemgetter(1), reverse=True)[:num]
		for pair in sorted_by_count_top:
			print '  ', pair


def classifiy_wiki_article(search_str, tfidfs_per_doc, idfs, lem_flag=False):
	'''
	Get an article from Wikipedia and cllassify it against the provided data
	TODO: not working...
	'''
	base_wiki = 'http://en.wikipedia.org/wiki/'
	wiki_url = base_wiki+search_str.replace(' ', '_')

	ar_text = \
		get_wiki.get_specific_wikipedia_article(wiki_url, markup=False)
	print ar_text	
	article_words = str_corpus_cleaner.get_clean_terms(ar_text, lem_flag)

	return classify_article_words(article_words, tfidfs_per_doc, idfs)


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
	
	match, sim_score = classifiy_wiki_article(search_str, tfidfs_per_doc, idfs)
	
	'''
	# Alternatively, use the POS cleaner
	article_tagged = nltk.pos_tag(nltk.wordpunct_tokenize(ar_text))
	article_taggged_clean = pos_corpus_cleaner.clean_pos(article_tagged)
	article_words = [word for (word,pos) in article_taggged_clean]
	print "POS"
	match, sim = classify_article_words(article_words, tfidfs_per_doc, idfs)
	'''