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

eng.topic.shares <- load.my.table("categories_2013-02-17_final/en-article-topics-full.txt")

# Ward Hierarchical Clustering
d <- dist(sample(mydata, 100), method = "canberra") # distance matrix
fit <- hclust(d, method="ward") 
plot(fit) # display dendogram
groups <- cutree(fit, k=10) # cut tree into 10 clusters
# draw dendogram with red borders around the 10 clusters 
rect.hclust(fit, k=10, border="red")