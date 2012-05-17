import os, codecs
import operator
import corpustools as ct
import nltk
from nltk.corpus import stopwords

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


if __name__ == "__main__":
	# Tag all documents in the folders under root_path. Store tags for each
	# folder in a file of their own, with a .pos extension. Takes about 1:20
	# hours to tag the Featured Articles corpus
	
	# tag_wiki_corpus(root_path)
	# clean_tag_wiki_corpus(root_path+'_pos_/')
	pass