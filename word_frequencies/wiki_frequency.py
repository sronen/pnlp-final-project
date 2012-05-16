import os, sys, inspect
cmd_folder = os.path.abspath(os.path.split(inspect.getfile(inspect.currentframe() ))[0])
if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)

import nltk
import corpustools as ct
from nltk.corpus import stopwords
import time
import math
from collections import defaultdict
from collections import Counter
import get_terms
from nltk.corpus import PlaintextCorpusReader
from nltk.corpus import TaggedCorpusReader
from nltk.corpus import CorpusReader
import operator
import codecs
import tf_idf
import cosine_similarity as cosine_sim


# TODO: split set to training and test, and evaluate. maybe 70:30 training:test?

def tag_pos_corpus(corpus_to_tag):
	'''
	Tag the POS of all words in passed corpus
	'''
	# should be faster than tagging sentences
	tagged_words = nltk.pos_tag(corpus_to_tag.tokens)
	
	return [(word.decode('utf-8'), pos) for (word,pos) in tagged_words]
	
	# for later?: opening as utf-8 didn't really work. 
	# may want to run replace() on corpus.raw()
	#text = text.replace("\xe2\x80\x94", ' ') # en-dash?
	#text = text.replace("\xc2\xa0", ' ')
	#text = text.replace('\n', ' ')
	#text.decode('utf-8')


def write_pos_to_file(tagged_words, outfile):
	'''
	Save tags to a file, using the format <word1>/<pos1> <word2>/pos<2>, eg:
	# Oslo/np-hl The/at most/ql positive/jj ..
	'''
	fout = codecs.open(outfile, 'w', encoding='utf-8')
	
	for word, pos in tagged_words:
		fout.write("%s/%s " % (word.encode('utf-8'), pos))
		
	fout.close()


def read_pos_from_file(infile):
	fin = codecs.open(infile, 'rU', encoding='utf-8')
	
	word_pos_list = fin.read().split()
	tagged_words = []
	
	for word_pos in word_pos_list:
		word, pos = word_pos.split('/')
		tagged_words.append((word, pos)) 
		
	fin.close()
	return tagged_words


def get_category_names(root_path):
	'''
	Intialize categories from a folder names, discarding hidden files (start
	with '.') and POS directories (start with '_')
	'''
	os.listdir(root_path)
	categories = []
	for folder in os.listdir(root_path):
		if folder[0] not in ['.', '_']:
			categories.append(folder)
		
	return categories



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


def print_top_terms(tfidfs, num=20):
	for folder, terms in tfidfs.iteritems():
	    print folder
	    sorted_by_count_top = sorted(terms, key=lambda (k,v): v, reverse=True)[:num]
	    for pair in sorted_by_count_top:
	        print '\t', pair


def top_n_terms(freqdist, n):
	#sorted_by_count_top = sorted(freqdist, key=lambda (k,v): v, reverse=True)[:n]
	
	top_items = sorted(freqdist.items(), key=operator.itemgetter(1), reverse=True)[:n]
	
	return top_items


def clean_pos(tagged_words_to_clean):
	'''
	Get a list of (word, POS tag) tuples and remove the irrelevant ones.
	'''
	# pos to remove: cardinal numbers, punctuation, and proper nouns
	POS_TO_REMOVE = ["-",".", ",", "?", "!",":",";", "(", ")", "\"", "\'", \
		"PRP", "NNP", "NNPS", "CD", "DT", "POS", "IN", "-NONE-"]
	
	# Get the words to remove. Maybe there's a nicer way to implment this
	clean_list = [(word,pos) for (word,pos) in tagged_words_to_clean if\
		pos not in POS_TO_REMOVE and word not in stopwords.words('english')]
	
	return clean_list


def tag_wiki_corpus(root_path):
	'''
	Create a POS-tagged file for each folder under root_path, which contains all
	words from all files in that folder. The files are stored in a directory
	named _pos_ under root_path, and have a .pos extension.
	'''
	
	# Create direcotry and get a list of all folders to tag, removing
	# hidden files
	try:
		os.makedirs(root_path+"_pos_")
	except OSError:
		pass # directory already exists
	
	categories = get_category_names(root_path)
	
	for category in categories:
		category_root = root_path+category
		print 
		print category_root
		category_corpus = ct.corpus_from_directory(category_root, '.*\.txt')
		print "Created corpus %s, tagging..." % category_root
	
		# Tag POS, remove proper nouns and other irrelevant POS, and store in
		# a file for future use
		st_time = time.time()
		tagged_words = tag_pos_corpus(category_corpus) 
		print ">>> Time to tag:", time.time()-st_time
		
		pos_tagged_file = root_path+"_pos_/"+category+".pos"
		write_pos_to_file(tagged_words, pos_tagged_file)
		print ">>> Created file %s" % (pos_tagged_file)
	
		#print "tagging sentences"
		#tagged_sents = map(lambda x:nltk.pos_tag(x), new_corpus_reader.sents())


def clean_tag_wiki_corpus(root_path):
	'''
	Load a POS-tagged corpus and create a clean version of it, discarding stopwords
	and irrelvant POS (prepositions, proper nouns, etc.).
	The new corpus is stored in a directory nameed _pos_clean_ in under root_path,
	and its files have a .pos.clean extension
	'''
	
	clean_root_path = root_path + "_pos_clean_/"
	try:
		os.mkdir(clean_root_path)
	except OSError:
		pass # probably already exists
		
	# Read the tagged corpus
	wiki_featured_corpus = TaggedCorpusReader(root_path, '.*\.pos')
	
	# Clean and calculate probabilities for each category separately
	clean_tagged_words = defaultdict(defaultdict)
	for category in wiki_featured_corpus.fileids():
		feat_category = nltk.Text(wiki_featured_corpus.words(category))
		
		# Clean and store
		print "Cleaning category %s:" % category,
		st_time = time.time()
		clean_tagged_words[category] = \
			clean_pos(wiki_featured_corpus.tagged_words(category))
		print time.time()-st_time
		write_pos_to_file(clean_tagged_words[category], \
			clean_root_path+category+".clean")
			
	return clean_tagged_words


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
	
	# TODO: one-off preparations should be moved to another module 
	# Tag all documents in the folders under root_path. Store tags for each
	# folder in a file of their own, with a .pos extension. Takes about 1:20
	# hours to tag the Featured Articles corpus
	
	# tag_wiki_corpus(root_path)
	#clean_tag_wiki_corpus(root_path+'_pos_/')

	# now load the entire Wiki corpus, calculate probabilities etc.
	# then, compare to different categories.
	#prob_ratios, all_probs = probability_ratios(root_path+'_pos_clean_/')
	
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