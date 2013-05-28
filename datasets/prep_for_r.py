
import sys
from datetime import datetime

SIZES_TABLE_PATH = "%s/2kb-sizes.txt"
SIZES_TABLE_FIXED_PATH = "%s/2kb-sizes-tabs.txt"

REV_HIST_TABLE_PATH = "revision_stats_sandbox/results/%s_person.txt"
REV_HIST_TABLE_DIFF_PATH = "revision_stats_sandbox/results/%s_person_timediff.txt"

TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S" # the timestamp used in the file

# The date for the dumps -- using one minute past midnight of the 
# date given by Wikipedia. 
DUMP_TIME = {"en": "2013-05-03T00:01:00",
	"es": "2013-04-29T00:01:00",
	"it": "2013-05-13T00:01:00",
	"pt": "2013-05-05T00:01:00"}


def convert_to_tabs(lang):
	# convert ", " in the sizes table to tabs 
	print "Converting ", " to tabs in sizes table..." 

	# load file
	inpath = SIZES_TABLE_PATH % lang
	fin = open(inpath, "rU")
	outpath = SIZES_TABLE__FIXED_PATH % lang
	fout = open(outpath, "w")

	# readline, for each line, convert according to dic
	for line in fin:
		name, chars, words = line.strip().split(", ")

		# write to file
		fout.write( "\t".join([name, str(chars), str(words)]) + "\n" )  

	fout.close()
	fin.close()
	print "File written to: %s" % outpath



def find_time_diff(lang):
	# Find time (in days, rounded to nearest day) since first revision
	print "Adding time difference (in days) to rev. history file..." 

	inpath = REV_HIST_TABLE_PATH % lang
	fin = open(inpath, "rU")
	outpath = REV_HIST_TABLE_DIFF_PATH % lang
	fout = open(outpath, "w")

	# read time from table
	for line in fin:
		name, wiki_id, revs, uniq_eds, tstamp = line.strip().split("\t")

		# convert to datetime and find the diff
		rev_time = datetime.strptime(tstamp, TIMESTAMP_FORMAT)
		dump_time = datetime.strptime(DUMP_TIME[lang], TIMESTAMP_FORMAT)

		time_diff = dump_time - rev_time

		# write the timediff
		fout.write("\t".join([name, str(wiki_id), str(revs),
			str(uniq_eds), str(tstamp), str(time_diff.days)]) + "\n")

	fout.close()
	fin.close()
	print "File written to: %s" % outpath


if __name__ == "__main__":
	cmd = sys.argv[1]
	
	lang = sys.argv[2]

	try:
		if cmd=="tabs":
			convert_to_tabs(lang)
		elif cmd=="time":
			find_time_diff(lang)
	except ValueError:
		print "Syntax: python prep_for_r.py time|tabs lang"
