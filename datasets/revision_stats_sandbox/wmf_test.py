# -*- coding: utf-8 -*-
import os, sys, time
import codecs
import datetime
from gzip import GzipFile
from wmf import dump

# DUMP_ROOT = "../wikipedia_stub_meta_history/" # update accordingly
DUMP_ROOT = "../../../wiki-dumps/"

DUMP_FILES = {"en": "enwiki-20130503-stub-meta-history.xml",
	"pt": "ptwiki-20130505-stub-meta-history.xml",
	"es": "eswiki-20130429-stub-meta-history.xml",
	"it": "itwiki-20130513-stub-meta-history.xml" }

# This is a list of the person articles we downloaded, based on the lists
# from DBpedia. We want to get revision history for these articles only.
LIST_OF_BIOS_IN_LANG = "../%s/2kb-ok.txt"

OUTPUT_FILE = "results/output_%s.txt"
ERROR_FILE = "results/error_%s.txt"

'''
Accent matching! - handled thru manually matching stuff!
count total number of actual articles (not talk, etc.)?
multiprocessing?
'''

def populate_list_of_persons(infile):
	# Add names from given file to a list of articles we're after
	fin = open(infile, "rU")
	
	persons = []

	for line in fin:
		name = line.strip().decode('utf-8')
		persons.append(name.replace("_", " "))

	return persons


if __name__ == "__main__":

	start_time = time.time()

	# Get the path from user input
	dump_lang = sys.argv[1].lower()
	path = os.path.join(DUMP_ROOT, DUMP_FILES[dump_lang])
	fp = codecs.open(path, "rU")

	try:
		# Support GZip compressed files as well 
		is_compressed = sys.argv[2]
		if is_compressed=="T" or is_compressed=="True":
			# User wants to process a compressed file
			fp = GzipFile(path, "r")
	except IndexError:
		# assume not compressed
		pass

	dumpIterator = dump.Iterator(fp)

	list_of_persons = \
		populate_list_of_persons(LIST_OF_BIOS_IN_LANG % dump_lang)

	fout = open(OUTPUT_FILE % dump_lang, "w")
	ferror = open(ERROR_FILE % dump_lang, "w")
	page_count = 0
	bio_count = 0

	# log the attribute errors
	attrib_errors = []

	for page_count, page in enumerate(dumpIterator.readPages()):
		#Do things with a page
		#like extract it's title: page.getTitle()
		#or it's ID: page.getId()
		if page_count % 1000 ==0:
			print page_count
		
		rev_count = 0
		unique_editors = set()

		article_title = page.getTitle()
		decoded_title = article_title.decode('utf-8') if not isinstance(article_title, unicode) else article_title

		try:
			if decoded_title not in list_of_persons:
				fout.write("X " + decoded_title.encode('utf-8') + "\n")
				#print "X " + encoded_title
				continue
		except UnicodeEncodeError:
				print "UnicodeException: X " + decoded_title
				ferror.write("UnicodeEncode: %s \n" % decoded_title.encode('utf-8'))
		except Exception:
				print "Exception: X " + decoded_title
				ferror.write("Other: %s \n" % decoded_title.encode('utf-8'))

		bio_count += 1

		rev1_time = page.readRevisions().next().getTimestamp()
		rev1_time = datetime.datetime.fromtimestamp(int(rev1_time)).strftime('%Y-%m-%dT%H:%M:%S')

		rev_count = 0

		for revision in page.readRevisions():
			#Do things with a revision
			#like extracting its text: revision.getText()
			#or it's comment: revision.getComment()
			rev_count += 1
			try:
				unique_editors.add(revision.getContributor().getUsername())
			except AttributeError:
				print "AttribError in", decoded_title.encode('utf-8'), "skipping"
				attrib_errors.append(decoded_title)
				ferror.write("Attrib: %s \n" % decoded_title.encode('utf-8'))
				break # skip to next articel

		fout.write("\t".join(str(v) for v in [decoded_title.encode('utf-8'), page.getId(), rev_count, len(unique_editors), rev1_time]) + "\n")
		#print("\t".join(str(v) for v in [decoded_title.encode('utf-8'), page.getId(), rev_count, len(unique_editors), rev1_time]))

	fout.close()
	fp.close()

	print "total:", page_count, " ppl:", bio_count

	print "ERRORS:"
	for err in attrib_errors:
		print err.encode('utf-8') + "||"

	print "time: ", time.time()-start_time