'''
Get a tab-and-comma-separated list of the following format:
 lang_code1,article_name1\tlang_code2,article_name2\t...

Return a file of the same format with only the selected languages.
NOTE: the script assumes all lines contains all the languages that should be kept.
E.g., if English and Spanish are to be kept, each line contains at least English 
and Spanish.

Languages are sorted arphabetically in the returned file.
'''

from collections import defaultdict

INFILE = "english_spanish_people_only.tsv" # test file
OUTFILE = "parallel_eng_spa.tsv"
LANGS_TO_KEEP = ["en", "es"]
SEP = "||"

fin = file(INFILE, "rU")
fout = open(OUTFILE, "w")

for line in fin:
	wiki_editions = line.rstrip().split('\t')
	kept_editions = defaultdict()

	for edition in wiki_editions:
		try:
			lang_code, article_name = edition.split(SEP)

			if lang_code in LANGS_TO_KEEP:
				kept_editions[lang_code] = article_name
				#print "Added:", lang_code, article_name

		except ValueError:
			# probably because a comma was used in the person's name
			print "Error (extra comma?): %s" % edition
			continue

	 
	for lang_code in sorted(kept_editions):
		fout.write("%s%s%s\t" % (lang_code,SEP,kept_editions[lang_code]))

	fout.write("\n")

fout.close()