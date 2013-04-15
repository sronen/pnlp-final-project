library(reshape2)
library(ggplot2)

setwd("~/Development/pnlp-final-project/datasets/")

load.my.table <- function(my.table.file) {
  # change some of the default arguments for read.csv
  my.table <- read.csv(my.table.file,
                       sep='\t',header=TRUE,
                       quote="", # Some article names have quotes, so if "quote" 
                       # isn't set to "" the table won't load properly
                       row.names=1, check.names=FALSE)
  return(my.table)
}

#http://www.statmethods.net/advstats/cluster.html

name.max <- function(vct) {
  # Return name of the column with the max value in given row 
  return(names(which.max(vct)))
}


eng.topic.shares <- load.my.table("categories_2013-02-17_final/en-article-topics-full.txt")
mydata <- eng.topic.shares[1:100,] #head(eng.topic.shares, 20000)

# Model Based Clustering
library(mclust)
fit <- Mclust(mydata)
plot(fit, mydata) # plot results 
print(fit) # display the best model

# Ward Hierarchical Clustering
d <- dist(mydata, method = "euclidean") # distance matrix
fit <- hclust(d, method="ward") 
#plot(fit) # display dendogram
groups <- cutree(fit, k=10) # cut tree into 10 clusters

# draw dendogram with red borders around the 10 clusters 
#rect.hclust(fit, k=10, border="red")



# add cluster and category info
mydata$category <- apply(mydata[, 1:17], 1, name.max)
temp <- as.data.frame(groups)
names(temp) <- "cluster" # rename column
mydata <- merge(mydata, temp, by="row.names")
rm(temp)

# contingency table from cross-classifying factors
mat <- melt(xtabs( ~ category + cluster, mydata))
# hack to convert to matrix..
#attr(mat, "class") <- NULL
#attr(mat, "call") <- NULL

tile <- ggplot() +
  geom_tile(aes(x=as.character(category), 
                   y=as.character(cluster),
                   fill=value),
               data=mat, color="black",size=0.1) +
  labs(x="Category",y="Cluster")

tile <- tile +
  geom_text(aes(x=as.character(category),y=as.character(cluster),
                label=value),
            data=mat, size=5, fontface="bold", colour="black") +
  scale_fill_gradient(low="grey97",high="red")

base_size <- 10
tile <- tile + theme_grey(base_size = base_size) + 
  #labs(x = "", y = "") +
  scale_x_discrete(expand = c(0, 0)) +
  scale_y_discrete(expand = c(0, 0)) +
  theme(text = element_text(size = base_size *2),
        axis.ticks = element_blank(), 
        axis.text.x = element_text(angle = 90, hjust=0, vjust = 0.2, colour = "grey50"),
        axis.text.y = element_text(colour = "grey50"))
print(tile)


#p <- ggplot(mat, aes(x=cat.name,y=groups, fill=value))
#print(p)
