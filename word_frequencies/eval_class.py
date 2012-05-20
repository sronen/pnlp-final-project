import os
import nltk
from nltk import metrics
import wiki_frequency
import str_corpus_cleaner
import time
import corpusus_os 

from collections import defaultdict

def eval_stats(results):
	'''
	Compute recall, precision, and f-measure from passed results.
	The expected format for results is a dictionary whose keys=<name of article>
	and values=tuple (<test category>, <reference category>, <scores>), where:
	test=category suggested by classifier, reference=pre-classified gold
	category, scores=can be None or dictionary whose keys=category names and
	values=matching score for this article.
	'''
	# Create sets of references / test classification for evaluation
	cat_ref = defaultdict(set)
	cat_test= defaultdict(set)
	for name, (test_category, ref_category, scores) in results.iteritems():
		cat_ref[ref_category].add(name) 		# gold-tagged categories
		cat_test[test_category].add(name) 	# suggested categories

	# Precision, recall, f-measure, support (num of reference articles in
	# each category) for each category
	print "\nCategory\tPrecision\tRecall\tF-measure" 
	measures = defaultdict(tuple)
	for category in cat_ref.keys():
		cat_prec = metrics.precision(cat_ref[category], cat_test[category])
		cat_rec = metrics.recall(cat_ref[category], cat_test[category])
		cat_f = metrics.f_measure(cat_ref[category], cat_test[category])
		cat_support = len(cat_ref[category])
		measures[category] = (cat_prec, cat_rec, cat_f, cat_support)
		print "%s\t%0.3f\t%0.3f\t%0.3f\t%d" % \
		(category, cat_prec, cat_rec, cat_f, cat_support)
	
	# Calculate precision, recall, f-measure for entire corpus:
	# This is a weighted average of the values of separate categories
	# SUM(product of all precisions, product of all supports)/sum(total number of supports)
	avg_prec = weighted_average([(cat_measure[0], cat_measure[3]) for \
		cat_measure in measures.values()])
	avg_rec = weighted_average([(cat_measure[1], cat_measure[3]) for \
		cat_measure in measures.values()])
	avg_f = weighted_average([(cat_measure[2], cat_measure[3]) for \
		cat_measure in measures.values()])
	total_support = sum([cat_support[3] for cat_support in measures.values()])
	
	print "%s\t%0.3f\t%0.3f\t%0.3f\t%d" % ("total", avg_prec, avg_rec, avg_f, total_support)
	

def weighted_average(value_weight_list):
	'''
	Takes a list of tuples (value, weight) and
	returns weighted average as calculated by
	Sum of all values * weights / Sum of all weights
	From: http://bcdcspatial.blogspot.com/2010/08/simple-weighted-average-with-python.html
	'''
	
	numerator = sum([v * w for v,w in value_weight_list])
	denominator = sum([w for v,w in value_weight_list])
	if(denominator != 0):
		return(float(numerator) / float(denominator))
	else:
		return None

if __name__ == "__main__":	
	corpus_path = '/Users/shahar/Documents/MIT/Classes/MASS60-PracticalNLP/Project/pnlp-final-project/datasets/cleaned_featured_bios/'
	
	#corpus_path = '/Users/shahar/Documents/MIT/Classes/MASS60-PracticalNLP/Project/pnlp-final-project/datasets/test/'
	
	# Split corpus
	training_root, test_root = corpus_os.split_training_and_test(corpus_path)
	print "Training root: %s\n" % training_root
	print "Test root: %s\n" % test_root
	
	# Create the corpus
	num_docs, training_corpus_path = \
		str_corpus_cleaner.create_corpus_files(training_root, '_eval_')
	
	# Calculate TF*IDF
	training_corpus = nltk.corpus.PlaintextCorpusReader( \
		training_corpus_path, '.*\.txt')
	tfidfs_per_doc, idfs = wiki_frequency.calculate_corpus_tf_idf(training_corpus)
	
	# Test
	print "Classifying test corpus..."
	st_time = time.time()
	results = wiki_frequency.batch_classify_gold(test_root, tfidfs_per_doc, idfs)
	print "Classified %d articles from %s in %.03f seconds" % (len(results), test_root, time.time()-st_time)
	
	# Calculate number of correct matches
	correct = 0
	missed = defaultdict(tuple)
	for article_name, (suggested, real, scores) in results.iteritems():
		if suggested==real:
			correct += 1
		else:
			missed[article_name] = (suggested, real)
	success_ratio = correct / float(len(results))
	print "Ratio: %0.3f" % success_ratio
	
	# Print wrong matches
	for name, (suggested, real) in missed.iteritems():
		print "%s\t%s\t%s" % (name, suggested, real)
	
	measures = eval_stats(results)
