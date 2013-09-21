library(reshape)
library(gridExtra)
library(ggplot2)

print.data.frame <- function(m){
  write.table(format(m, justify="right"),
              row.names=F, col.names=F, quote=F)
}


compare.shares <- function(article.name) {
  cat("Lang ")
  print(colnames(en.tshares)) # print titles
  cat("English ")
  print(en.tshares[row.names(en.tshares)==article.name,])
  cat("Spanish ")
  print(es.tshares[row.names(es.tshares)==article.name,])
  cat("Italian ")
  print(it.tshares[row.names(it.tshares)==article.name,])
  cat("Portuguese ")
  print(pt.tshares[row.names(pt.tshares)==article.name,])
}

compare.shares("Lionel_Messi")
compare.shares("David_Beckham")
compare.shares("Carla_Bruni")
compare.shares("Tiger_Woods")

plot.person.donuts <- function(person.name,
                        en.shares,es.shares,
                        it.shares,pt.shares) {
  # plot a category donut chart for each language
  
  # convert the format and plot
  en.article <- melt(en.tshares[row.names(en.tshares)==person.name,])
  names(en.article) <- c("category", "percent.articles")
  p.en <- plot.category.shares.donut(en.article, "English")
  
  es.article <- melt(es.tshares[row.names(es.tshares)==person.name,])
  names(es.article) <- c("category", "percent.articles")
  p.es <- plot.category.shares.donut(es.article, "Spanish")
  
  it.article <- melt(it.tshares[row.names(it.tshares)==person.name,])
  names(it.article) <- c("category", "percent.articles")
  p.it <- plot.category.shares.donut(it.article, "Italian")
  
  pt.article <- melt(pt.tshares[row.names(pt.tshares)==person.name,])
  names(pt.article) <- c("category", "percent.articles")
  p.pt <- plot.category.shares.donut(pt.article, "Portuguese")
  
  return(grid.arrange(p.en, p.es, p.it, p.pt, nrow=2, ncol=2))
}

plot.article.shares.donut <- function(orig.dat, lang) {
  # Plot a donut chart for a language showing the share of each category
  
  # Add additional columns, needed for drawing with geom_rect.
  dat <- orig.dat[,order(orig.dat, decreasing=T)]
  dat$ymax = sum(dat) # end of slices, will be 1 if shares for all categories are listed
  dat$ymin = c(0, head(dat$ymax, n=-1)) #  
  
  donut.text <- dat[1:17]/2 #+ c(0, sum(dat)[-length(dat)])
  donut.text.size <- dat[1:17] * 0.5 # 3 # make it small for easier post-processing
  
  print(donut.text)
  print(colnames(dat)[1:17])
  
  # environment() helps pass variables for geom_text labels,
  # see http://stackoverflow.com/questions/15429447/why-does-my-user-supplied-label-in-geom-text-in-ggplot2-generate-an-error
  
  p <- ggplot(dat, aes(as.numeric(dat), fill=colnames(dat)[1:17]),  
    #ggplot(dat, aes(fill=colnames(dat)[1:17], ymax=ymax, ymin=ymin, xmax=4, xmin=3), 
              environment = environment() ) +
    #geom_rect(colour="grey30") +
    geom_bar() +
    #coord_polar(theta="y") +
    #xlim(c(0, 4)) +
    #scale_fill_grey(start = 0, end = .9) +
    #geom_text(aes(x=3.5,y=donut.text, # x is between xmax and xmin
    #              label=sprintf("%s\n%s%%", colnames(dat[1:17]), dat[1:17])), 
    #          size=donut.text.size) +
    labs(title=lang) +
    theme_bw() +
    theme(panel.grid=element_blank()) +
    theme(axis.text=element_blank()) +
    theme(axis.ticks=element_blank()) #+
    #theme(legend.position="none")
  return(p)
}

en.tshares <- read.delim("../datasets/topic-names-final/en-topic-names-50-final-fixed.txt",
                         quote="", comment.char="", row.names=1)

es.tshares <- read.delim("../datasets/topic-names-final/es-topic-names-50-final-fixed.txt",
                         quote="", comment.char="", row.names=1)

it.tshares <- read.delim("../datasets/topic-names-final/it-topic-names-50-final-fixed.txt",
                         quote="", comment.char="", row.names=1)

pt.tshares <- read.delim("../datasets/topic-names-final/pt-topic-names-50-final-fixed.txt",
                         quote="", comment.char="", row.names=1)

exit()
#### Donut plots per person
plot.person.donuts(en.tshares, es.tshares, it.tshares, pt.tshares, "Barack_Obama")


en.edited <- subset(en.article.stats, num.uniq.eds>=100)
en.top <- head(en.edited[order(en.edited$rev.per.day, decreasing=T),
                       c("name", "num.revs", "num.uniq.eds", "rev.per.day", "category")], 10)
 
it.edited <- subset(it.article.stats, num.uniq.eds>=100)
it.top <- head(it.edited[order(it.edited$rev.per.day, decreasing=T),
                       c("name", "num.revs", "num.uniq.eds", "rev.per.day", "category")], 10)

pt.edited <- subset(pt.article.stats, num.uniq.eds>=100)
pt.top <- head(pt.edited[order(pt.edited$rev.per.day, decreasing=T),
                       c("name", "num.revs", "num.uniq.eds", "rev.per.day", "category")], 10)


# en.tshares[row.names(en.tshares)=="Lionel_Messi",]
# 
# en.tshares[row.names(en.tshares)=="Tiger_Woods",]
# 
# colMeans(en.tshares)
# 
# 
# 
# old.network <- read.delim("../../paper_acl/fig1-network/en_network_edgelist.txt")
# 
# new.network <- read.delim("../../paper_cscw/network/en_network_edgelist.txt")
# 
# sum(subset(old.network, subset=tgt=="Sports", select=c("weight")))
# 
# sum(subset(new.network, subset=tgt=="Sports", select=c("weight")))



