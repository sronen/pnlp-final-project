#### FA HACK: this script was creating by glueing together parts from other scripts.
#### I used ../confusion_matrix/confusion_matrix.R to find topic compositions for all
#### featured articles, as some are listed in the full topic compo file and the rest is 
#### in the complementary FA table. Then, I used category_stat.R to a frequency plot.

library(ggplot2)

ENG.TOPICS.FILE <- "../../datasets/categories_2013-02-17_final/en-article-topics-full.txt"
ENG.TOPICS.FA.FILE <- "../../datasets/categories_2013-02-17_final/en-article-topics-fa.txt"
ENG.FA.LIST <- "../../datasets/wikipedia_bio_lists/top_lists/featured_bios_table_eng.tsv"
SPA.TOPICS.FILE <- "../../datasets/categories_2013-02-17_final/es-article-topics-full.txt"
SPA.TOPICS.FA.FILE <- "../../datasets/categories_2013-02-17_final/es-article-topics-fa.txt"
SPA.FA.LIST <- "../../datasets/wikipedia_bio_lists/top_lists/featured_bios_table_spa.tsv"
MAPPING.TABLE <- "category_mapping.tsv"

load.my.table <- function(my.table.file) {
  # change some of the default arguments for read.csv
  my.table <- read.csv(my.table.file,
                       sep='\t',header=TRUE,
                       quote="", # Some article names have quotes, so if "quote" 
                       # isn't set to "" the table won't load properly
                       row.names=1, check.names=FALSE)
  return(my.table)
}


generate.comparison.df <- function(fa.list.file, 
                                   topic.shares.file1, # Main file 
                                   topic.shares.file2) # additional file (order is meaningless)
{
  ## NOTE: this function gets two file becuse we were missing some featured biographies.
  ## Passing an additional file is a way to correct this.
  fa.expected.cats <- load.my.table(fa.list.file)
  
  # Load shares for all topics
  topic.shares1 <- load.my.table(topic.shares.file1)
  
  # We missed some featured articles, adding them here
  topic.shares2 <- load.my.table(topic.shares.file2)
  
  all.topic.shares <- rbind(topic.shares1, topic.shares2)
  
  # Get only the topic shares of the featured articles and find their categories
  fa.identified.topic.shares <<- all.topic.shares[rownames(all.topic.shares) %in% rownames(fa.expected.cats),]
 
  return(fa.identified.topic.shares)
}

eng.comp.data <- generate.comparison.df(ENG.FA.LIST, 
                                        ENG.TOPICS.FILE, 
                                        ENG.TOPICS.FA.FILE)

spa.comp.data <- generate.comparison.df(SPA.FA.LIST, 
                                        SPA.TOPICS.FILE, 
                                        SPA.TOPICS.FA.FILE)


# English entropy: 2.714043
# Spanish entropy: 2.662469

# Entropy equation for latex:

#\usepackage{amsmath}
#\usepackage{relsize}

#\begin{equation}
#\frac{1}{|A|} \mathlarger{\sum\limits_{i\in{A}} 2^{-\sum\limits_{c\in{C}} p(c)log_{2}(c)}}
#\end{equation}

library(plyr)
library(ggplot2)
library(gridExtra)

DATA.DIR <- "../../datasets/categories_2013-02-17_final/"

load.my.table <- function(my.table.file) {
  # change some of the default arguments for read.csv
  my.table <- read.csv(my.table.file,
                       sep='\t',header=TRUE,
                       quote="", # Some article names have quotes, so if "quote" 
                       # isn't set to "" the table won't load properly
                       row.names=1, check.names=FALSE)
  return(my.table)
}


topic.distribution.figure <- function(eng.topic.shares, # Number of topics per article
                                      spa.topic.shares)
{ 
  eng.topic.nums <- apply(eng.topic.shares[, 1:16], 1, calc.entropy.per.article)
  bins.eng <- hist(eng.topic.nums, breaks=20, plot=F)
  
  bin.sizes <- bins.eng$mids[2] - bins.eng$mids[1] # assume all bins have the same size
  
  probs.eng <- (bins.eng$counts / bin.sizes) / sum(bins.eng$counts / bin.sizes)
  probs.eng.df <- data.frame(bins.eng$mids, probs.eng, "English")
  colnames(probs.eng.df) <- c("BinMids", "Topics", "Lang")
  
  spa.topic.nums <- apply(spa.topic.shares[, 1:16], 1, calc.entropy.per.article)
  bins.spa <- hist(spa.topic.nums, breaks=20, plot=F)
  probs.spa <- (bins.spa$counts / bin.sizes) / sum(bins.spa$counts / bin.sizes)
  probs.spa.df <- data.frame(bins.spa$mids, probs.spa, "Spanish")
  colnames(probs.spa.df) <- c("BinMids", "Topics", "Lang")
  
  probs.df <- rbind(probs.eng.df, probs.spa.df)
  
  p <- ggplot(probs.df, aes(x=BinMids, y=Topics, color=Lang)) + 
    #geom_bar(position="dodge", stat="identity")
    geom_line() + geom_point()
  p <- p + xlab("Number of Topics (k)") + ylab("P(k)")
  return(p)
}

