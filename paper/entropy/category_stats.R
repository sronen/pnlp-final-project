# English entropy: 2.714043
# Spanish entropy: 2.662469

# Entropy equation for latex:

#\usepackage{amsmath}
#\usepackage{relsize}

#\begin{equation}
#\frac{1}{|A|} \mathlarger{\sum\limits_{i\in{A}} 2^{-\sum\limits_{c\in{C}} p(c)log_{2}(c)}}
#\end{equation}

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

calc.entropy <- function(topic.shares) {
  # Find entropy per article
  
  entro <- sum(2^(-rowSums(topic.shares*log(topic.shares)))) / nrow(topic.shares)
  return(entro)
}

calc.entropy.per.article <- function(topic.shares) {
  
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
  
  library(plyr)
  cat.stats <- ddply(x, 'Category', .progress = "text", 
                     function(x) c(num.articles=nrow(x), 
                                   percent.articles=round(nrow(x)/total.articles*100,1),
                                   entropy.mean=mean(x$Entropy),
                                   entropy.sd=sd(x$Entropy)) )
  cat.stats$Language <- language.name # Makes it easier to merge and plot in ggplot
  return(cat.stats)
}

#eng.topic.shares <- load.my.table(paste(DATA.DIR, "en-article-topics-fa.txt", sep=""))
#save(eng.fa.stats <- category.stats(eng.topic.shares)
#sum(eng.fa.stats$count*eng.fa.stats$entropy.mean)/sum(eng.fa.stats$count)
#print(eng.fa.stats)

eng.topic.shares <- load.my.table(paste(DATA.DIR, "en-article-topics-full.txt", sep=""))
eng.stats <- category.stats(eng.topic.shares, language.name="English")
print(sum(eng.stats$count*eng.stats$entropy.mean)/sum(eng.stats$count))
print(eng.stats)

spa.topic.shares <- load.my.table(paste(DATA.DIR, "es-article-topics-full.txt", sep=""))
spa.stats <- category.stats(spa.topic.shares, language.name="Spanish")
print(sum(spa.stats$count*spa.stats$entropy.mean)/sum(spa.stats$count))
print(spa.stats)

all.stats <- rbind(eng.stats, spa.stats)

p <- ggplot( all.stats, aes(x=reorder(Category,blah), y=num.articles)) + 
  geom_bar( aes(fill=Language, width=0.7), position="dodge", stat="identity") +  # adjust poisiton dodge
  geom_text( data=all.stats,
             aes(x=Category, 
                 y=num.articles, 
                 label=num.articles,
                 hjust=-0.2, # keep the label afar from the bar
                 vjust=ifelse(Language=="English", 1.2, 0)) ) + # move English label down
  theme(axis.text.y = element_text(face="bold", colour="#000000", size=16)) + # change axis label font size
  coord_flip()
print(p)


# ggplot(eng.stats, aes(y=num.articles, x=reorder(Category,Language,num.articles))) + 
#   geom_bar( aes(fill=Language, width=0.7), position="dodge", stat="identity")  # adjust poisiton dodge
# 
# 
ggplot(eng.stats, aes(y=num.articles, x=reorder(Category,num.articles))) + 
  geom_bar(width=0.5, stat="identity", fill="red", alpha=0.1) + # adjust position dodge
  geom_bar(data=spa.stats, aes(x=reorder(Category,eng.stats$num.articles), y=num.articles), 
           position=position_dodge(width=2), 
           width=0.5, stat="identity", fill="blue", alpha=0.1) + # adjust position dodge
  geom_text( data=all.stats,
           aes(x=Category, 
               y=num.articles, 
               label=num.articles,
               hjust=-0.2, # keep the label afar from the bar
               vjust=ifelse(Language=="English", 1.2, 0)) ) + # move English label down
  theme(axis.text.y = element_text(face="bold", colour="#000000", size=16)) + # change axis label font size
  coord_flip()
