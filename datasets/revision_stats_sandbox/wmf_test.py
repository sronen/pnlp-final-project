# -*- coding: utf-8 -*-

import codecs
import datetime
from bz2 import BZ2File
from gzip import GzipFile
from wmf import dump

#path = "eswiki-20130429-pages-logging.xml.gz"

'''
Accent matching!
count total number of actual articles (not talk, etc.)?
multiprocessing?
'''

def populate_list_of_persons(infile):
	fin = codecs.open(infile, "rU", encoding="utf-8")
	fin = open(infile, "rU")
	persons = []

	for line in fin:
		name, clean_size = line.split(", ")
		persons.append(name.replace("_", " "))

	return persons


if __name__ == "__main__":

	path = "ptwiki-20130505-stub-meta-history.xml.gz"
	#path = "enwiki-20130503-stub-meta-history1.xml"
	#fp = BZ2File(path, "r")
	fp = GzipFile(path, "r")
	dumpIterator = dump.Iterator(fp)

	list_of_persons = populate_list_of_persons("2kb-sizes-pt.txt")

	fout = open("output_pt.txt", "w")
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

