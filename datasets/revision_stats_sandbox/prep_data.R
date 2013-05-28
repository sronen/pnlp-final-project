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

load.rev.history.table <- function(infile) {
  rev.hist <- read.delim(infile, header=F, 
                         comment.char="", quote="", # disable comments and quotes 
                         col.names=c("name", "id", "num.revs", "num.uniq.eds", "date.first.rev"))
}

load.sizes.table <- function(infile) {
  size.stats <- read.delim(infile, header=F, colClasses=c("character", "integer", "integer"),
                         comment.char="", quote="", # disable comments and quotes 
                         col.names=c("name", "num.chars", "num.words"))
  size.stats$name <- gsub("_", " ", size.stats$name) # replace underscores
  return(size.stats)
}

`%notin%` <- function(x,y) !(x %in% y)

load.stats.table <- function(sizes.path, rev.hist.path) {
  sizes.tbl <- load.sizes.table(sizes.path)
  rev.hist.tbl <- load.rev.history.table(rev.hist.path)
  
  stats.tbl <- merge(sizes.tbl, rev.hist.tbl)
  
  # debug
  print(summary(stats.tbl[ ,c("num.chars", "num.words", "num.revs", "num.uniq.eds")]))
  
  return(stats.tbl)
}

pt.stats <- load.stats.table("pt/2kb-sizes-fixed.txt",
                             "revision_stats_sandbox/results/person_pt.txt")

# No correlation between length and number of topics in PT!
summary(lm(num.words~num.revs, pt.stats))
summary(lm(num.chars~num.revs, pt.stats))
summary(lm(num.words~num.uniq.eds, pt.stats))
summary(lm(num.chars~num.uniq.eds, pt.stats))

# more uniq editors -> more rev.
summary(lm(num.revs~num.uniq.eds, pt.stats))

# only 194 articles (out of >20k with over 1000 edits!)

pt.stats$avg.rev.per.editor <- pt.stats$num.revs / pt.stats$num.uniq.eds
