# coding: utf-8

'''
Module for finding the sizes for Wikipedia biographies in English and Spanish.
TODO: results needs to be merged later using the merge_and_delete_files.py;
Merging could also be done by this very script, but better synchronization
of processes will be necessary. 
'''

import os, sys	# Command-line arguments, etc.
import string, csv
import urllib, urllib2, simplejson
import time
from itertools import islice
from collections import defaultdict
import multiprocessing

BIO_LIST_FILE = "parallel_eng_spa_new_test.tsv"
SPLIT_SIZE = 10000 # size for each file chunk, def. 20MB

MAX_WIKI_QUERIES = 50 # maximum number of IDs Wikipedia allows in a single query

 # use Wikipedia Edition language code, e.g., 'en' or 'de' 
WIKIPEDIA_ENG_API_URL = 'http://en.wikipedia.org/w/api.php'
WIKIPEDIA_SPA_API_URL = 'http://es.wikipedia.org/w/api.php'
#ACTIVE_LANG_EDITION = WIKIPEDIA_ES_API_URL

def get_wiki_sizes(lang_edition, article_titles):
	'''
	Given a language edition and a list of Wikipedia pageids, returns a dictionary 
	of key=wpid (i.e., page id) and value=size of article. Also returns a list of 
	articles that weren't found.
	REST query: http://en.wikipedia.org/w/api.php?action=query&prop=revisions&titles=Jerry%20Seinfeld|Charles%20Darwin&rvprop=size&redirects=
	TODO: work with WPID: http://en.wikipedia.org/w/api.php?action=query&pageids=19162933|1326810&format=json
	'''

	# Get the wpids convert to a string to use as key 	
	titles_str = \
		"|".join([str(article_title) for article_title in article_titles])

	# Query Wikipedia for the names
	params = {'titles': titles_str, 'prop': 'revisions', 'rvprop': 'size'}
	results = _query_using_urllib(lang_edition, params)

	if not results:
		# not a single ID found, return empty dict
		return {}

	# print results
	wiki_sizes_dict = defaultdict(str)
	not_found_list = []

	for wpid, pageinfo in results['query']['pages'].iteritems():
		article_name = pageinfo['title']
		try:
			article_size =  pageinfo['revisions'][0]['size']
			wiki_sizes_dict[article_name.encode('utf-8')] = article_size
		except KeyError:
			print "\"%s\" not found in %s" % (article_name, lang_edition)
			not_found_list.append(article_name)
			wiki_sizes_dict[article_name.encode('utf-8')] = -1
			continue
	
	if (len(wiki_sizes_dict)==49 and lang_edition==WIKIPEDIA_ENG_API_URL):
		for wpid, pageinfo in results['query']['pages'].iteritems():
			print pageinfo['title'], pageinfo['revisions'][0]['size']
		print "****************"

		for title in article_titles:
			print title

	return wiki_sizes_dict, not_found_list


def _query_using_urllib(wiki_edition_api_url, params):
	'''
	Query implemented using urllib and simplejson 
	'''
	params['action'] = 'query'
	params['format'] = 'json' # ask for result in JSON format
	# params['redirects'] = '' # automatically resolve
	req = urllib2.Request(url=wiki_edition_api_url, data=urllib.urlencode(params))
	res = urllib2.urlopen(req)
	
	json_string = res.read()
	json_dic = simplejson.loads(json_string)
	
	return json_dic


