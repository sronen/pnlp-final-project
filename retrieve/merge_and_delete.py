import os

ORIG_FILE =  "parallel_eng_spa_new.tsv"
OUTPUT_TITLE = "name_eng\tname_spa\twiki_size_eng\twiki_size_spa"
ERROR_TITLE = "titles that made the query fail:"
TOTALS_TITLE = "Chunk\tTotal\tok_eng\tbad_eng\tok_spa\tbad_spa"

# Name generation follows get_article_sizes.py

def merge_files(orig_file, suffix, header_row):
	'''
	orig_file: name of the original file being processed; the chunk names are derived from it
	suffix: error/output, etc.
	header row: the entire header row, to be added to the 
	'''
	root, ext = os.path.splitext(orig_file)
	temp_pattern = "_" + root + "_" + suffix + "*" + ext
	merged_file =  root + "_" + suffix + "_all" + ext

	#merge files
	os.system("cat %s | grep -v \"%s\" > %s" % (temp_pattern, header_row, merged_file) )
	os.system("echo '%s' > _temp_file" % header_row.rstrip()) # remove line breaks, echo adds them?
	os.system("cat _temp_file %s > _temp_merged_file" % merged_file )
	os.rename("_temp_merged_file", merged_file)
	os.remove("_temp_file")


if __name__ == "__main__":
	root, ext = os.path.splitext(ORIG_FILE)
	merge_files(ORIG_FILE, "output", OUTPUT_TITLE)
	merge_files(ORIG_FILE, "error", ERROR_TITLE)
	merge_files(ORIG_FILE, "totals", TOTALS_TITLE)

	# delete all remainaing temp files
	os.system("rm %s%s" % ("_*", ext) )
