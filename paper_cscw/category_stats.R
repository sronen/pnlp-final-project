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


prep.category.stats.table <- function(topics.df, language.name) {
  # Find the entropy mean+sd, num articles, and % article for each category
  cat.stats <- ddply(topics.df[,c("category","num.topics")], 'category', .progress = "text", 
                     function(x) c(num.articles=nrow(x), 
                                   percent.articles=round(nrow(x)/nrow(topics.df)*100,1),
                                   entropy.mean=mean(x$num.topics),
                                   entropy.sd=sd(x$num.topics)) )
  cat.stats$Language <- language.name # Makes it easier to merge and plot in ggplot
  
  return(cat.stats)
}

plot.donuts <- function(cat.stats) {
  cat.stats <- all.stats
  # plot a category donut chart for each language
  p.en <- plot.category.shares.donut(subset(cat.stats, Language=="English"), "English")
  p.es <- plot.category.shares.donut(subset(cat.stats, Language=="Spanish"), "Spanish")
  p.it <- plot.category.shares.donut(subset(cat.stats, Language=="Italian"), "Italian")
  p.pt <- plot.category.shares.donut(subset(cat.stats, Language=="Portuguese"), "Portuguese")
  
  return(grid.arrange(p.en, p.es, p.it, p.pt, nrow=2, ncol=2))
}

plot.category.shares.donut <- function(dat, lang) {
  # Plot a donut chart for a language showing the share of each category
  
  # Add additional columns, needed for drawing with geom_rect.
  dat = dat[order(dat$percent.articles), ]
  dat$ymax = cumsum(dat$percent.articles) # end of slices
  dat$ymin = c(0, head(dat$ymax, n=-1)) #  
  
  donut.text <- dat$percent.articles/2 + c(0, cumsum(dat$percent.articles)[-length(dat$percent.articles)])
  donut.text.size <- 3 # make it small for easier post-processing
  
  # environment() helps pass variables for geom_text labels,
  # see http://stackoverflow.com/questions/15429447/why-does-my-user-supplied-label-in-geom-text-in-ggplot2-generate-an-error
  
  p <- ggplot(dat, aes(fill=category, ymax=ymax, ymin=ymin, xmax=4, xmin=3), 
              environment = environment() ) +
    geom_rect(colour="grey30") +
    coord_polar(theta="y") +
    xlim(c(0, 4)) +
    scale_fill_grey(start = 0, end = .9) +
    geom_text(aes(x=3.5,y=donut.text, # x is between xmax and xmin
                  label=sprintf("%s\n%s%%", category, percent.articles)), 
              size=donut.text.size) +
    labs(title=lang) +
    theme_bw() +
    theme(panel.grid=element_blank()) +
    theme(axis.text=element_blank()) +
    theme(axis.ticks=element_blank()) +
    theme(legend.position="none")
  return(p)
}


### MAIN ####
# source('../datasets/prep_data.R', chdir=T)

en.cat.stats <- prep.category.stats.table(en.article.stats, "English")
es.cat.stats <- prep.category.stats.table(es.article.stats, "Spanish")
it.cat.stats <- prep.category.stats.table(it.article.stats, "Italian")
pt.cat.stats <- prep.category.stats.table(pt.article.stats, "Portuguese")

all.stats <- rbind(en.cat.stats, es.cat.stats,
                   it.cat.stats, pt.cat.stats)

postscript("category_share_comparison.eps")
plot.donuts(all.stats)
dev.off()

## load tables
# en.topic.shares <- load.my.table(sprintf(TOPIC.SHARES.TBL.PATH, "en"))
# es.topic.shares <- load.my.table(sprintf(TOPIC.SHARES.TBL.PATH, "es"))
# it.topic.shares <- load.my.table(sprintf(TOPIC.SHARES.TBL.PATH, "it"))
# pt.topic.shares <- load.my.table(sprintf(TOPIC.SHARES.TBL.PATH, "pt"))
# get per-category stats
# all.stats <- rbind(category.stats(en.topic.shares, "English"),
#                    category.stats(es.topic.shares, "Spanish"),
#                    category.stats(it.topic.shares, "Italian"),
#                    category.stats(pt.topic.shares, "Portuguese"))



# TODO: get edition-wide stats for entropy
#par(mfrow=c(2,2))
#boxplot(edition.wide.entropy(en.topic.shares), at=0:2*5+1, 
#        xlim=c(0,5), ylim=range(1, 5.5))
#boxplot(edition.wide.entropy(es.topic.shares), at=0:2*5+2, add=T)
#boxplot(edition.wide.entropy(it.topic.shares), at=0:2*5+3, add=T)
#boxplot(edition.wide.entropy(pt.topic.shares), at=0:2*5+4, add=T)

# Hack to add missing a row for the missing Royalty category in Spanish
#all.stats <- rbind(all.stats[1:28,], 
#                    c("Royalty", as.numeric(0), as.numeric(0),
#                      as.numeric(0), as.numeric(0), "Spanish"),  
#                    all.stats[29:63,])
#rownames(all.stats) <- seq(64)


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