###
# (1) Convert the ", " separated size files to tab-separated
# (2) Copy the 2kb-sizes-tabs.txt and the 2kb-ok.txt files to Excel.
# (3) Sort the columns on both, then copy the names from 2kb-ok next to the sizes.
# (4) Copy the result to a new text file and sav to 2kb-sizes-fixed.txt, and load to R
###

### TODO: 
# (1) Find the names that cannot be merged (e.g., there are 2 in PT)
# (2) load # chars and # words as numbers 


ROOT.DIR <- "~/Development/pnlp-final-project/datasets/"
setwd(ROOT.DIR)

SIZES.TBL.PATH <- "%s/2kb-sizes-fixed.txt"
REV.HIST.TBL.PATH <- "revision_stats_sandbox/results/%s_person_timediff.txt"


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

`%notin%` <- function(x,y) !(x %in% y)

load.stats.table <- function(lang) {
  
  sizes.path <- sprintf(SIZES.TBL.PATH,lang)
  rev.hist.path <- sprintf(REV.HIST.TBL.PATH,lang)
  
  sizes.tbl <- load.sizes.table(sizes.path)
  rev.hist.tbl <- load.rev.history.table(rev.hist.path)
  
  stats.tbl <- merge(sizes.tbl, rev.hist.tbl)
  
  # debug
  print(summary(stats.tbl[ ,c("num.chars", "num.words", 
                              "num.revs", "num.uniq.eds", "num.days")]))
  
  return(stats.tbl)
}

length.and.contribution.correlation <- function(lang.stats) {
  # Return the R-sqaures
  
  words.and.revs <- summary(lm(num.words~num.revs, lang.stats))
  chars.and.revs <- summary(lm(num.chars~num.revs, lang.stats))
  words.and.eds <- summary(lm(num.words~num.uniq.eds, lang.stats))
  chars.and.eds <- summary(lm(num.chars~num.uniq.eds, lang.stats))
  
  return(c(words.and.revs$adj.r.squared, chars.and.revs$adj.r.squared,
           words.and.eds$adj.r.squared, chars.and.eds$adj.r.squared))
}

length.and.time.correlation <- function(lang.stats) {
  # Return the R-sqaures
  
  words.and.days <- summary(lm(num.words~num.days, lang.stats))
  chars.and.days <- summary(lm(num.chars~num.days, lang.stats))
  
  return(c(words.and.days$adj.r.squared, words.and.days$adj.r.squared))
}

# Load tables
pt.stats <- load.stats.table("pt")
es.stats <- load.stats.table("es")
it.stats <- load.stats.table("it")
en.stats <- load.stats.table("en")

# Correlation between length and contribution? 
# Nothing to write home about: 0.23 to 0.37
length.and.contribution.correlation(pt.stats)
length.and.contribution.correlation(es.stats)
length.and.contribution.correlation(it.stats)
length.and.contribution.correlation(en.stats)

length.and.time.correlation(pt.stats)
length.and.time.correlation(es.stats)
length.and.time.correlation(it.stats)
length.and.time.correlation(en.stats)

# more uniq editors -> more rev.
x <- summary(lm(num.revs~num.uniq.eds, pt.stats))

# Rev. distribution by lang
# only 194 articles (out of >20k with over 1000 edits!)

par(mfrow=c(2,2))
hist(pt.stats$rev.per.editor)
hist(es.stats$rev.per.editor)
hist(it.stats$rev.per.editor)
hist(en.stats$rev.per.editor)


par(mfrow=c(2,2))
hist(pt.stats$num.days)
hist(es.stats$num.days)
hist(it.stats$num.days)
hist(en.stats$num.days)

par(mfrow=c(2,2))
hist(pt.stats$rev.per.day)
hist(es.stats$rev.per.day)
hist(it.stats$rev.per.day)
hist(en.stats$rev.per.day)
