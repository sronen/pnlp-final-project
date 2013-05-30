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
TOPIC.TBL.PATH <- "topic-names-final/%s-topic-names-50-final-fixed.txt"

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

calc.entropy.per.article <- function(topic.shares) {
  # Find entropy (actually, number of topics) per article  
  # add 10e-32 to smooth zero values
  entro <- 2^(-sum(topic.shares*log(topic.shares+10e-32)))
  return(entro)
}

load.topics.table <- function(infile) {
  topic.shares <- read.delim(infile, header=T,
                             quote="", # Some article names have quotes, so if "quote" 
                             # isn't set to "" the table won't load properly
                             row.names=1, 
                             check.names=FALSE)
  topic.shares[is.na(topic.shares)] <- 0
  
  num.topics.tbl <- data.frame(apply(topic.shares[, 1:16], 1, calc.entropy.per.article),
                  row.names=rownames(topic.shares))
  names(num.topics.tbl) <- "num.topics"
  num.topics.tbl$name <- row.names(num.topics.tbl)
  num.topics.tbl$name <- gsub("_", " ", num.topics.tbl$name) # replace underscores
  
  return(num.topics.tbl)
}

load.stats.table <- function(lang) {
  sizes.path <- sprintf(SIZES.TBL.PATH,lang)
  rev.hist.path <- sprintf(REV.HIST.TBL.PATH,lang)
  topic.path <- sprintf(TOPIC.TBL.PATH,lang)
  
  sizes.tbl <- load.sizes.table(sizes.path)
  rev.hist.tbl <- load.rev.history.table(rev.hist.path)
  topics.tbl <- load.topics.table(topic.path)
  
  stats.tbl <- merge(sizes.tbl, rev.hist.tbl)
  stats.tbl <- merge(stats.tbl, topics.tbl)
  
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
  # Return the R-squares
  
  words.and.days <- summary(lm(num.words~num.days, lang.stats))
  chars.and.days <- summary(lm(num.chars~num.days, lang.stats))
  
  return(c(words.and.days$adj.r.squared, words.and.days$adj.r.squared))
}

topic.correlations <- function(lang.stats) {
  # Return r-squares
  # very low (under 10%) for all langs
#   topics.and.chars <- summary(lm(num.topics~num.chars, lang.stats))
#   topics.and.words <- summary(lm(num.topics~num.words, lang.stats))
#   topics.and.revs <- summary(lm(num.topics~num.revs, lang.stats))
#   topics.and.uniq.eds <- summary(lm(num.topics~num.uniq.eds, lang.stats))
#   topics.and.days <- summary(lm(num.topics~num.days, lang.stats))
#   return(c(topics.and.chars$adj.r.squared, 
#            topics.and.words$adj.r.squared, 
#            topics.and.revs$adj.r.squared, 
#            topics.and.uniq.eds$adj.r.squared, 
#            topics.and.days$adj.r.squared))
  topics.and.freq <- summary(lm(num.topics~log10(rev.per.day+10e-32), lang.stats))
  topics.and.ed.activ <- summary(lm(num.topics~log10(rev.per.editor+10e-32), lang.stats))
  return(c(topics.and.freq$adj.r.squared, 
           topics.and.ed.activ$adj.r.squared))
}


main <- function() {
  # Load tables
  pt.stats <- load.stats.table("pt")
  es.stats <- load.stats.table("es")
  it.stats <- load.stats.table("it")
  en.stats <- load.stats.table("en")
  
  topic.correlations(en.stats)
  topic.correlations(es.stats)
  topic.correlations(it.stats)
  topic.correlations(pt.stats)
  
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
  hist(pt.stats$num.uniq.eds)
  hist(es.stats$num.uniq.eds)
  hist(it.stats$num.uniq.eds)
  hist(en.stats$num.uniq.eds)
  
  
  par(mfrow=c(2,2))
  hist(pt.stats$rev.per.day)
  hist(es.stats$rev.per.day)
  hist(it.stats$rev.per.day)
  hist(en.stats$rev.per.day)
}

#main()