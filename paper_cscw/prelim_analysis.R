source('../datasets/prep_data.R', chdir=T)

library(lattice) # for correlation plots
library(reshape) # for melt

# preliminary analysis
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


find.bin.mids <- function(x, bin.breaks) {
  bins <- hist(x, breaks=bin.breaks, plot=F)
  return(bins$mids)
}

find.bin.probs <-function(x, bin.breaks) {
  bins <- hist(x, breaks=bin.breaks, plot=F)
  bin.sizes <- bins$mids[2] - bins$mids[1] # assume all bins have the same size
  bin.probs <- (bins$counts/bin.sizes) / sum(bins$counts/bin.sizes)
  return(bin.probs)
}

plot.topic.distribution.figure <- function(article.topics.nums) { 
  
  article.topic.nums<-all.article.topic.nums
  
  # temp hack to force the same number of breaks in all languages:
  # if an integer is passed, e.g, breaks=20, R uses it only as a recommedation only.
  # TODO: use min and max values from the DF. 
  bin.breaks <- seq(1.0, 5.2, 0.2)
    
  bins <- ddply(article.topic.nums, 'language', .progress = "text", 
                  function(x) c(bin.mids=find.bin.mids(x$num.topics,bin.breaks), 
                                bin.probs=find.bin.probs(x$num.topics,bin.breaks)) )
  
  # melt into the desired shape for plotting (might be a better way):
  # first, melt the mids part...
  molten.mids <- melt(bins[, 1:22],id=c("language"))
  molten.mids$variable <- NULL # remove this column
  colnames(molten.mids)[colnames(molten.mids)=="value"] <- "mids"
  
  # then the probs part...
  molten.probs <- melt(bins[, c(1,23:43)],id=c("language"))
  molten.probs$variable <- NULL # remove this column
  colnames(molten.probs)[colnames(molten.probs)=="value"] <- "probs"
  
  # ...now combine!
  molten.bins <- cbind(molten.mids, molten.probs[,c("probs")])
  colnames(molten.bins) <- c("language", "mids", "probs")
  
  p <- ggplot(molten.bins, aes(x=mids, y=probs, color=language)) + 
    #geom_bar(position="dodge", stat="identity")
    geom_line() + geom_point()
  p <- p + xlab("Number of Topics (k)") + ylab("P(k)")
  
  postscript("fig-topic-diversity-probs.eps")
  eval(p)
  dev.off()
}


plot.lang.pairwise.correlations <- function(article.stats, lang.name) {
  # find pairwise correlations between columns of the stats DF.
  jpeg(sprintf("wiki_stat_correls_%s.png", lang.name), width=900, height=900)
  correl.lattice <- splom(pt.article.stats[,c("num.words",
                            "num.revs","num.uniq.eds",
                            "rev.per.editor","rev.per.day",
                            "num.topics")],
        main=sprintf("Correlations (%s)", lang.name))
  print(correl.lattice)
  dev.off()
}


prep.num.topics.only.table <- function(article.stats, lang) {
  # leave only the name and the number of topics columns,
  # and add the lanugage name for identification.
  
  topic.only.stats <- article.stats[,c("name", "num.topics")]
  topic.only.stats$language <- lang
  return(topic.only.stats) 
}


main <- function() {
  
  #### Topic distrubtion ####
  en.topic.nums <- prep.num.topics.only.table(en.article.stats, "English") 
  es.topic.nums <- prep.num.topics.only.table(es.article.stats, "Spanish") 
  it.topic.nums <- prep.num.topics.only.table(it.article.stats, "Italian") 
  pt.topic.nums <- prep.num.topics.only.table(pt.article.stats, "Portuguese") 
  
  all.article.topic.nums <- rbind(en.topic.nums, es.topic.nums,
                                   it.topic.nums, pt.topic.nums)
  plot.topic.distribution.figure(all.article.topic.nums)
  
  ## Find correlations between the different stats:
  ## Spoiler: nothing interesting...
  plot.lang.pairwise.correlations(pt.article.stats, "pt")
  plot.lang.pairwise.correlations(es.article.stats, "es")
  plot.lang.pairwise.correlations(it.article.stats, "it")
  plot.lang.pairwise.correlations(en.article.stats, "en")

  
    
#   topic.correlations(en.stats)
#   topic.correlations(es.stats)
#   topic.correlations(it.stats)
#   topic.correlations(pt.stats)
#   
#   # Correlation between length and contribution? 
#   # Nothing to write home about: 0.23 to 0.37
#   length.and.contribution.correlation(pt.stats)
#   length.and.contribution.correlation(es.stats)
#   length.and.contribution.correlation(it.stats)
#   length.and.contribution.correlation(en.stats)
#   
#   length.and.time.correlation(pt.stats)
#   length.and.time.correlation(es.stats)
#   length.and.time.correlation(it.stats)
#   length.and.time.correlation(en.stats)
#   
#   # more uniq editors -> more rev.
#   x <- summary(lm(num.revs~num.uniq.eds, pt.stats))
  
  # Rev. distribution by lang
  # only 194 articles (out of >20k with over 1000 edits!)
  
  par(mfrow=c(2,2))
  hist(pt.article.stats$rev.per.editor)
  hist(es.article.stats$rev.per.editor)
  hist(it.article.stats$rev.per.editor)
  hist(en.article.stats$rev.per.editor)
  
  
  par(mfrow=c(2,2))
  hist(pt.article.stats$num.days)
  hist(es.article.stats$num.days)
  hist(it.article.stats$num.days)
  hist(en.article.stats$num.days)
  
  
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