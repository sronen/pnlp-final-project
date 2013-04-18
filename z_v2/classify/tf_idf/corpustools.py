'''
An easier to follow and easier to use version of HW1,
to be used for HW2.
'''

import sys
import nltk
from nltk.probability import MLEProbDist
from nltk.probability import WittenBellProbDist
from nltk.probability import FreqDist
from nltk.corpus import brown
from nltk.corpus import PlaintextCorpusReader
from collections import defaultdict
from math import log
from markov_start import *
import os

WORDS_IN_ENGLISH = 230000
# Based on:
# http://oxforddictionaries.com/words/how-many-words-are-there-in-the-english-language


def corpus_from_files(filenames):
	# Make a corpus of text that's not built into NLTK.
	corpus_root = "./"
	corpus_reader = PlaintextCorpusReader(corpus_root, filenames)
	return nltk.Text(corpus_reader.words())


def corpus_from_directory(path, filetype='.*'):
	'''
	Make a corpus of all files in a given directory. Can limit type by passing
	the desired extension, proper format is, e.g., '.*\.txt'
	'''
	corpus_reader = PlaintextCorpusReader(path, filetype)
	return nltk.Text( corpus_reader.words() )


def unigram_prob_dist(corpus):
	'''
	Compute unigram probability distributions from given corpus.
	WittenBell provides smoothing compared to no. of words in English,
	preventing probabilities of zero.
	'''
	freqs = corpus.vocab()
	probs = WittenBellProbDist(freqs, WORDS_IN_ENGLISH)
	
	return probs


def prob_ratios(probs1, probs2, top_tokens=50):
	'''
	Compute the ratios of probability distributions probs1 and prob2,
	and return the top_tokens highest ratios between them.
	'''
	# for each word, ratio to brown, then select top 50
	prob_ratio = defaultdict(float)
	
	# prepare the probability ratio dictionary
	for token in probs1.samples():
		p1 = probs1.prob(token)
		p2 = probs2.prob(token) # returns 0.0 if not found
		prob_ratio[token] = p1 / p2
		
	# Pick the top_tokens highest ratios
	return [ (x,prob_ratio[x]) for x in \
		sorted(prob_ratio, key=prob_ratio.get,reverse=True)[:top_tokens] ]


def bigram_pointwise_mutual_info(corpus, top_tokens=50):
	'''
	Build a probability distribution for bigrams of words in your corpus, 
	and return the top top_tokens bigrams with the most pointwise mutual information compared 
	to the unigrams in the corpus.
	'''

	def pmi(p_w1w2, p_w1, p_w2 ):
		# Calculate pointwise mutual information for given probabilities
		return log( p_w1w2/(p_w1*p_w2) )
	
	# Calculate probability of unigrams
	probs_unigrams = unigram_prob_dist(corpus)
	
	# Calculate probability of bigrams
	bigrams = nltk.bigrams(corpus.tokens)
	freq_bigrams = FreqDist(bigrams)
	prob_bigrams = nltk.MLEProbDist(freq_bigrams)
	
	# Calculate PMI for all bigrams
	pmis = defaultdict(float)
	for bigram in bigrams:
		pmis[bigram] = pmi( prob_bigrams.prob(bigram), \
			probs_unigrams.prob(bigram[0]), probs_unigrams.prob(bigram[1]) )
	
	# Pick the top_tokens higest PMIs
	return [ (x,pmis[x]) for x in \
		sorted(pmis, key=pmis.get,reverse=True)[:top_tokens] ]


def generate_text(corpus, words_to_generate, num_words_to_remember=5):
	'''
	Compute probability distributions for each Markov state of the previous n
	words, and use it to generate text from your corpus.
	'''
	# probabilty distribution for ngrams of length=num_words_to_remember  
	probs = make_probs(corpus, num_words_to_remember+1) 
	
	# Start: generate "last words list" with no prior knowledge 
	last_n_words = probs[None].generate() 
	# Start the text with these words
	generated_text = list(last_n_words)
	
	for i in xrange(words_to_generate-num_words_to_remember):
		# Generate next word based on last n words
		try:
			# make_probs() may miss the last word tuple: it doesn't expect
			# to be called with +1 to the number of n-grams, but that's the
			# only way to get it to work with n=1. This exception block
			# handles this gracelfully by returning the text already generated
			# and moving on to the next n-length.
			new_word = probs[last_n_words].generate()
			# Add new word to text
			generated_text.append(new_word)
		
			if num_words_to_remember>1:
				temp_list = list(last_n_words[1:]) # remove oldest word
				temp_list.append(new_word) # add new word
				last_n_words = tuple(temp_list) # make it a tuple
			else:
				# No window to slide: replace the word and don't bother 
				last_n_words = (new_word,)
		except KeyError:
			print ">>> Exception:", i, last_n_words, new_word
			break
	return ' '.join(generated_text) # 


if __name__ == "__main__":
	# try 'plutarch-lives-sulla.txt' or 'dino_text.txt'
	textfilename = sys.argv[1]
	if textfilename==None:
		print "Usage: python corpustools.py <text file to use as corpus>"
		exit()
	
	# Create the new corpus and compute prob. dist.
	new_corpus = corpus_from_textfile(textfilename)
	print "created corpus from", textfilename, ":", new_corpus
	new_prob = unigram_prob_dist(new_corpus)
	
	# Intialize the Brown corpus and compute prob. dist.
	brn_corpus = nltk.Text( brown.words() )
	brn_prob = unigram_prob_dist(brn_corpus)
	
	# Get top 50 probablity ratios for the corpora 
	prob_ratios_50 = prob_ratios(new_prob, brn_prob, top_tokens=50)
	print "Top 50 ratios (New corpus to Brown):", prob_ratios_50
	
	# Find the top 50 bigrams with the most pointwise mutual information
	# compared to the unigrams in your corpus. Note we use CorpusReader!
	pmis_50 = bigram_pointwise_mutual_info(new_corpus, top_tokens=50)
	print "Top 50 PMIs in new corpus", pmis_50
	
	# Generate some random text based on probability distribution of corpus
	# Show examples for n-grams with n=1 through 5.
	print
	for ngram_length in xrange(1,6):
		# We use n+1 because a lookup of previous n words means we're using a model of n+1 
		print ">>> Generated text (n=", ngram_length, "):"
		print generate_text(new_corpus, words_to_generate=150, num_words_to_remember=ngram_length), "\n"