from glob import glob
import os
import codecs

def count_stats(fp):
	# return number of chars and number of words in file
	print fp.encode('utf-8')

	with open(fp) as fh:
		ftext = fh.read()
		return len(ftext), len(ftext.split())

def stats_for_files(dirname, outfile):
	# write a table containing for each file in folder 
	# "dirname" its name, number of characters, and number of words
	fout = codecs.open(dirname + "_counts.tsv", "w")

	#for num_words in map(countwords, filter(os.path.isfile, glob(my_dir + "*.txt") ) ):
	for fname in filter(os.path.isfile, glob(os.path.join(dirname, "*.txt") ) ):
		ufname = fname.decode("utf-8")
		print fname, ufname

		num_chars, num_words = count_stats(ufname)
		fout.write("\t".join([ufname.encode('utf-8'), str(num_chars), str(num_words)]) + "\n")

	fout.close()


if __name__ == "__main__":
	#langnames = ["en", "es", "it", "pt"]
	langnames = ["pt"]

	for lang in langnames:
		outfile = lang + "_count.tsv"
		dirname = lang # + "/2kb-clean"
		stats_for_files(dirname, outfile)

