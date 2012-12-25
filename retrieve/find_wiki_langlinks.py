# -*- coding: utf-8 -*-

'''
Module for finding all Wikipedia language editions for a given article in English.
Hacky adaptation of a script I wrote to augment Freebase's person.tsv file with English
Wikipedia pageid and name for each person listed.

Input files available under datasets/wikipedia_bios_lists. Results are also stored there.
NOTE: script must be run from same folder as data and wiki_article_meta.py.

TODO: results needs to be merged later using the shell script merge_files.sh,
or simply: 
cat person*_matched.tsv | grep -v "date_of_birth" > all_person_matched.tsv
("date_of_birth" used to identify the headers if these exist, grep -v removes them)
'''

import os, sys          # Command-line arguments, etc.
import string, csv
import urllib, urllib2, simplejson
import time
from itertools import islice
from collections import defaultdict
import multiprocessing
import wiki_article_meta as wm
import codecs

SPLIT_SIZE = 10000000 # size for each file chunk, def. 20MB
ORIG_PERSON_TSV = "person_wiki.tsv" #
RESOLVED_PERSON_TSV = "person_langs.tsv"
# List of all IDs that returned an error.
# Not the best coding practice, but gets it done
ERROR_FILE = "person_error.txt"

MAX_WIKI_QUERIES = 50 # maximum number of IDs Wikipedia allows in a single query

 # use Wikipedia Edition language code, e.g., 'en' or 'de' 
WIKIPEDIA_EN_API_URL = 'http://en.wikipedia.org/w/api.php'


def _query_using_urllib(wiki_edition_api_url, params):
	'''
	Query implemented using urllib and simplejson 
	'''
	params['action'] = 'query'
	params['format'] = 'json' # ask for result in JSON format
	req = urllib2.Request(url=wiki_edition_api_url, data=urllib.urlencode(params))
	res = urllib2.urlopen(req)
	
	json_string = res.read()
	json_dic = simplejson.loads(json_string)
	
	return json_dic


def convert_person_tsv(infile, outfile, errorfile, chunk_number, header_row):
	# For each person in person.tsv, get his/her English Wiki ID and name.
	# Then output the ones on the English Wikipedia to a new file, along
	# With their Wiki name and Wiki ID.
	fin = open(infile, "rU")
	dr = csv.DictReader(fin, fieldnames=header_row, delimiter="\t")

	fout = open(outfile, "w")

	ferror = open(errorfile, "w")
	ferror.write("Names that returned errors:" + "\n")
	ferror.close()

	i = 0
	name_not_found = 0
	name_found = 0

	st_time = time.time()

	while True:
		# To speed queries, we read several lines from the file each time.
		# We get the Wikipedia names from these lines and query them all at once,
		# this reduces the number of slow API hits. 
		# MAX_WIKI_QUERIES is the maximum number of names Wikipedia
		# allows in one query
		next_n_lines = list(islice(dr, MAX_WIKI_QUERIES))

		if not next_n_lines:
			break

		if i % 1000 == 0:
			print "***** Chunk: %d Iteration %d: matched=%d not_matched=%d *****" % \
			(chunk_number, i, name_found, name_not_found )
			
		# store Wikipedia names read from curent chunk
		wiki_en_names = [row['wiki_name'].decode('utf-8') for row in next_n_lines]

		# Find names in all languages
		wiki_all_names = wm.find_articles_languages(wiki_en_names)
		
		# Write the chunk of rows to file 
		for english_name, lang_dic in wiki_all_names.iteritems():
			try:
				row_text = ""
				# Add Wikipedia article name to dict
				for lang, name_in_lang in lang_dic.iteritems():
				 	row_text += "%s,%s\t" % (lang, name_in_lang)

				# Now convert to a string and write it
				unicode_row = row_text.encode('utf-8')
				fout.write( unicode_row + "\n")
				name_found += 1
			except KeyError:
				# Errors are handled by wiki_article_meta, so this shouldn't happen
				print ">>> No English Wikipedia article for %s : %s" % (row['id'], row['name'])
				name_not_found += 1

			# counter
			i += 1

	print "***** Chunk: %d | total %d | matched %d | not matched %d" % \
		(chunk_number, i, name_found, name_not_found)
	ferror.close()
	fout.close()
		

def multiprocess_it(origfile):
	# read file
	forig = open(origfile, "rU")
	split_dir = "split_dir"

	# split to 20MB chunks
	
	i = 0

	# get header
	header_row = forig.readline()[:-1].split('\t')

	if not os.path.exists(split_dir):
		os.makedirs(split_dir)
	os.chdir(split_dir)

	while True: 
		print "iteration:", i

		chunked_lines = forig.readlines(SPLIT_SIZE)
		if not chunked_lines:
			break

		# Name all the new files
		chunkfile = os.path.splitext(origfile)[0] + str(i) + ".tsv"
		chunkmatchedfile = os.path.splitext(chunkfile)[0] + "_matched.tsv"
		chunkerrorfile = os.path.splitext(chunkfile)[0] + "_error.tsv"
		
		fchunk = open(chunkfile, "w")
		fchunk.writelines(chunked_lines)
		fchunk.close()
		
		# call a thread for each part
		print "thread", i 

		p = multiprocessing.Process(target=convert_person_tsv, \
			args=(chunkfile, chunkmatchedfile, chunkerrorfile, i, header_row))
		p.start()

		i+=1 
	
	forig.close()
	os.chdir("..") # level up
 

if __name__ == "__main__":
	# Multiprocess mode
	st_time = time.time()
	multiprocess_it(ORIG_PERSON_TSV)
	print "time: ", time.time() - st_time

	# Test single process
	#forig = open(ORIG_PERSON_TSV, "rU")
	#header_row = forig.readline()[:-1].split('\t')
	#convert_person_tsv(ORIG_PERSON_TSV, RESOLVED_PERSON_TSV, ERROR_FILE, 1, header_row=header_row)
	
