import math
from collections import Counter, defaultdict


def tf(words_in_document):
	'''
	Return Term Frequency (TF) for each term in the document. TF is number of
	appearances divided by total number of words in the document. 
	A document can be a single article or all articles in a folder.
	-Input: a list of words in the document
	-Return: a Counter with keys=terms and values=frequencies
	'''
	term_count = Counter(words_in_document)
	total_words = float(len(words_in_document))
	
	tfs = {term:(freq/total_words) for (term,freq) in term_count.iteritems()}
	
	return tfs


def idf(tfs_per_document):
	'''
	Inverse Document Frequency: return the number of documents in which each
	term appears.
	-Input: a dictionary containing for each document in the corpus a
	 dictionary of term frequncies.
	-Return: a Counter with keys=terms and values=# of documents in corpus;
	 a Counter stating for each term number of docs in the corpus featuring it
	'''
	# Calculate TF for the entire corpus
	num_docs_per_term = Counter()
	for document, tfs in tfs_per_document.iteritems():
		for term in tfs.keys():
			num_docs_per_term[term] += 1
	
	# Calculate the IDF
	idfs = {}
	total_documents = len(tfs_per_document)
	for term, docs_featuring_term in num_docs_per_term.iteritems():
		idfs[term] = math.log(total_documents / (1.0 + docs_featuring_term) )
	
	return idfs


def tf_idf(tfs, idfs, documents_in_corpus):
	'''
	Calculate the TF*IDF weight given the TF of a document and the IDF of the
	entire corpus. Can be used for a document in the corpus or outside the 
	corpus.
	-Input: (1) TF dictionary for a document (2) IDF dictionary for the entire
	 corpus (3) Number of documents in corpus (to calculate IDF for terms in
	 the document that are not in the corpus (see below)
	-Return: a dictionary whose keys=term and values=TF-IDF scores for terms.
	'''
	tfidfs = defaultdict(float)
	
	for term, freq in tfs.iteritems():
		try:
			tfidfs[term] = freq * idfs[term]
		except KeyError:
			# Term doesn't appear in the corpus: can happen when compraing
			# an external document to an existing corpus. In this case, the
			# IDF would be log( # of documents in corpus), see
			# http://en.wikipedia.org/wiki/Tf-idf#Mathematical_details
			tfidfs[term] = math.log(documents_in_corpus)
			print "Term not in corpus: %s" % term
		
	return tfidfs