missing.from.folder <- function(lang, folder.list, orig.list) {
 # find articles listed in the download list for the given language but not downloaded.

  folder.contents$V1 <- gsub("_.txt", "", folder.list$V1)
  folder.contents$V1 <- gsub("_", " ", folder.list$V1)
  if (lang=='en') {
    missing.from.folder <- subset(orig.list, !(name_eng %in% folder.contents$V1))  
    #missing.from.folder <- subset(folder.list, !(V1 %in% orig.list$name_eng))  
  }
  else {
    # Spanish
    missing.from.folder <- subset(orig.list, !(name_spa %in% folder.contents$V1))
    #missing.from.folder <- subset(folder.list, !(V1 %in% orig.list$name_spa))  
  }
  return(missing.from.folder) 
}

# Get the original list of bios we downloaded
setwd("~/Development/pnlp-final-project/datasets/wikipedia_bio_lists")
orig.list <- read.csv('parallel_eng_spa_sizes_clean.tsv', sep="\t")

# Get the files listing the actual contents for each download folder
setwd('~/Development/pnlp-final-project/datasets/parallel_corpora/comparisons/explaintext')


en.folder.contents <- read.table("explaintext_en_dir_contents.txt")
es.folder.contents <- read.table("explaintext_es_dir_contents.txt")

# find the respective english name for each spanish downloaded article 
en.equiv.of.downloaded.es <- orig.list[es.folder.contents$V1,][1]
# now find the difference with english
en.folder.contents$V1 <- gsub("_.txt", "", en.folder.contents$V1)
en.folder.contents$V1 <- gsub("_", " ", en.folder.contents$V1)
in.both.folders.qmark <- subset(en.equiv.of.downloaded.es, name_eng %in% en.folder.contents$V1)  


missing.in.en2 <- missing.from.folder('en', en.folder.contents, orig.list )
missing.in.es2 <- missing.from.folder('es', es.folder.contents, orig.list )