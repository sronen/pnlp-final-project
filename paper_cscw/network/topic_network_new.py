'''
Generate a table showing average topic composition by category, as a matrix category X topic.
The category of an article is determined by the topic that has the largest share.  

- "Other" category is removed.
- A file named "category_count_x.txt" with the number of articles and their share is written as well.


'''
import csv
from itertools import izip
from collections import defaultdict
import json # for pretty printing

AVERAGE = True # output average topic composition (instead of total)
ARTICLE_NAME_HEADER = "ARTICLE_NAME"


def convert_to_network_formats(langcode):
	infile = '../../datasets/topic-names-final/%s-topic-names-50-final-fixed.txt' % langcode
	net_matrix_outfile = '%s_network_matrix_no_other.txt' % langcode # adjacency matrix
	net_edgelist_outfile = '%s_network_edgelist_no_other.txt' % langcode # for CytoScape
	cat_outfile = '%s_category_count.txt' % langcode


	fin = open(infile, "rU")
	dr = csv.DictReader(fin, delimiter="\t")

	# Init adjancy matrix of max_topics X topics, implemented through a nested dictionary
	# Note that ARTICLE_NAME_HEADER is remvoed
	topic_edgelist = { topic: {topic: 0.0 for topic in dr.fieldnames if topic!=ARTICLE_NAME_HEADER} 
						for topic in dr.fieldnames if topic!=ARTICLE_NAME_HEADER}
	# count number of articles in category for normalizing later
	category_count = { topic : 0 for topic in topic_edgelist.keys() }

	print "***%s***" % langcode

	for row in dr:
		try:
			article_name = row.pop(ARTICLE_NAME_HEADER) # remove this non-numeric field
		except KeyError:
			print row
			(exit)
		#print article_name
		try:
			article_topic_compo = {name : float(share) if share!='' else float(0) for name, share in row.iteritems()}
		except ValueError:
			print row
			exit()
		#print "bal:", article_topic_compo

		### TODO: get top three topics, connect top topic to the other two.
		#max_topics = dict(sorted(article_topic_compo.iteritems(),
		# key=operator.itemgetter(1), reverse=True)[:3])

		# Find the topic with the maximum share. We use it as article category.
		max_topic = max(article_topic_compo, key=article_topic_compo.get) # get key of max topic 
		#print "max_topic:", max_topic # debug
		category_count[max_topic] += 1 # increment respective counter

		# Add directed, weighted links from category to other topics in this article. Weight is the share of each topic
		for topic_name, topic_share in article_topic_compo.iteritems():
			if topic_name!="Other":
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
		if category_name=="Other":
			continue
		topics.pop('Other')
		# Create a matrix row by adding the category name to its topic shares
		topic_matrix_row['Category'] = category_name
		topic_matrix_row.update(topics)
		dw.writerow(topic_matrix_row)

	fout.close()

	# Write category matrix to edgelist
	fout = open(net_edgelist_outfile, "w")
	fout.write("src\ttgt\tweight.{0}\n".format(langcode))
	for category_name, topics in topic_edgelist.iteritems():
		if category_name=="Other":
			# skip other
			continue
		for topic_name, topic_share in topics.iteritems():
			if topic_name!="Other":
				# skip othe
				# src-tgt-weight
				fout.write("%s\t%s\t%s\n" % (category_name, topic_name, topic_share))
	fout.close()

	# Write category counts and percentages to file
	total_num_articles = sum(category_count.values())
	fout = open(cat_outfile, "w")
	fout.write("category\tnum.articles.{0}\tpercent.articles.{0}\n".format(langcode))
	for category_name, count in category_count.iteritems():
		fout.write("{0}\t{1}\t{2}\n".format(category_name, count, count / float(total_num_articles) * 100) ) 
	fout.write("TOTAL\t{0}".format(total_num_articles))

	fout.close()


if __name__ == "__main__":
	for langcode in ["en", "es", "it", "pt"]:
		convert_to_network_formats(langcode)
