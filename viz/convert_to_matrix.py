# convert_to_matrix.py
import codecs
from collections import defaultdict
import csv, json

infile = "human-fr.txt"
outfile = "human-fr-matrix.txt"

fin = codecs.open(infile, "rU", encoding="utf-8")

# skip header
fin.readline()

#
#
# store topic composition for each article
topic_compos = defaultdict(defaultdict)

for i, line in enumerate(fin):
	vals1 = line.split('\t')
	person_name = vals1[0].replace("_", " ") # remove underscores while we're at it
	topics = vals1[1:]

	for topic_val in topics:
		topic_name, topic_share = topic_val.split(',')
		topic_compos[person_name][topic_name] = topic_share

# neat trick to print an orderly dictionary
#print json.dumps(topic_compos, indent=4)

#
#
# Now write the new file
fout = open(outfile, "w")

headers = topic_compos.itervalues().next().keys()
headers.insert(0, "Name")

dw = csv.DictWriter(fout, delimiter='\t', 
	fieldnames=headers ) # get first item in dictionary
dw.writeheader()

for person_name, compo in topic_compos.iteritems():
	# Two decimal digits is enough
	compo = { topic_name: round(float(topic_share), 2) for topic_name, topic_share in compo.iteritems() }
	#compo = { topic_name: "{0:.2f}".format(float(topic_share)) for topic_name, topic_share in compo.iteritems() }
	# add the header
	compo['Name'] = person_name.encode('utf-8')
	dw.writerow(compo)

