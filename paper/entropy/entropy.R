# English entropy: 2.714043
# Spanish entropy: 2.662469

# Entropy equation for latex:

#\usepackage{amsmath}
#\usepackage{relsize}

#\begin{equation}
#\frac{1}{|A|} \mathlarger{\sum\limits_{i\in{A}} 2^{-\sum\limits_{c\in{C}} p(c)log_{2}(c)}}
#\end{equation}

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

eng.topic.shares <- load.my.table("../../datasets/categories_2013-02-17/en-article-topics-full.txt")
eng.entro <- calc.entropy(eng.topic.shares)

spa.topic.shares <- load.my.table("../../datasets/categories_2013-02-17/es-article-topics-full.txt")
spa.entro <- calc.entropy(spa.topic.shares)

cat("English entropy:", eng.entro, "\n")
cat("Spanish entropy:", spa.entro, "\n")
