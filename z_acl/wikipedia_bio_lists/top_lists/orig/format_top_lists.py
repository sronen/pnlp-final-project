#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
given a list of featured bios in the following format:
<category1>
<bio1><sep><bio2><sep><bio3><sep>...
<empty line>
<category2>
<bio1><sep><bio2><sep><bio3><sep>...
<empty line>

Convert it to a table of this format:
<bio name><category>

The script is heavily dependent on the format!
'''

CATEGORY_INDICATORS = ["biographies", "Biographies", 
	"biographies of ", "Biographies of "]


def convert_bio_list(infile, outfile, sep):
	fin = open(infile, "rU")
	fout = open(outfile, "w")
	fout.write("Article\tWikiCategory\n")

	### TODO: this script may generate an extra space at the end
	### of each line!!! Verify this.
	for line in fin:
		# note that the iterator is incremented within the loop as well...
		cat_title =  line.strip()

		for indic in CATEGORY_INDICATORS:
			# Remove indicators
			cat_title =  cat_title.replace(indic, "")
		
		# read next line and get the article names
		line = next(fin)
		article_names = line.strip().split(sep) 
		
		# write to new file

		for article in article_names:
			if sep in article:
				# Verify we got the split right
				print "Found separator in %s. Check input file and re-run"
			fout.write("%s\t%s\n" % (article, cat_title))

		#  skip following empty line
		try:
			next(fin)
		except StopIteration:
			print "Probably done! Make sure there's no unnecessary whitespace!"

	fout.close()
	fin.close()


if __name__ == "__main__":
	convert_bio_list("featured_bios_spa.txt", 
		"featured_bios_table_spa.tsv", sep=" – ")
	convert_bio_list("featured_bios_eng.txt", 
		"featured_bios_table_eng.tsv", sep=" · ")
