
# Generate confusion matrix for featured articles
# 
# 1) Load table of expected categories for featured article
# 2) Load the table of topics we found for featured artices.
# 3) Find the max topic for each article. 
# 4) Compare.

spa.fa.categories.file <- "../../datasets/wikipedia_bio_lists/top_lists/featured_bios_table_spa.tsv"
fa.expected.cats <- read.csv(spa.fa.categories.file,
                              sep='\t',header=TRUE,
                              row.names=1, check.names=FALSE)

spa.topic.shares.file <- "../../datasets/categories_2013-02-17/es-topics-full.txt"
all.topic.shares <- read.csv(spa.topic.shares.file,
                             header=TRUE, sep='\t',
                             quote="", # Some article names have quotes, and if quote isn't set to "" the table won't load properly
                             row.names=1, check.names=FALSE)

# select only the featured articles
fa.observed.topics.shares <- all.topic.shares[rownames(all.topic.shares) %in% rownames(fa.expected.cats),]



# get maximum topic for each article, and write to a DF
fa.observed.max.topics.v <- colnames( fa.observed.topics.shares[
  apply(fa.observed.topics.shares, 1, 
  function(x) max(which(x == max(x, na.rm = TRUE))))] )

fa.observed.cats <- data.frame(fa.observed.max.topics.v, 
                               row.names=rownames(fa.observed.topics.shares) )
colnames(fa.observed.cats)[1] <- "Category"
# Remove suffixes to category names, as duplicates are allowed.
fa.observed.cats$Category <- gsub("\\.(.*)","", fa.observed.cats$Category)



# Need to find those!
# vc <- setdiff(rownames(fa.expected.cats), rownames(fa.observed.cats))

# Get the category for 