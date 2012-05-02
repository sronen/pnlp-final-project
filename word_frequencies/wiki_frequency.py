import os, sys, inspect
cmd_folder = os.path.abspath(os.path.split(inspect.getfile(inspect.currentframe() ))[0])
if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)

import nltk
from nltk.corpus import brown
import corpustools as ct
from nltk.corpus import stopwords
import chunk_wikipedia_modified as chunk_wiki

if __name__ == "__main__":
	
	try:
		path = sys.argv[1]
	except IndexError:
		print "Usage: python corpustools.py <file or folder to load files from into corpus>"
		exit()
	
	#
	#
	# Create the new corpus (assume files are already clean)
	new_corpus_reader = ct.corpus_from_directory(path)
	new_corpus = nltk.Text( new_corpus_reader.words() )
	print "created corpus from", path, ":", new_corpus
	
	#
	#
	# Tag POS and remove proper nouns
	# TODO: takes a long time, add progress bar + improve performance
	print "tagging sentences"
	tagged_sents = map(lambda x:nltk.pos_tag(x), new_corpus_reader.sents()) 

	# pos to remove: cardinal numbers, punctuation, and proper nouns
	POS_TO_REMOVE = ["-",".", ",", "?", "!",":",";", "(", ")", "\"", "\'", "NNP", "NNPS", "CD"]
	
	# get the words to remove -- Maybe there's a nicer way to implment this
	blacklisted_words = set()
	for sent in tagged_sents:
		new_blacklisted = [word for (word,pos) in sent if pos in POS_TO_REMOVE or word in stopwords.words('english')]
		blacklisted_words.update(new_blacklisted)
	####
	
	# compute stuff
	print "computing probs etc."
	
	# compute prob. dist.
	new_prob = ct.unigram_prob_dist(new_corpus)
	
	# Intialize the Brown corpus and compute prob. dist.
	brn_corpus = nltk.Text( brown.words() )
	brn_prob = ct.unigram_prob_dist(brn_corpus)
	
	# Get top probablity ratios for the corpora, excluding blacklisted words
	prob_ratios_1000 = [(word, prob) for (word, prob) in ct.prob_ratios(new_prob, brn_prob, top_tokens=1000) if word not in blacklisted_words]
	#print "Top 50 ratios (New corpus to Brown):", prob_ratios_50
	
	# Find the top 50 bigrams with the most pointwise mutual information
	# compared to the unigrams in your corpus. Note we use CorpusReader!
	pmis_50 = ct.bigram_pointwise_mutual_info(new_corpus_reader, top_tokens=50)
	#print "Top 50 PMIs in new corpus", pmis_50
	
	"""""
	
	# Generate some random text based on probability distribution of corpus
	# Show examples for n-grams with n=1 through 5.
	print
	for ngram_length in xrange(1,6):
		# We use n+1 because a lookup of previous n words means we're using a model of n+1 
		print ">>> Generated text (n=", ngram_length, "):"
		print ct.generate_text(new_corpus, words_to_generate=150, num_words_to_remember=ngram_length), "\n"
	"""