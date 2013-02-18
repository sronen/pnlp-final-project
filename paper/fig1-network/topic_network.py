'''
Generate a table showing average topic composition by category, as a matrix category X topic.
The of an article is determined by the topic that has the largest share.  
'''
import csv
from itertools import izip
from collections import defaultdict
import json # for pretty printing

AVERAGE = True # output average topic composition (instead of total)
ARTICLE_NAME = ""

infile = '../../datasets/categories_2013-02-17/es-topics-full.txt'
net_matrix_outfile = 'es_network_matrix.txt' # adjacency matrix
net_edgelist_outfile = 'es_network_edgelist.txt' # for CytoScape
cat_outfile = 'es_category_count.txt'

fin = open(infile, "rU")
dr = csv.DictReader(fin, delimiter="\t")

# Init adjancy matrix of max_topics X topics, implemented through a nested dictionary
# Note that ARTICLE_NAME is remvoed
topic_edgelist = { topic: {topic: 0.0 for topic in dr.fieldnames if topic!=ARTICLE_NAME} 
					for topic in dr.fieldnames if topic!=ARTICLE_NAME}
# count number of article in category for npomalizing later
category_count = { topic : 0 for topic in topic_edgelist.keys() }


for row in dr:
	article_name = row.pop('') # remove this non-numeric field
	#print article_name
	article_topic_compo = {name : float(share) for name, share in row.iteritems()}
	#print "bal:", article_topic_compo

	# Find the topic with the maximum share. We use it as article category.
	max_topic = max(article_topic_compo, key=article_topic_compo.get) # get key of max topic 
	#print "max_topic:", max_topic # debug
	category_count[max_topic] += 1 # increment respective counter

	# Add weighted links from category to other topics in this article. Weight is the share of each topic
	for topic_name, topic_share in article_topic_compo.iteritems():
		topic_edgelist[max_topic][topic_name] += float(topic_share)

fin.close()

# OUTPUT
#print(json.dumps(topic_edgelist, indent=4))

# Get average topic compo for category. Done by dividing the total shares 
# for each category with the number of articles in that category. TODO:
# currently smoothing zeros by adding a small value - consider a better way
if (AVERAGE==True):
	avg_topic_edgelist = defaultdict(defaultdict)

	for category_name, topics in topic_edgelist.iteritems():
		avg_topic_edgelist[category_name] = \
			{ name: (total_share / float(category_count[category_name]+1e-16)) 
			for name, total_share in topics.iteritems() }
	topic_edgelist = avg_topic_edgelist


# Write category matrix to file
fout = open(net_matrix_outfile, "w")
header_row = ['Category']
header_row.extend(topic_edgelist.keys())
dw = csv.DictWriter(fout, fieldnames=header_row , delimiter='\t')
dw.writeheader()

topic_matrix_row = {}
for category_name, topics in topic_edgelist.iteritems():
	# Create a matrix row by adding the category name to its topic shares
	topic_matrix_row['Category'] = category_name
	topic_matrix_row.update(topics)
	dw.writerow(topic_matrix_row)

fout.close()

# Write category matrix to edgelist
fout = open(net_edgelist_outfile, "w")
fout.write("src\ttgt\tweight\n")
for category_name, topics in topic_edgelist.iteritems():
	for topic_name, topic_share in topics.iteritems():
		# src-tgt-weight
		fout.write("%s\t%s\t%s\n" % (category_name, topic_name, topic_share))
fout.close()

# Write category counts to file
fout = open(cat_outfile, "w")
fout.write("Category\tNum_articles\n")
for category_name, count in category_count.iteritems():
	fout.write("%s\t%s\n" % (category_name, count) ) 
fout.write("TOTAL\t%s" % sum(category_count.values()))

fout.close()
