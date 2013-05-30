#source('../datasets/prep_data.R', chdir=T)

# preliminary analysis

library(lattice) # for correlation plots
library(reshape) # for melt

prep.num.topics.only.table <- function(article.stats, lang) {
  # leave only the name and the number of topics columns,
  # and add the lanugage name for identification.
  
  topic.only.stats <- article.stats[,c("name", "num.topics")]
  topic.only.stats$language <- lang
  return(topic.only.stats) 
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

plot.topic.distribution.figure <- function(article.topic.nums) { 
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
  return(p)
}


plot.lang.pairwise.correlations <- function(article.stats, lang.name) {
  # find pairwise correlations between columns of the stats DF.
  jpeg(sprintf("wiki_stat_correls_%s.png", lang.name), width=900, height=900)
  correl.lattice <- splom(article.stats[,c("num.words",
                            "num.revs","num.uniq.eds",
                            "rev.per.editor","rev.per.day",
                            "num.topics")],
        main=sprintf("Correlations (%s)", lang.name))
  print(correl.lattice)
  dev.off()
}


  #### Topic diversity prob. distrubtion  ####
  en.topic.nums <- prep.num.topics.only.table(en.article.stats, "English") 
  es.topic.nums <- prep.num.topics.only.table(es.article.stats, "Spanish") 
  it.topic.nums <- prep.num.topics.only.table(it.article.stats, "Italian") 
  pt.topic.nums <- prep.num.topics.only.table(pt.article.stats, "Portuguese") 
  
  all.article.topic.nums <- rbind(en.topic.nums, es.topic.nums,
                                   it.topic.nums, pt.topic.nums)
  
  postscript("fig-topic-diversity-probs.eps")
  p <- plot.topic.distribution.figure(all.article.topic.nums)
  eval(p)
  dev.off()
  
  #### Topic diversity box plot  ####
  postscript("fig-topic-diversity-boxplot.eps")
  p <- ggplot(all.article.topic.nums, aes(x=language, y=num.topics, fill=language)) +
    geom_boxplot() +
    guides(fill=F) +
    coord_flip()
  eval(p)
  dev.off()
  
  
  ## Find correlations between the different stats:
  ## Spoiler: nothing interesting...
  plot.lang.pairwise.correlations(pt.article.stats, "pt")
  plot.lang.pairwise.correlations(es.article.stats, "es")
  plot.lang.pairwise.correlations(it.article.stats, "it")
  plot.lang.pairwise.correlations(en.article.stats, "en")
  
  # Rev. distribution by lang
  # only 194 articles (out of >20k with over 1000 edits!)
  
  exit()

  # TODO: draw hist distributions using lattice?
  # Sample code for scatterplots for each combination of two factors 
  xyplot(mpg~wt|cyl.f*gear.f, 
         main="Scatterplots by Cylinders and Gears", 
         ylab="Miles per Gallon", xlab="Car Weight")

  # 
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
