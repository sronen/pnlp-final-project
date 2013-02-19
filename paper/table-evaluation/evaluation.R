# Generate confusion matrix for featured articles
# 
# 1) Load table of expected categories for featured article
# 2) Load the table of topics we found for featured artices.
# 3) Find the max topic for each article. 
# 4) Convert Wikipedia topics to our topics.
# 5) Generate matrix

library(ggplot2)

ENG.TOPICS.FILE <- "../../datasets/categories_2013-02-17/en-article-topics-full.txt"
ENG.TOPICS.FA.FILE <- "../../datasets/categories_2013-02-17/en-article-topics-fa.txt"
ENG.FA.LIST <- "../../datasets/wikipedia_bio_lists/top_lists/featured_bios_table_eng.tsv"
SPA.TOPICS.FILE <- "../../datasets/categories_2013-02-17/es-article-topics-full.txt"
SPA.TOPICS.FA.FILE <- "../../datasets/categories_2013-02-17/es-article-topics-fa.txt"
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

find.article.category <- function(article.topic.share.df) {
  ## Given a DF of topic share for articles, find the category of each article.
  # A category is defined as the maximum topic that's not "Other"
  
  # Remove the "Other" topic
  article.topic.share.df$Other <- NULL
  
  # Get maximum non-other topic for each article, and write to a DF
  article.categories.v <- colnames( article.topic.share.df[
    apply(article.topic.share.df, 1, 
          function(x) max(which(x == max(x, na.rm = TRUE))))] )
  
  article.categories.df <- data.frame(article.categories.v, 
                                 row.names=rownames(article.topic.share.df) )
  colnames(article.categories.df)[1] <- "Category"
  # Remove suffixes to category names, as duplicates are allowed.
  article.categories.df$Category <- gsub("\\.(.*)","", article.categories.df$Category)  
  
  return(article.categories.df)
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
  fa.identified.topic.shares <- all.topic.shares[rownames(all.topic.shares) %in% rownames(fa.expected.cats),]
  fa.identified.cats <- find.article.category(fa.identified.topic.shares)
  
  # If there's a mismatch between the number of expected FA and identified FA
  # merge() will handle it
  fa.category.comparison <- merge(fa.expected.cats, fa.identified.cats, by=0)
  cat("FA expected:",nrow(fa.expected.cats),
      ", FA found:",nrow(fa.identified.cats), "\n")
  
  # Update column names
  rownames(fa.category.comparison)=fa.category.comparison$Row.names
  fa.category.comparison$Row.names <- NULL
  names(fa.category.comparison) <- c("Actual", "Predicted")
  
  # convert Wikipedia categories to our categories (refer to mapping table
  # in the paper). Original Wikipedia category stored as ActualOrig.
  the.map <- load.my.table(MAPPING.TABLE)
  
  colnames(fa.category.comparison)[1] <- "ActualOrig" # rename orig...
  fa.category.comparison$Actual <- the.map[match(fa.category.comparison$ActualOrig,
                                                 row.names(the.map)),"Our_Topic"]  
  return(fa.category.comparison)
}
  
visualize.confusion.matrix <- function(comp.data) {
  #### VIZ
  # Now create a confusion matrix for fa.observed.cats and fa.expected.cats
  # FROM http://www.findnwrite.com/musings/visualizing-confusion-matrix-in-r/
  ####
  
  # Hack: rename the categories that are not on Wikipedia so they appear at 
  # the bottom of the matrix -- the diagonal looks nicer.
  comp.data$Predicted[comp.data$Predicted=="Personal"] <- "-Personal"
  comp.data$Predicted[comp.data$Predicted=="Explorers"] <- "-Explorers"
  
  #compute frequency of actual categories
  actual1 <- as.data.frame(table(comp.data$Actual))
  names(actual1) <- c("Actual","ActualFreq")
  
  #build confusion matrix
  confusion1 <- as.data.frame(table(comp.data$Actual, comp.data$Predicted))
  names(confusion1) <- c("Actual","Predicted","Freq")
  
  #calculate percentage of test cases based on actual frequency
  confusion1 <- merge(confusion1, actual1, by=c("Actual"))
  confusion1$Percent <- confusion1$Freq/confusion1$ActualFreq*100
  
  #render plot
  # we use three different layers
  # first we draw tiles and fill color based on percentage of test cases
  tile <- ggplot() +
    geom_tile(aes(x=Actual, y=Predicted,fill=Percent),data=confusion1, color="black",size=0.1) +
    labs(x="Actual",y="Predicted") 
  
  # next we render text values. If you only want to indicate values greater than zero then use data=subset(confusion, Percent > 0)
  tile <- tile +
    geom_text(aes(x=Actual,y=Predicted, label=sprintf("%.1f", Percent)),data=confusion1, size=3, colour="black") +
    scale_fill_gradient(low="grey",high="red")
  
  # lastly we draw diagonal tiles. We use alpha = 0 so as not to hide previous layers but use size=0.3 to highlight border
  tile <- tile +
    geom_tile(aes(x=Actual,y=Predicted),data=subset(confusion1, as.character(Actual)==as.character(Predicted)), color="black",size=0.3, fill="black", alpha=0) 
  
  #render
  return(tile)
}

#### MAIN ####
cat("ENGLISH\n")
eng.comp.data <- generate.comparison.df(ENG.FA.LIST, 
                                        ENG.TOPICS.FILE, 
                                        ENG.TOPICS.FA.FILE)
eng.mat.viz <- visualize.confusion.matrix(eng.comp.data)

par(pty="s")
postscript("eng_confusion_matrix.eps")
print(eng.mat.viz)
dev.off()

cat("SPANISH\n")
spa.comp.data <- generate.comparison.df(SPA.FA.LIST, 
                                        SPA.TOPICS.FILE, 
                                        SPA.TOPICS.FA.FILE)
spa.mat.viz <- visualize.confusion.matrix(spa.comp.data)
postscript("spa_confusion_matrix.eps")
print(spa.mat.viz)
dev.off()
