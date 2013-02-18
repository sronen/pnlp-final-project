library(reshape)
library(ggplot2)

postscript("avg_topic_compo.eps")

# Load DF and assign rownames
eng.topic.df <- read.csv("outfile_en.txt", sep = "\t", header=T)
rownames(eng.topic.df) <- eng.topic.df[,1]
eng.topic.df[,1] <- NULL

spa.topic.df <- read.csv("outfile_es.txt", sep = "\t", header=T)
rownames(spa.topic.df) <- spa.topic.df[,1]
spa.topic.df[,1] <- NULL

# Merge
topic.aggr <- data.frame( colnames(eng.topic.df), 
                         colMeans(eng.topic.df)*100, # for percentage 
                         colMeans(spa.topic.df*100) )
colnames(topic.aggr) <- c("Topic", "English", "Spanish")
topic.aggr$Topic <- gsub("_", " ", topic.aggr$Topic) # remove underscores

# df <- read.table(text = "       Input Rtime Rcost Rsolutions  Btime Bcost 
# 1   12-proc.     1    36     614425     40    36 
# 2   15-proc.     1    51     534037     50    51 
# 3    18-proc     5    62    1843820     66    66 
# 4    20-proc     4    68    1645581 104400    73 
# 5 20-proc(l)     4    64    1658509  14400    65 
# 6    21-proc    10    78    3923623 453600    82",header = TRUE,sep = "")

dfm <- melt(topic.aggr[,c('Topic','English','Spanish')],id.vars = 1)
colnames(dfm) <- c('Topic', 'Language', 'Percentage')

p <- ggplot( dfm, aes(x=Topic, y=Percentage)) + 
  geom_bar( aes(fill=Language, width=0.7), position="dodge", stat="identity") +  # adjust poisiton dodge
  geom_text( data=dfm,
             aes(x=Topic, 
                 y=Percentage, 
                 label=round(Percentage,1),
                 hjust=-0.2, # keep the label afar from the bar
                 vjust=ifelse(Language=="English", 1.2, 0)) ) + # move English label down
  theme(axis.text.y = element_text(face="bold", colour="#000000", size=16)) + # change axis label font size
  coord_flip()
print(p)

dev.off()