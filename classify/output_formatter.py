import sys, re, string, time, os, pickle, urllib2

def make_tsv_output(topics_file, topic_names_file, output_file, num_topics=10):
	"""Read the mallet-formatted topics_file, and generate a tsv output_file."""
	# 1. Read topic_names_file to build an in-memory topic names map. topic_num->topic_name
	topic_names_f = open(topic_names_file, 'r')
	topic_names_dict = dict()
	for line in topic_names_f.readlines():
		if line[0] == '#':
			continue
		# Topics name file format:
		# topicnum topicname
		topic_num = line.split()[0]
		topic_name = ' '.join(line.split()[1:])
		topic_names_dict[topic_num] = topic_name

	# 2. Read topics_file line by line, and generate the corresponding line in output file
	output_f = open(output_file, 'w')

	# add top line
	output_text = 'Name'
	for i in range(num_topics):
		output+text += '\t' + topic_names_dict[i]
	output_text += '\n'
	topics_f = open(topics_file, 'r')

	# add data lines
	for line in topics_f.readlines():
		if line[0] == '#':
			continue
		# Topics file format:
		# doc fullpath topicnum1 proportion1 topicnum2 proportion2...
		topic_props_dict = dict() # topic_num->topic_prop
		line_split = line.split()
		for i in range(min(len(line_split), 2+(2*num_topics))):
			if i == 0:
				continue
			elif i == 1:
				article_name = os.path.split(line_split[i])[1]
				output_text += article_name
			elif i % 2 == 0:
				pass
				#topic_name = topic_names_dict[line_split[i]]
			elif i % 2 == 1:
				topic_props_dict[line_split[i-1]] = line_split[i]
				#output_text += '\t' + topic_name + ',' + line_split[i]

		# print topic_props_dict
		for i in range(num_topics):
			output_text += topic_props_dict[i] + '\t'
		output_text += '\n'
	output_f.write(output_text)

if __name__ == '__main__':
	if len(sys.argv) > 3:
		num_topics = 10
		topics_file = sys.argv[1]
		topic_names_file = sys.argv[2]
		output_file = sys.argv[3]

		if len(sys.argv) > 4:
			num_topics = sys.argv[4]
		make_tsv_output(topics_file, topic_names_file, output_file, num_topics)
	else:
		print 'usage: make_tsv_output.py topics_file_path \
			   topic_names_file_path output_file_path num_topics'
