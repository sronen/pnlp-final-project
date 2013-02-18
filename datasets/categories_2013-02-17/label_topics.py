import csv, os
from collections import defaultdict

IGNORE_PREFIX = "[" # topics starting with this character will be ignored
ARTICLE_NAME_COL_HEADER = "ARTICLE_NAME"

# List of approved categories:
CATEGRORY_LIST = [
	"Art", 
	"Business", 
	"Education", 
	"Explorers", 
	"Humanities", 
	"Law", 
	"Literature", 
	"Media", 
	"Music", 
	"Personal", 
	"Politics", 
	"Religion", 
	"Royalty", 
	"Science", 
	"Sports", 
	"Warfare",
	"Other"] # category for unlabeled topics


def read_conversion_table(convertfile, verify_cat=True):
	'''
	Create from given file a conversion table of topic ID to topic names.
	The input file should be tab-delimited without a header, 
	whose first column is topic ID and the second is tha assigned topic name.
	If vertify_cat=True, will throw exception an halt if a category is
	not in the list of approved categories.
	'''
	fin = open(convertfile, "rU")

	conversion_dict = {}
	for line in fin:
		topic_id, topic_name = line.strip().split('\t')
		
		if topic_name.startswith(IGNORE_PREFIX):
			topic_name = "Other"

		if (verify_cat==True):
			# Check if in list of approved categories
			if topic_name not in CATEGRORY_LIST:
				print ">>> ERROR: mapping file %s has unapproved category %s, check list" % \
					(convertfile, topic_name)
				exit()
		conversion_dict[topic_id] = topic_name

	fin.close()
	return conversion_dict


def get_final_topics(infile, convertfile, outfile):#, langcode):
	'''
	Given a topic proportions files and and mapping of topic numbers to names
	for the file, create a matrix of article X labeled topics, showing the topic_share
	of each labeled topic. 
	'''

	conv_dict = read_conversion_table(convertfile)
	# print conv_dict

	# Prep to read
	fin = open(infile, "rU")
	fin.readline() # skip header

	# Prep to write
	fout = open(outfile, "w")
	hdrs = [ARTICLE_NAME_COL_HEADER]
	hdrs.extend(CATEGRORY_LIST)
	dw = csv.DictWriter(fout, delimiter="\t", fieldnames=hdrs)
	dw.writeheader()

	for line in fin:
		line_vals = line.rstrip().split(' ')
		article_id = line_vals[0]
		# Get the file name without the extension
		article_name = \
			os.path.basename(line_vals[1]).replace('.txt','').replace('_', ' ')
		
		# Create a dictionary from topic list: use even items as keys and odd as values.
		topic_shares_dict = dict( zip(line_vals[2::2], [ float(x) for x in line_vals[3::2] ]) )

		# Convert topic numbers to IDs, merging categories if necessary
		topic_names_shares_dict = defaultdict(float)
		for topic_id, topic_share in topic_shares_dict.iteritems():
			topic_name = conv_dict[topic_id] # convert id to name			
			topic_names_shares_dict[topic_name] += topic_share
				
		# Add title column and write to file 
		topic_names_shares_dict[ARTICLE_NAME_COL_HEADER] = article_name 
		dw.writerow(topic_names_shares_dict)

	fin.close()

	# Debug
	#print article_id, article_name
	#for k, v in topic_shares_dict.iteritems():
	#	print "%s\t%s" % (k, v)
	#print
	#for k, v in topic_names_shares_dict.iteritems():
	#	print "%s\t%s" % (k, v)


if __name__ == "__main__":
	FILE_NUMBERS = [10, 11, 12, 20, 21, 22, 30, 31, 32]
	#LANGCODES = ['en', 'es']
	LANGCODES = ['es']

	TOPIC_FILENAME = "%s-topic-prop/%s-%s-topic-prop.txt"
	MAP_FILENAME = "%s-topic-names/%s-%s-topic-names.txt"
	OUTPUT_FILENAME = "%s-topic-prop-names/%s-%s-topic-prop-names.txt"
	OUTPUT_DIR = "%s-topic-prop-names/"

	for lang in LANGCODES:
		if not os.path.exists(OUTPUT_DIR % lang):
			os.makedirs(OUTPUT_DIR % lang) # store the output files here

		for num in FILE_NUMBERS:
			get_final_topics(TOPIC_FILENAME % (lang, lang, num), \
							 MAP_FILENAME % (lang, lang, num), \
							 OUTPUT_FILENAME % (lang, lang, num) )
			print "Converted iteration %s-%s" % (lang, num)
