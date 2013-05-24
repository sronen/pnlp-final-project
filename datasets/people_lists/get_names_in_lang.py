
# Get names of people from DBPedia instance_type dumps.
# The dumps are assumed to be in the same folder as this script.

import codecs

LANGS_TO_GET = ["en", "it", "es", "pt"]

INFILE_TEMPLATE = "instance_types_%s.ttl"
OUTFILE_TEMPLATE = "list_of_%s.txt"

PERSON_TYPE = "<http://xmlns.com/foaf/0.1/Person>"
DBPEDIA_PREFIX_ENG = "<http://dbpedia.org/resource/"
DBPEDIA_PREFIX_OTHER = "<http://%s.dbpedia.org/resource/"
#TO_REPLACE = "<http://www.w3.org/1999/02/22-rdf-syntax-ns#type> %s ." % PERSON_TYPE


def get_people_names(lang):

	fin = codecs.open(INFILE_TEMPLATE % lang, "rU")
	fout = codecs.open(OUTFILE_TEMPLATE % lang, "w")

	num_lines_in = 0
	num_ppl_in = 0
	num_ppl_out = 0

	for line in fin:
		# look for type in line.
		if line.find(PERSON_TYPE) != -1:
			# If found, get just the name

			line_name = line.split()[0] # name is the first part
			
			if line_name.find("__") == -1: # remove entries with __: these note photos, etc.
				if lang!="en":
					person_name = line_name.replace(DBPEDIA_PREFIX_OTHER % (lang), "")
				else:
					person_name = line_name.replace(DBPEDIA_PREFIX_ENG, "")
				person_name = person_name.replace(">", "")
				fout.write(person_name + "\n")
				num_ppl_out += 1	# How many people we wrote down

			num_ppl_in += 1 # How many people we found

		
		num_lines_in += 1 # How many lines total	

	print("lang: %s\t\tLINES_IN: %s\t\tPPL_IN: %s\t\tPPL_OUT: %s" % (lang, num_lines_in, num_ppl_in, num_ppl_out))

	fout.close()
	fin.close()

if __name__ == "__main__":

	for lng in LANGS_TO_GET:
		get_people_names(lng)