calc.lang.entropy <- function(topic.shares) {
  # Find entropy per language
  # To run:
  # calc.lang.entropy(eng.topic.shares[, 1:16]) # 2.26, not including "other" category
  # calc.lang.entropy(spa.topic.shares[, 1:16]) # 2.21, not including "other" category
  
  entro <- sum(2^(-rowSums(topic.shares*log(topic.shares)))) / nrow(topic.shares)
  return(entro)
}

calc.entropy.per.article <- function(topic.shares) {
  # Find entropy (actually, number of topics) per article  
  entro <- 2^(-sum(topic.shares*log(topic.shares)))
  return(entro)
}

find.category <- function(vct) {
  # Return name of the column with the max value in given row 
  return(names(which.max(vct)))
}

category.stats <- function(topic.shares.df, language.name) {
  # Not considering "other" as a category or a topic...
  x <- data.frame(apply(topic.shares.df[, 1:16], 1, find.category),
                  apply(topic.shares.df[, 1:16], 1, calc.entropy.per.article),
                  row.names=rownames(topic.shares.df))
  names(x)[1] <- "Category"
  names(x)[2] <- "Entropy"
  total.articles <- nrow(x)
  
  cat.stats <- ddply(x, 'Category', .progress = "text", 
                     function(x) c(num.articles=nrow(x), 
                                   percent.articles=round(nrow(x)/total.articles*100,1),
                                   entropy.mean=mean(x$Entropy),
                                   entropy.sd=sd(x$Entropy)) )
  cat.stats$Language <- language.name # Makes it easier to merge and plot in ggplot
  return(cat.stats)
}

eng.stats <- category.stats(eng.comp.data, language.name="English")
print(eng.stats)

spa.stats <- category.stats(spa.comp.data, language.name="Spanish")
print(spa.stats)

all.stats <- rbind(eng.stats, spa.stats) # Now combine them all...

#### Topic distrubtion ####

topic.dist.plot <- topic.distribution.figure(eng.comp.data, spa.comp.data)
topic.dist.plot <- topic.dist.plot + theme(legend.position="none")
print(topic.dist.plot)



#### Category counts and shares. ###
articles.by.cat.plot <- ggplot( all.stats, aes(x=Category, y=percent.articles)) + 
  geom_bar( aes(fill=Language, width=0.7), alpha=1, position="dodge", stat="identity") +  # adjust positon dodge
  geom_text( data=all.stats,
             aes(x=Category, 
                 y=percent.articles, 
                 label=percent.articles,
                 size=12,
                 hjust=-0.2, # keep the label afar from the bar
                 vjust=ifelse(Language=="English", 1.2, 0)) ) + # move English label down
  theme(axis.text.y = element_text(face="bold", colour="#000000", size=16)) + # change axis label font size
  theme(legend.position="none") +
  xlab("") + ylab("% of articles") +
  coord_flip()
print(articles.by.cat.plot)

#### Topics by category ####
topics.by.cat.plot <- ggplot( all.stats, aes(x=Category, y=entropy.mean)) + 
  geom_bar( aes(fill=Language, width=0.7), alpha=1, position="dodge", stat="identity") +  # adjust positon dodge
  geom_text( data=all.stats,
             aes(x=Category, 
                 y=entropy.mean, 
                 label=round(entropy.mean,2),
                 size=12,
                 hjust=-0.2, # keep the label afar from the bar
                 vjust=ifelse(Language=="English", 1.2, 0)) ) + # move English label down
  theme(axis.text.y = element_text(face="bold", colour="#000000", size=16)) + # change axis label font size
  theme(legend.position="none") +
  xlab("") + ylab("Number of topics") +
  coord_flip()
print(topics.by.cat.plot)

postscript("articles_by_cat_plot.eps")
grid.arrange(articles.by.cat.plot, ncol=1, 
             widths=unit(c(15), "cm"),
             heights=unit(c(13), "cm") )
dev.off()

postscript("topics_by_cat_plot.eps")
grid.arrange(topics.by.cat.plot, ncol=1, 
             widths=unit(c(15), "cm"),
             heights=unit(c(13), "cm") )
dev.off()

postscript("topics_dist_plot.eps")
grid.arrange(topic.dist.plot, ncol=1, 
             widths=unit(c(13), "cm"),
             heights=unit(c(13), "cm") )
dev.off()