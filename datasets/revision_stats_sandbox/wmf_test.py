# -*- coding: utf-8 -*-
import os, sys
import codecs
import datetime
from gzip import GzipFile
from wmf import dump

#path = "eswiki-20130429-pages-logging.xml.gz"

DUMP_ROOT = "../wikipedia_stub_meta_history/" # update accordingly

DUMP_FILES = {"en": "enwiki-20130503-stub-meta-history.xml",
	"pt": "ptwiki-20130505-stub-meta-history.xml",
	"es": "eswiki-20130429-stub-meta-history.xml",
	"it": "itwiki-20130513-stub-meta-history.xml" }

# This is a list of the person articles we downloaded, based on the lists
# from DBpedia. We want to get revision history for these articles only.
LIST_OF_BIOS_IN_LANG = "../%s/2kb.txt"

OUTPUT_FILE = "output_%s"

'''
Accent matching!
count total number of actual articles (not talk, etc.)?
multiprocessing?
'''

def populate_list_of_persons(infile):
	# Add names from given file to a list of articles we're after

	fin = codecs.open(infile, "rU", encoding="utf-8")
	fin = open(infile, "rU")
	persons = []

	for line in fin:
		name = line.strip().replace("_", " ")
		persons.append(name)

	return persons


if __name__ == "__main__":

	# Get the path from user input
	dump_lang = sys.argv[1].lower()
	path = os.path.join(DUMP_ROOT, DUMP_FILES[dump_lang])
	fp = open(path, "r")

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
	print list_of_persons

	fout = open(OUTPUT_FILE % dump_lang, "w")
	page_count = 0


	for page_count, page in enumerate(dumpIterator.readPages()):
		#Do things with a page
		#like extract it's title: page.getTitle()
		#or it's ID: page.getId()
		if page_count % 100 ==0:
			print page_count
		
		rev_count = 0
		unique_editors = set()
		#print page.getTitle()

		article_title = page.getTitle()
		encoded_title = article_title.encode('utf-8') if isinstance(article_title, unicode) else article_title

		try:
			if article_title not in list_of_persons:
				fout.write("X " + encoded_title + "\n")
				#print "X " + encoded_title
				continue
		except UnicodeEncodeError:
				print "UnicodeException: X " + encoded_title
		except Exception:
				print "Exception: X " + encoded_title

		# Unicode
		fout.write(encoded_title + "\n")
		# print(encoded_title)
		continue

		rev1_time = page.readRevisions().next().getTimestamp()
		rev1_time = datetime.datetime.fromtimestamp(int(rev1_time)).strftime('%Y-%m-%dT%H:%M:%S')

		rev_count = 0

		for revision in page.readRevisions():
			#Do things with a revision
			#like extracting its text: revision.getText()
			#or it's comment: revision.getComment()
			#print revision
			rev_count += 1
			unique_editors.add(revision.getContributor().getUsername())

		fout.write("\t".join(str(v) for v in [encoded_title, page.getId(), rev_count, len(unique_editors), rev1_time]) + "\n")
		# print("\t".join(str(v) for v in [encoded_title, page.getId(), rev_count, len(unique_editors), rev1_time]))

	fout.close()
	fp.close()
