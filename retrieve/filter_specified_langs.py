'''
Get a tab-and-comma-separated list of the following format:
 lang_code1,article_name1\tlang_code2,article_name2\t...

Return a file of the same format with only the selected languages.
Script assumes all lines contains all the languages that are set to be kept.
'''

INFILE = "english_spanish_people.tsv"
OUTFILE = "english_spanish_people_only.tsv"
LANGS_TO_KEEP = ["en", "es"]
SEP = "||"

fin = file(INFILE, "rU")
fout = open(OUTFILE, "w")

for line in fin:
	wiki_editions = line.rstrip().split('\t')

	for edition in wiki_editions:
		#print edition
		try:
			lang_code, article_name = edition.split(SEP)
			if lang_code in LANGS_TO_KEEP:
				fout.write("%s%s%s\t" % (lang_code,SEP,article_name))
		except ValueError:
			# probably because a comma was used in the person's name
			print "Error (extra comma?): %s" % edition
			continue

	fout.write("\n")

fout.close()