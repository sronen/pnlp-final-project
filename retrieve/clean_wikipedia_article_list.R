# Remove duplicate entries from a list of bios in English and Spanish Wikipedias,
# Remove articles that weren't found (size=-1), and write output to file.

PNLP.DIR <- "~/Development/pnlp-final-project/datasets/wikipedia_bio_lists/people_in_langs/"
setwd(PNLP.DIR)

INFILE <- "parallel_eng_spa_sizes.tsv"
OUTFILE <- "parallel_eng_spa_sizes_clean.tsv"

# Read from file 
bios <- read.csv(INFILE, sep = "\t", header=T)

# Remove duplicate records: first English
bios.unique <- bios[!duplicated(bios[c("name_eng")]),]
# ...Then Spanish
bios.unique <- bios.unique[!duplicated(bios.unique[c("name_spa")]),]
# Note that "bios.unique <- unique(bios)" requires row to have duplicate
# values in both language columns to be removed, so it's not enough


# Remove articles not found (size=-1) in either lanugage
bios.unique.found <- bios.unique[bios.unique$wiki_size_eng!=-1
                                 & bios.unique$wiki_size_spa!=-1,]

write.table(bios.unique.found, file=OUTFILE, sep='\t', quote=F, row.names=F)
