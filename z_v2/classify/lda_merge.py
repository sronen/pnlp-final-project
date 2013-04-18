import sys
import nltk
from nltk import FreqDist
import numpy as np
import math

class TopicFdists:
	def __init__(self):
		self.fdists = dict() # topic number -> fdist of word indexes

	def inc(self, topic, word_index):
		if topic not in self.fdists.keys():
			self.fdists[topic] = FreqDist()
		self.fdists[topic].inc(word_index)

def get_topic_fdists(lda_results_filename, word_indexes=dict(), word_table=dict(),max_word_index=-1):
	"""return the frequency arrays for words in each topic"""
	f = open(lda_results_filename, 'r')

	topic_fdists = TopicFdists()

	# word_indexes = dict() # map from word id to word
	# max_word_index = -1
	first_run = (len(word_indexes.keys()) == 0)

	# map from word_indexes to set of documents it appeared in
	# doc_appearances = dict()

	for line in f.readlines():
		if line[0] == '#':
			continue
		data_list = line.split()
		assert(len(data_list) == 6)

		word = data_list[4]

		if first_run:
			word_index = (int)(data_list[3]) # unique
			word_table[word] = word_index
			word_indexes[word_index] = word
			if word_index > max_word_index:
				max_word_index = word_index
		else:
			if word in word_table:
				word_index = word_table[word]
			else: # new word
				max_word_index += 1
				word_index = max_word_index
				word_indexes[word_index] = word
				word_table[word] = word_index

		"""for cosdist, (i,j) in cosdists:"""
		#new_topics.merge(i,j)
		topic = (int)(data_list[5])
		topic_fdists.inc(topic, word_index)

	# Now we've constructed an fdist for each topic, so let's compute the frequency vectors
	tf_arrays = dict()
	for topic, fdist in topic_fdists.fdists.items():
		tfs = np.ndarray(shape=(max_word_index+1), dtype=float)
		for index, word in word_indexes.items():
			tfs[index] = fdist[index]/float(fdist.N())
		tf_arrays[topic] = tfs
	return (tf_arrays, word_indexes, word_table, max_word_index)

def match_topics(lda_results_caps, lda_results_nocaps):
	"""match caps topics to nocaps topics. for every caps topic, compute the cosine similarity
	to each nocaps topic, and match it to the max (but we will list the max 3 here, so humans can resolve).
	if there are too many duplicates: we can resolve by hand or implement a maximum-matching alg.
	for now, we will resolve by hand."""

	# have to continue using same word_indexes list because otherwise the arrays won't match up
	# because each run of LDA has different numbers of total words (since different preprocessing)
	(caps_tf_arrays, word_indexes, word_table, max_word_index) = get_topic_fdists(lda_results_caps)
	(nocaps_tf_arrays, word_indexes, word_table, max_word_index) = get_topic_fdists(lda_results_nocaps, word_indexes, word_table, max_word_index)

	top_nocaps_matches = list() # each list entry will be the top 3 caps topics that match it
	for i in range(len(nocaps_tf_arrays.keys())):
		cosdists = list()
		for j in range(len(caps_tf_arrays.keys())):
			cosdist = cosine_distance(caps_tf_arrays[j], nocaps_tf_arrays[i])
			cosdists.append((cosdist, j))
		best3 = sorted(cosdists, reverse=True)[:3]
		print (i, best3)
		top_nocaps_matches.append(best3)
	return top_nocaps_matches


def collapse_topics(lda_results_filename):
	"""for a single LDA run, collapse a large number of topics into a smaller one by similarity"""
	tf_arrays = get_topic_fdists(lda_results_filename)

	# compute cosine distances
	cosdists = list()
	for i in range(len(tf_arrays.keys())):
		for j in range(i+1,len(tf_arrays.keys())):
			cosdist = cosine_distance(tf_arrays[i], tf_arrays[j])
			cosdists.append((cosdist, (i,j)))

	new_topics = NewTopics(cosdists)
	print new_topics

def print_cosdists(cosdists):
	for cosdist, (i,j) in cosdists:
		print 'Topics ' + str(i) + ' and ' + str(j) + ': ' + str(cosdist)

class NewTopics:
	def __init__(self, cosdists):
		self.next_topic = 0
		self.new_to_old = dict()
		self.old_to_new = dict()

		cosdists.sort(reverse=True)
		for cosdist, (i,j) in cosdists:
			if cosdist < .1:
				break
			self.merge(i,j)

	def merge(self, i, j): # params: old topics i, j
		if i in self.old_to_new.keys():
			if j not in self.old_to_new.keys():
				self.old_to_new[j] = self.old_to_new[i]
				self.new_to_old[self.old_to_new[i]].add(j)
		elif j in self.old_to_new.keys():
			if i not in self.old_to_new.keys():
				self.old_to_new[i] = self.old_to_new[j]
				self.new_to_old[self.old_to_new[j]].add(i)
		else:
			self.new_to_old[self.next_topic] = set([i,j])
			self.old_to_new[i] = self.next_topic
			self.old_to_new[j] = self.next_topic
			self.next_topic += 1

	def __str__(self):
		ret = ""
		ret += 'Merged Topics\n'
		for topic, old_topics in self.new_to_old.items():
			ret += str(old_topics) + '\n'
		return ret


def cosine_distance(u, v):
	return np.dot(u, v) / (math.sqrt(np.dot(u, u)) * math.sqrt(np.dot(v,v)))



if __name__ == '__main__':
	if len(sys.argv) > 2:
		print match_topics(sys.argv[1], sys.argv[2])
	elif len(sys.argv) > 1:
		collapse_topics(sys.argv[1])
	else:
		# collapse_topics('datasets/mallet/30/wiki_bios_lemm_30')
		print """Usage: need to pass the lda results file as an argument. To match topics 
				from two lda runs, pass the caps file first, then the nocaps file second."""

		"""python lda_merge.py 'wikipedia_classification/en_wiki_output/wiki_lem_caps_output/wiki_lem_caps_50/wiki_lem_caps_50' 'wikipedia_classification/en_wiki_output/wiki_lem_no_caps_output/wiki_lem_no_caps_50/wiki_lem_no_caps_50'"""