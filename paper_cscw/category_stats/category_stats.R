source('../../datasets/prep_data.R', chdir=T)

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
  # plot a category donut chart for each language
  p.en <- plot.category.shares.donut(subset(cat.stats, Language=="English"), "English")
  p.es <- plot.category.shares.donut(subset(cat.stats, Language=="Spanish"), "Spanish")
  p.it <- plot.category.shares.donut(subset(cat.stats, Language=="Italian"), "Italian")
  p.pt <- plot.category.shares.donut(subset(cat.stats, Language=="Portuguese"), "Portuguese")
  
  return(grid.arrange(p.en, p.es, p.it, p.pt, nrow=2, ncol=2))
}

plot.category.shares.donut <- function(dat, lang) {
  # Plot a donut chart for a language showing the share of each category
  print(head(dat))
  
  # Add additional columns, needed for drawing with geom_rect.
  dat = dat[order(dat$percent.articles), ]
  dat$ymax = cumsum(dat$percent.articles) # end of slices
  dat$ymin = c(0, head(dat$ymax, n=-1)) #  
  
  donut.text <- dat$percent.articles/2 + c(0, cumsum(dat$percent.articles)[-length(dat$percent.articles)])
  donut.text.size <- dat$percent.articles * 0.5 # 3 # make it small for easier post-processing
  
  # environment() helps pass variables for geom_text labels,
  # see http://stackoverflow.com/questions/15429447/why-does-my-user-supplied-label-in-geom-text-in-ggplot2-generate-an-error
  
  p <- ggplot(dat, aes(fill=category, ymax=ymax, ymin=ymin, xmax=4, xmin=3), 
              environment = environment() ) +
    geom_rect(colour="grey30") +
    coord_polar(theta="y") +
    xlim(c(0, 4)) +
    #scale_fill_grey(start = 0, end = .9) +
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

## Category shares
en.cat.stats <- prep.category.stats.table(en.article.stats, "English")
es.cat.stats <- prep.category.stats.table(es.article.stats, "Spanish")
it.cat.stats <- prep.category.stats.table(it.article.stats, "Italian")
pt.cat.stats <- prep.category.stats.table(pt.article.stats, "Portuguese")

all.cat.stats <- rbind(en.cat.stats, es.cat.stats,
                   it.cat.stats, pt.cat.stats)

postscript("category_share_comparison.eps", height=900, width=900)
plot.donuts(all.cat.stats)
dev.off()
exit()

#### Topic diversity by category ####
# Todo: nicer viz (x16) as Deepak suggested.
topics.by.cat.plot <- ggplot( all.cat.stats, aes(x=category, y=entropy.mean)) + 
  geom_bar( aes(fill=Language, width=0.7), alpha=1, position="dodge", stat="identity") +  # adjust positon dodge
  #   geom_text( data=all.cat.stats,
  #              aes(x=category, 
  #                  y=entropy.mean, 
  #                  label=round(entropy.mean,2),
  #                  size=12,
  #                  hjust=-0.2, # keep the label afar from the bar
  #                  vjust=ifelse(Language=="English", 1.2, 0)) ) + # move English label down
  theme(axis.text.y = element_text(face="bold", colour="#000000", size=16)) + # change axis label font size
  #theme(legend.position="none") +
  xlab("") + ylab("Number of topics") +
  coord_flip()
print(topics.by.cat.plot)

