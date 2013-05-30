#### 
# Load the topics shares file and find topic entropies, 
# then merge with revision history and size table
#
# Some manual prepration to overcome article name encoding issues:
# (1) Convert the ", " separated size files to tab-separated
# (2) Copy the 2kb-sizes-tabs.txt and the 2kb-ok.txt files to Excel.
# (3) Sort the columns on both, then copy the names from 2kb-ok next to the sizes.
# (4) Copy the result to a new text file and sav to 2kb-sizes-fixed.txt, and load to R
#
####

### TODO: 
# (1) Find the names that cannot be merged (e.g., there are 2 in PT)
# (2) load # chars and # words as numbers 
###

DATA.DIR <- "~/Development/pnlp-final-project/datasets/"

SIZES.TBL.PATH <- paste0(DATA.DIR, "%s/2kb-sizes-fixed.txt")
REV.HIST.TBL.PATH <- paste0(DATA.DIR, "revision_stats_sandbox/results/%s_person_timediff.txt")
TOPIC.SHARES.TBL.PATH <- paste0(DATA.DIR, "topic-names-final/%s-topic-names-50-final-fixed.txt")

`%notin%` <- function(x,y) !(x %in% y)

load.rev.history.table <- function(infile) {
  rev.hist <- read.delim(infile, header=F,
                         comment.char="", quote="", # disable comments and quotes 
                         colClasses=c("character", "integer", "integer", "integer",
                                      "character", "integer"),
                         col.names=c("name", "id", "num.revs", "num.uniq.eds",
                                     "date.first.rev", "num.days"))
  rev.hist$date.first.rev <- NULL # drop this
  rev.hist$rev.per.editor <- rev.hist$num.revs / rev.hist$num.uniq.eds
  rev.hist$rev.per.day <- rev.hist$num.revs / rev.hist$num.days
  return(rev.hist)
}


load.sizes.table <- function(infile) {
  size.stats <- read.delim(infile, header=F,
                           comment.char="", quote="", # disable comments and quotes 
                           colClasses=c("character", "integer", "integer"),
                           col.names=c("name", "num.chars", "num.words"))
  size.stats$name <- gsub("_", " ", size.stats$name) # replace underscores
  return(size.stats)
}


find.article.category <- function(vct) {
  # Return name of the column with the max value in given row 
  return(names(which.max(vct)))
}

calc.article.entropy <- function(topic.shares) {
  # Find topic diversity (=2^entropy) per article  
  # add 10e-32 to smooth zero values
  # NOTE: must be a function so it can be mapped to values using "apply"
  entro <- 2^(-sum(topic.shares*log(topic.shares+10e-32)))
  return(entro)
}


calc.lang.entropy <- function(topic.shares) {
  # Find avg. topic diversiry per language. To run:
  # calc.lang.entropy(eng.topic.shares[, 1:16]) # 2.26, not including "other" category
  # calc.lang.entropy(spa.topic.shares[, 1:16]) # 2.21, not including "other" category
  entro <- sum(2^(-rowSums(topic.shares*log(topic.shares)))) / nrow(topic.shares)
  return(entro)
}

edition.wide.entropy <- function(topic.shares.df) {
  x <- data.frame(apply(topic.shares.df[, 1:16], 1, calc.article.entropy),
                  row.names=rownames(topic.shares.df))
  names(x)[1] <- "Entropy"
  return(x)
}


load.topics.table <- function(infile) {
  # Find the category and topic diversity for each article
  topic.shares <- read.delim(infile, header=T,
                             # Some article names have quotes, so if "quote" 
                             # isn't set to "" the table won't load properly
                             quote="",
                             row.names=1, 
                             check.names=FALSE)
  topic.shares[is.na(topic.shares)] <- 0
  
  # NOTE: "Other" is the last column -- we're not considering it as a category
  num.topics.tbl <- data.frame(apply(topic.shares[, 1:16], 1, find.article.category),
                               apply(topic.shares[, 1:16], 1, calc.article.entropy),
                               row.names=rownames(topic.shares))
  names(num.topics.tbl) <- c("category", "num.topics")
  num.topics.tbl$name <- row.names(num.topics.tbl)
  num.topics.tbl$name <- gsub("_", " ", num.topics.tbl$name) # replace underscores
  
  return(num.topics.tbl)
}

prep.article.stats.table <- function(lang) {
  # Merge the different statistics tables 
  
  sizes.path <- sprintf(SIZES.TBL.PATH,lang)
  rev.hist.path <- sprintf(REV.HIST.TBL.PATH,lang)
  topic.path <- sprintf(TOPIC.SHARES.TBL.PATH,lang)
  
  sizes.tbl <- load.sizes.table(sizes.path)
  rev.hist.tbl <- load.rev.history.table(rev.hist.path)
  topics.tbl <- load.topics.table(topic.path)
  
  stats.tbl <- merge(sizes.tbl, rev.hist.tbl)
  stats.tbl <- merge(stats.tbl, topics.tbl)
  
  # debug
  #print(summary(stats.tbl[ ,c("num.chars", "num.words", 
  #                            "num.revs", "num.uniq.eds", "num.days")]))
  
  return(stats.tbl)
}


# Load tables
en.article.stats <- prep.article.stats.table("en")
es.article.stats <- prep.article.stats.table("es")
it.article.stats <- prep.article.stats.table("it")
pt.article.stats <- prep.article.stats.table("pt")
