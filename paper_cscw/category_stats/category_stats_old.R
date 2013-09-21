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

DATA.DIR <- "" # same dir as script

load.my.table <- function(my.table.file) {
  # change some of the default arguments for read.csv
  my.table <- read.delim(my.table.file, header=TRUE,
                         # Some article names have quotes, so if "quote" 
                         # isn't set to "" the table won't load properly
                         quote="", row.names=1, check.names=FALSE)
  my.table[is.na(my.table)] <- 0
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
  # add 10e-32 to smooth zero values
  entro <- 2^(-sum(topic.shares*log(topic.shares+10e-32)))
  return(entro)
}

find.category <- function(vct) {
  # Return name of the column with the max value in given row 
  return(names(which.max(vct)))
}

category.stats <- function(topic.shares.df, language.name) {
  # Not considering "other" as a category or a topic: Other is the last column
  
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

edition.wide.entropy <- function(topic.shares.df) {
  x <- data.frame(apply(topic.shares.df[, 1:16], 1, calc.entropy.per.article),
                  row.names=rownames(topic.shares.df))
  names(x)[1] <- "Entropy"
  return(x)
}


plot.donuts <- function(cat.stats) {
  
  cat.stats <- all.stats
  # plot a category donut chart for each language
  p.en <- plot.category.shares.donut(subset(cat.stats, Language=="English"), "English")
  p.es <- plot.category.shares.donut(subset(cat.stats, Language=="Spanish"), "Spanish")
  p.it <- plot.category.shares.donut(subset(cat.stats, Language=="Italian"), "Italian")
  p.pt <- plot.category.shares.donut(subset(cat.stats, Language=="Portuguese"), "Portuguese")
         
  print(p.en)
  print(p.es)
  print(p.it)
  print(p.pt)
  
  #grid.arrange(p.en, p.es, p.it, p.pt, nrow=2, ncol=2)
  
  return(grid.arrange(p.en, p.es, p.it, p.pt, nrow=2, ncol=2))
}

plot.category.shares.donut <- function(dat, lang) {
  # Plot a donut chart for a language showing the share of each category
  
  # Add additional columns, needed for drawing with geom_rect.
  dat = dat[order(dat$percent.articles), ]
  dat$ymax = cumsum(dat$percent.articles) # end of slices
  dat$ymin = c(0, head(dat$ymax, n=-1)) #  
  
  donut.text <- dat$percent.articles/2 + c(0, cumsum(dat$percent.articles)[-length(dat$percent.articles)])
  donut.text.size <- 7
  
  p <- ggplot(dat, aes(fill=Category, ymax=ymax, ymin=ymin, xmax=4, xmin=3)) +
    geom_rect(colour="grey30") +
    coord_polar(theta="y") +
    xlim(c(0, 4)) +
    scale_fill_grey(start = 0, end = .9) +
    theme_bw() +
    theme(panel.grid=element_blank()) +
    theme(axis.text=element_blank()) +
    theme(axis.ticks=element_blank()) +
    labs(title=lang) +
    geom_text(aes(x=3.5,y=donut.text, # x is between xmax and xmin
                  label=sprintf("%s\n%s%%", Category, percent.articles)), 
              size=donut.text.size)
  
  return(p)
}



### MAIN ####

DATA.DIR <- ""
TOPIC.SHARES.PATH <- paste0(DATA.DIR, "%s-topic-names-50-final-fixed.txt")

## load tables
en.topic.shares <- load.my.table(sprintf(TOPIC.SHARES.PATH, "en"))
es.topic.shares <- load.my.table(sprintf(TOPIC.SHARES.PATH, "es"))
it.topic.shares <- load.my.table(sprintf(TOPIC.SHARES.PATH, "it"))
pt.topic.shares <- load.my.table(sprintf(TOPIC.SHARES.PATH, "pt"))

# TODO: get edition-wide stats for entropy
#par(mfrow=c(2,2))
#boxplot(edition.wide.entropy(en.topic.shares), at=0:2*5+1, 
#        xlim=c(0,5), ylim=range(1, 5.5))
#boxplot(edition.wide.entropy(es.topic.shares), at=0:2*5+2, add=T)
#boxplot(edition.wide.entropy(it.topic.shares), at=0:2*5+3, add=T)
#boxplot(edition.wide.entropy(pt.topic.shares), at=0:2*5+4, add=T)

# get per-category stats
all.stats <- rbind(category.stats(en.topic.shares, "English"),
                   category.stats(es.topic.shares, "Spanish"),
                   category.stats(it.topic.shares, "Italian"),
                   category.stats(pt.topic.shares, "Portuguese"))
# Hack to add missing a row for the missing Royalty category in Spanish
#all.stats <- rbind(all.stats[1:28,], 
#                    c("Royalty", as.numeric(0), as.numeric(0),
#                      as.numeric(0), as.numeric(0), "Spanish"),  
#                    all.stats[29:63,])
#rownames(all.stats) <- seq(64)

print(plot.donuts(all.stats))

exit()
#### Topic distrubtion ####
#TODO:
topic.dist.plot <- topic.distribution.figure(pt.topic.shares, it.topic.shares)
topic.dist.plot <- topic.dist.plot + theme(legend.position="none")
print(topic.dist.plot)

#### Category counts and shares. ###
# TODO: 

#print(plot.category.shares(subset(all.stats, Language=="English")))


# articles.by.cat.plot <- ggplot( all.stats, aes(x=Category, y=percent.articles)) + 
#   geom_bar( aes(fill=Language, width=0.7), alpha=1, position="dodge", stat="identity") +  # adjust positon dodge
#   geom_text( data=all.stats,
#              aes(x=Category, 
#                  y=percent.articles, 
#                  label=percent.articles,
#                  size=12,
#                  hjust=-0.2, # keep the label afar from the bar
#                  vjust=ifelse(Language=="English", 1.2, 0)) ) + # move English label down
#   theme(axis.text.y = element_text(face="bold", colour="#000000", size=16)) + # change axis label font size
#   #theme(legend.position="right") +
#   xlab("") + ylab("% of articles") +
#   coord_flip()
# print(articles.by.cat.plot)

#### Topics by category ####
# topics.by.cat.plot <- ggplot( all.stats, aes(x=Category, y=entropy.mean)) + 
#   geom_bar( aes(fill=Language, width=0.7), alpha=1, position="dodge", stat="identity") +  # adjust positon dodge
#   geom_text( data=all.stats,
#              aes(x=Category, 
#                  y=entropy.mean, 
#                  label=round(entropy.mean,2),
#                  size=12,
#                  hjust=-0.2, # keep the label afar from the bar
#                  vjust=ifelse(Language=="English", 1.2, 0)) ) + # move English label down
#   theme(axis.text.y = element_text(face="bold", colour="#000000", size=16)) + # change axis label font size
#   theme(legend.position="none") +
#   xlab("") + ylab("Number of topics") +
#   coord_flip()
# print(topics.by.cat.plot)
# 
# postscript("articles_by_cat_plot.eps")
# grid.arrange(articles.by.cat.plot, ncol=1, 
#              widths=unit(c(15), "cm"),
#              heights=unit(c(13), "cm") )
# dev.off()
# 
# postscript("topics_by_cat_plot.eps")
# grid.arrange(topics.by.cat.plot, ncol=1, 
#              widths=unit(c(15), "cm"),
#              heights=unit(c(13), "cm") )
# dev.off()
# 
# postscript("topics_dist_plot.eps")
# grid.arrange(topic.dist.plot, ncol=1, 
#              widths=unit(c(13), "cm"),
#              heights=unit(c(13), "cm") )
# dev.off()