def add_person_size_english_spanish(infile, outfile, errorfile, totalsfile, chunk_number, header_row):
	"""
	For each person listed, get the size of his/her wikipedia article
	in English and in Spanish, then output the name and size to a new file.
	infile is a tab-delimited file, with one column holding English names 
	and another holding Spanish names. The columns are titled "name_eng" and
	"name_spa", respectively. 
	"""
	fin = open(infile, "rU")
	dr = csv.DictReader(fin, fieldnames=header_row, delimiter="\t")

	out_headers = dr.fieldnames
	out_headers.extend(["wiki_size_eng", "wiki_size_spa"])

	fout = open(outfile, "w")
	dw = csv.DictWriter(fout, delimiter="\t", fieldnames=out_headers)
	dw.writeheader()

	ferror = open(errorfile, "w")
	ferror.write("titles that made the query fail:" + "\n")

	# Summary file
	ftotals = open(totalsfile, "w")
	ftotals.write("Chunk\tTotal\tok_eng\tbad_eng\tok_spa\tbad_spa\n")

	i = 0
	name_not_found_eng = name_not_found_spa = 0
	name_found_eng = name_found_spa = 0

	st_time = time.time()

	while True:
		# To speed queries, we read several lines from the file each time.
		# We get the FB IDs from these lines and query them all at once,
		# first on FB then on Wikipedia; this reduces the number of slow
		# API hits. MAX_WIKI_QUERIES is the maximum number of IDs Wikipedia
		# allows in one query
		next_n_lines = list(islice(dr, MAX_WIKI_QUERIES))
		
		if not next_n_lines:
			break

		if i % 1000 == 0:
			print "***** Chunk: %d Iteration %d matched_eng=%d not_matched_eng=%d matched_spa=%d not_matched_spa=%d *****" % \
			(chunk_number, i, name_found_eng, name_not_found_eng, name_found_spa, name_not_found_spa )
			
		# store article names read from curent chunk
		article_names_eng = [row['name_eng'] for row in next_n_lines]
		article_names_spa = [row['name_spa'] for row in next_n_lines]

		# Get article sizes from Wikipedia
		wiki_sizes_eng, error_list_eng = get_wiki_sizes(WIKIPEDIA_ENG_API_URL, article_names_eng)
		wiki_sizes_spa, error_list_spa = get_wiki_sizes(WIKIPEDIA_SPA_API_URL, article_names_spa)
		#print "test"
		#print wiki_sizes

		# Update stats: size of returned dictionary reflects number of successful queries.
		name_found_eng += len(wiki_sizes_eng)-len(error_list_eng)
		name_not_found_eng += len(error_list_eng)

		name_found_spa += len(wiki_sizes_spa)-len(error_list_spa)
		name_not_found_spa += len(error_list_spa)

		# Write the chunk of rows to file 
		for row in next_n_lines:
			# Add Wikipedia article size to dict
			row['wiki_size_eng'] = wiki_sizes_eng[row['name_eng']]
			row['wiki_size_spa'] = wiki_sizes_spa[row['name_spa']]
			# print row['name'], row['wiki_size'], wiki_sizes[row['name']]

			# Encode
			# Based on J.F.Sebastian's comment at
			# http://stackoverflow.com/questions/5838605/python-dictwriter-writing-utf-8-encoded-csv-files
			unicode_row = dict( (k, v.encode('utf-8') if isinstance(v, unicode) else v) \
				for k,v in row.iteritems() )

			# Now write it
			dw.writerow( unicode_row )

			# iteration counter
			i += 1
 
		# TODO: table format?
		for article_name in error_list_eng:			
			ferror.write(article_name.encode('utf-8') + "\tENG" + "\n") 
		for article_name in error_list_spa:			
			ferror.write(article_name.encode('utf-8') + "\tSPA" + "\n") 

	# Write totals to file and screen
	print "***** Chunk: %d | total %d | matched_eng %d | not_matched_eng %d | matched_spa %d | not_matched_spa %d" % \
		(chunk_number, i, name_found_eng, name_not_found_eng, name_found_spa, name_not_found_spa )
	totals_str = '\t'.join([str(chunk_number), str(i), 
		str(name_found_eng), str(name_not_found_eng), 
		str(name_found_spa), str(name_not_found_spa)])

	ftotals.write(totals_str +"\n")

	ftotals.close()
	ferror.close()
	fout.close()

	# TODO: returned result is currently not used, find a way to use it with multiprocessing.
	return name_found_eng, name_not_found_eng, name_found_spa, name_not_found_spa
		

def multiprocess_it(function_to_parallelize, origfile):
	# read file
	forig = open(origfile, "rU")

	# split to SPLIT_SIZE chunks
	i = 0

	# get header
	header_row = forig.readline()[:-1].split('\t')

	while True: 
		#print "iteration:", i

		chunked_lines = forig.readlines(SPLIT_SIZE)
		if not chunked_lines:
			break

		# Name all the new files
		root, ext = os.path.splitext(origfile)

		chunkfile = "_" + root + str(i) + ext
		chunkmatchedfile = "_" + root + "_output" + str(i) + ext
		chunkerrorfile = "_" + root + "_error" + str(i) + ext
		chunktotalsfile = "_" + root + "_totals" + str(i) + ext
		
		fchunk = open(chunkfile, "w")
		fchunk.writelines(chunked_lines)
		fchunk.close()
		
		# call a process for each part
		#print "process", i 
		p = multiprocessing.Process(target=function_to_parallelize, \
			args=(chunkfile, chunkmatchedfile, chunkerrorfile, chunktotalsfile, i, header_row))
		p.start()

		i+=1 

	forig.close()

if __name__ == "__main__":
	st_time = time.time()
	multiprocess_it(add_person_size_english_spanish, BIO_LIST_FILE)
	print "time: ", time.time() - st_time
