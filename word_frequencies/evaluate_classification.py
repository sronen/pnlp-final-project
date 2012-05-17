import nltk
import wiki_frequency
import str_corpus_cleaner, pos_corpus_cleaner
import time
import codecs

STR_CORPUS_ROOT = '../datasets/cleaned_featured_bios/_filtered_3_plus/'
POS_CORPUS_ROOT = '../datasets/cleaned_featured_bios/_pos_clean_/'

def str_corpus_eval(articles_to_classify):
	# Initialize a plain-text corpus 
	training_corpus = nltk.corpus.PlaintextCorpusReader( \
		STR_CORPUS_ROOT, '.*\.txt')
	
	# Calculate TF*IDF for each category and IDF for the entrie corpus
	tfidfs_per_doc, idfs = wiki_frequency.calculate_corpus_tf_idf(training_corpus)
	#print_top_terms(tfidfs_per_doc)
	
	print "STR"
	st_time = time.time()
	
	for article_path in articles_to_classify:
		# Initialize new article
		ar_text = codecs.open(article_path, 'rU').read()
		article_words = str_corpus_cleaner.get_clean_terms(ar_text)	
		match, all_scores = wiki_frequency.classify_article_tfidf(article_words, tfidfs_per_doc, idfs)
		print "%s\t%s\t(%.3e)\ttime: %.3f sec" % \
			( article_path.split('/')[-1].replace('.txt',''), \
			match[0].split('.')[0], match[1], time.time()-st_time )
	
	
def pos_corpus_eval(articles_to_classify):
	# Use a POS-tagged corpus
	training_corpus = nltk.corpus.TaggedCorpusReader( \
		POS_CORPUS_ROOT, '.*\.pos.clean' )
	
	# Calculate TF*IDF for each category and IDF for the entrie corpus
	tfidfs_per_doc, idfs = wiki_frequency.calculate_corpus_tf_idf(training_corpus)
	
	print "POS"
	st_time = time.time()
	
	for article_path in articles_to_classify:
		ar_text = codecs.open(article_path, 'rU').read()
		article_tagged = nltk.pos_tag(nltk.wordpunct_tokenize(ar_text))
		article_taggged_clean = pos_corpus_cleaner.clean_pos(article_tagged)
		article_words = [word for (word,pos) in article_taggged_clean]
		match, all_scores = wiki_frequency.classify_article_tfidf(article_words, tfidfs_per_doc, idfs)
		print "%s\t%s\t(%.3e)\ttime: %.3f sec" % \
			( article_path.split('/')[-1].replace('.txt',''), \
			match[0].split('.')[0], match[1], time.time()-st_time )


if __name__ == "__main__":	
	root_path =\
	'/Users/shahar/Documents/MIT/Classes/MASS60-PracticalNLP/Project/pnlp-final-project/datasets'
	
	articles = ['cleaned_featured_bios/Media biographies/Cillian_Murphy.txt',
	'cleaned_featured_bios/Music biographies/AC_DC.txt',
	'cleaned_featured_bios/Literature and theatre biographies/Anton_Chekhov.txt',
	'cleaned_featured_bios/Sport and recreation biographies/Tim_Duncan.txt',
	'non_featured_bios/Tiger_Woods.txt',
	'non_featured_bios/Karl_Marx.txt',
	'non_featured_bios/Agatha_Christie.txt',
	'non_featured_bios/Toni_Blair.txt',
	'non_featured_bios/Napoleon.txt',
	'non_featured_bios/O._J._Simpson.txt']
	
	paths_to_classify = [root_path+"/"+article for article in articles]
	
	str_corpus_eval(paths_to_classify)
	print "\n"
	pos_corpus_eval(paths_to_classify)
	