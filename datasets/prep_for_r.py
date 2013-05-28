

import datetime

SIZES_TABLE_PATH = "%s/2kb-sizes.txt"
SIZES_TABLE_FIXED_PATH = "%s/2kb-sizes-tabs.txt"

REV_HIST_TABLE_PATH = "revision_stats_sandbox/results/person_%s.txt"
REV_HIST_TABLE_DIFF_PATH = "revision_stats_sandbox/results/person_%s_timediff.txt"

TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S" # the timestamp used in the file
# Populate with actual dump times
DUMP_TIME = {"en": "2013-05-03T09:00:00",
	"es": "2013-05-03T09:00:00",
	"it": "2013-05-03T09:00:00",
	"pt": "2013-05-03T09:00:00"}


def convert_to_tabs(lang):
	# convert ", " in the sizes table to tabs 

	# load file
	fin = open(SIZES_TABLE_PATH % lang, "rU")
	fout = open(SIZES_TABLE__FIXED_PATH % lang, "w")

	# readline, for each line, convert according to dic
	for line in fin:
		name, chars, words = line.strip().split(", ")

		# write to file
		fout.write( "\t".join([name, str(chars), str(words)]) + "\n" )  

	fout.close()
	fin.close()



def find_time_diff(lang):
	# Find time (in days, rounded to nearest day) since first revision

	fin = open(SIZES_TABLE_PATH % lang, "rU")
	fout = open(SIZES_TABLE__FIXED_PATH % lang, "w")

	# read time from table
	for line in fin:
		name, wiki_id, revs, uniq_eds, tstamp = line.strip().split("\t")

		# convert to datetime and find the diff
		rev_time = datetime.strptime(tstamp, TIMESTAMP_FORMAT)
		dump_time = datetime.strptime(DUMP_TIMES[lang], TIMESTAMP_FORMAT)

		time_diff = dump_time - rev_time

		# write the timediff
		fout.write("\t".join([name, wiki_id, revs, uniq_eds, time_diff.days]) + "\n")

	fout.close()
	fin.close()
	print "time done!"


if __name__ == "__main":
	cmd = sys.argv[1]
	print cmd
	lang = sys.argv[2]

	try:
		if cmd=="tabs":
			print "tabs...cat "
			convert_to_tabs(lang)
		elif cmd=="time":
			print "time..." 
			find_time_diff(lang)
	except ValueError:
		print "Syntax: python prep_for_r.py time|tabs lang"
