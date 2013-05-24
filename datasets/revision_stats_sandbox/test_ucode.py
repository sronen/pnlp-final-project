# -*- coding: utf-8 -*-

import codecs

#path = "eswiki-20130429-pages-logging.xml.gz"

def populate_list_of_persons(infile, outfile):
	fin = codecs.open(infile, "rU", encoding="utf-8")
	#fin = open(infile, "rU")
	
	fout = open(outfile, "w")

	persons = []

	for line in fin:
		name, clean_size = line.split(", ")
		#name = name.decode("utf-8")
		persons.append(name.replace("_", " "))
		print name.encode("utf-8")
		#fout.write(name.encode("utf-8") + "\n")
		fout.write(name.encode('utf-8') + "\n" if isinstance(name, unicode) else name + "\n")

	fout.close()

	return persons


if __name__ == "__main__":

	list_of_persons = populate_list_of_persons("2kb-sizes-pt-test.txt", "test.txt")