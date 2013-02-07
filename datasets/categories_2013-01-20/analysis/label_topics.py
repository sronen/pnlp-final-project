import csv
from collections import defaultdict

# ignore topics starting with X_
IGNORE_PREFIX = "X_"
CATEGORIES = ["Art", "Business_and_economics", "Exploration", "Law_and_crime", "Life", "Literature", "Music", "Politics", "Popular_culture", "Science_and_technology", "Sports", "TV_and_film", "War_and_military"]
ARTICLE_NAME_COL_HEADER = "ARTICLE_NAME"


def read_conversion_table(convertfile):
	# Create from given file a conversion table of topic ID to topic names.
	# The input file should be tab-delimited and contain the header
	# "Topic_Id\tPrimary\tSecondary"

	fin = open(convertfile, "rU")

	dictin = csv.DictReader(fin, delimiter="\t", )

	conversion_dict = {}
	for row in dictin:
		conversion_dict[row['Topic_Id']] = row['Primary']

	fin.close()
	return conversion_dict


def get_final_topics(infile, outfile, convertfile, langcode):
	conv_dict = read_conversion_table(convertfile)
	print conv_dict

	# Prep to read
	fin = open(infile, "rU")
	fin.readline() # skip header

	# Prep to write
	fout = open(outfile, "w")
	hdrs = [ARTICLE_NAME_COL_HEADER]
	hdrs.extend(CATEGORIES)
	dw = csv.DictWriter(fout, delimiter="\t", fieldnames=hdrs)
	dw.writeheader()

	for line in fin:
		line_vals = line.rstrip().split(' ')
		article_id = line_vals[0]
		article_name = line_vals[1].replace(
			langcode + '/5kb_train_test_split/5kbtest/', '').replace(
			'.txt', '').replace('_', ' ')
		
		# Create a dictionary from topic list: use even items as keys and odd as values.
		topic_shares_dict = dict( zip(line_vals[2::2], [ float(x) for x in line_vals[3::2] ]) )

		# Create a new dictionary with topic names converted from topic IDs, and discard
		# topics that start with IGNORE_PREFIX
		topic_names_shares_dict = defaultdict()

		for topic_id, topic_share in topic_shares_dict.iteritems():
			topic_name = conv_dict[topic_id] # convert id to name
			if not topic_name.startswith(IGNORE_PREFIX):
				# Name is "legit"
				if topic_names_shares_dict.has_key(topic_name):
					# Add to existing value
					topic_names_shares_dict[topic_name] += topic_share
				else:
					# Create new key with value
					topic_names_shares_dict[topic_name] = topic_share
				
		# Add title column and write to file 
		topic_names_shares_dict[ARTICLE_NAME_COL_HEADER] = article_name 
		dw.writerow(topic_names_shares_dict)

	fin.close()

	print article_id, article_name
	for k, v in topic_shares_dict.iteritems():
		print "%s\t%s" % (k, v)
	print
	for k, v in topic_names_shares_dict.iteritems():
		print "%s\t%s" % (k, v)


if __name__ == "__main__":
	get_final_topics("en-test-doc-topic-proportions.txt",
		"outfile_en.txt", "en_topic_conversion.txt", "en")
	get_final_topics("es-test-doc-topic-proportions.txt",
		"outfile_es.txt", "es_topic_conversion.txt", "es")
