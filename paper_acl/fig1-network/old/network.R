#### Set working directoy to script directory! ####

library(igraph)

EDGE.THRESHOLD <- 0.02

load.visualize.network <- function(net.file, cat.file, vcolor="cornflowerblue") {
  # Load adjacency matrix
  dat <- read.csv(net.file, sep='\t',header=TRUE,
                  row.names=1, check.names=FALSE) # read .csv file
  row.names(dat) <- gsub("_", " ", row.names(dat)) # clean text
  colnames(dat) <- gsub("_", " ", colnames(dat))
  
  m <- as.matrix(dat)
  
    # Create graph from matix
  graf <- graph.adjacency(m, mode="directed", 
                         weighted=TRUE, diag=FALSE)
  # Remove "Other" category
  graf <- delete.vertices(graf, "Other")
  
  # Load category count
  cat.count <- read.csv(cat.file, sep='\t', header=TRUE,
                        row.names=1, check.names=FALSE) # read .csv file
  # Remove "Other" and "TOTAL"
  cat.count <- subset(cat.count, row.names(cat.count)!="TOTAL")
  cat.count <- subset(cat.count, row.names(cat.count)!="Other")
  
  # Remove edges under given weight
  bad.edges <- E(graf)[E(graf)$weight<EDGE.THRESHOLD]
  good.graf <- delete.edges(graf, bad.edges)
  
  ewidth <- 70*(E(good.graf)$weight)
  vsize <- log10(cat.count$Num_articles*0.05)*12
  
  # For the pie vertices:
  # Find the average share of the category (=most prominent topic) among
  # article in that category, and its complement to 1.
  shares.of.max.topics <- lapply( dat, function(x) c(max(x), 1-max(x)) ) #, 1-max(x)) )
  print(net.file)
  print(shares.of.max.topics)
  
  plot(good.graf,
       #vertex.label = paste(as.character(V(graf)$name), "\n", cat.count$Num_articles),
       vertex.label = paste(as.character(V(graf)$name)),
       vertex.label.family = "Times",
       vertex.label.font = 2,
       vertex.label.cex = log10(vsize), # continuous
       #vertex.frame.color = NA, # no frames at all
       vertex.size = vsize,
  
       vertex.shape="pie",
       vertex.pie=shares.of.max.topics,
       vertex.pie.color=list(c(vcolor, "white")),
    
       edge.color = rgb(.1, .1, .1, ewidth/12),
       edge.width = ewidth, # discrete values     
       edge.arrow.size = ewidth*0.4,
       edge.curved = 0.2, # to show reciprocal edges
  )
} 

#### MAIN ####

svg("english_topic_network2.svg")
par(oma=c(0,0,0,0), mar=c(0,0,0,0))
load.visualize.network("en_network_matrix.txt", "en_category_count.txt", vcolor="lightblue1")
dev.off()

svg("spanish_topic_network2.svg")
load.visualize.network("es_network_matrix.txt", "es_category_count.txt", vcolor="darksalmon")
dev.off()