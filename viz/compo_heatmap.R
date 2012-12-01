# Compare language detection stats

setwd("~/Development/pnlp-final-project/viz/matrices/")

# load data
eng <- read.csv("human-en-matrix.txt", sep="\t")
spa <- read.csv("human-es-matrix.txt", sep="\t")
fra <- read.csv("human-fr-matrix.txt", sep="\t")

#### eng ####

# name row by person
row.names(eng) <- eng$Name
eng <- eng[,2:ncol(eng)] # get rid of first col

# merge categories, drop unnecessary
eng$sports <- eng$cricket + eng$sports
eng$cricket <- NULL
eng$royalty.religion <- eng$royalty + eng$church.royalty
eng$church.royalty <- NULL
eng$royalty <- NULL

#### fra ####

# name row by person
row.names(fra) <- fra$Name
fra <- fra[,2:ncol(fra)] # get rid of first col

# merge categories, rename, drop
names(fra)[2] <- "literature" # rename literature...other
names(fra)[4] <- "family" # rename family...life
fra$music <- fra$music + fra$orchestra
fra$orchestra <- NULL
fra$royalty.religion <- fra$royalty + fra$church.royalty
fra$royalty <- NULL
fra$church.royalty <- NULL

#### spa ####

# name row by person
row.names(spa) <- spa$Name
spa <- spa[,2:ncol(spa)] # get rid of first col

# merge categories, rename, drop unnecessary
names(spa)[5] <- "military" # rename war.ancient
names(spa)[10] <- "politics" # rename politics.art
spa$music <- spa$music.orchestra + spa$music.rock
spa$music.orchestra <- NULL
spa$music.rock <- NULL

spa$royalty.religion <- spa$royalty + spa$empire.religion
spa$royalty <- NULL
spa$empire.religion <- NULL

#### select common columns ####
common.cols = Reduce(intersect, list(colnames(eng),colnames(fra),colnames(spa)))
# [1] "literature"       "family"           "music"           
# [4] "politics"         "military"         "royalty.religion"
eng <- subset(eng, select = common.cols)
fra <- subset(fra, select = common.cols)
spa <- subset(spa, select = common.cols)

#### select common rows ####
common.rows = Reduce(intersect, list(rownames(eng),rownames(fra),rownames(spa)))
eng <- eng[rownames(eng) %in% common.rows, ]
eng <- eng[order(rownames(eng)), ]
fra <- fra[rownames(fra) %in% common.rows, ]
fra <- fra[order(rownames(fra)), ]
spa <- spa[rownames(spa) %in% common.rows, ]
spa <- spa[order(rownames(spa)), ]

#### heatmaps ####
# Following:
# http://flowingdata.com/2010/01/21/how-to-make-a-heatmap-a-quick-and-easy-solution/

par(mar = rep(2, 4))
eng_matrix <- data.matrix(eng)
eng_heatmap <- heatmap(eng_matrix[100:120,], Rowv=NA, Colv=NA, 
  col = cm.colors(16), scale="column", margins=c(5,10), main="English")

fra_matrix <- data.matrix(fra)
fra_heatmap <- heatmap(fra_matrix[100:120,], Rowv=NA, Colv=NA, 
  col = cm.colors(16), scale="column", margins=c(5,10), main="French")

spa_matrix <- data.matrix(spa)
spa_heatmap <- heatmap(spa_matrix[100:120,], Rowv=NA, Colv=NA, 
  col = cm.colors(16), scale="column", margins=c(5,10), main="Spanish")

#### aggregates ####
means.matrix <- matrix( c(round(colMeans(eng),2), 
                          round(colMeans(fra),2),
                          round(colMeans(spa),2) ),
                        nrow = 3, ncol=6, byrow=TRUE,
                        dimnames = list(c("English", "French", "Spanish"), 
                                        colnames(eng)) )
svg('means_all.svg')
means.heatmap <- heatmap(means.matrix, Rowv=NA, Colv=NA, 
  col = cm.colors(16), scale="column", margins=c(5,10), main="Means")
dev.off()

library(gplots)
#svg('means_all_values.svg')
heatmap.2( means.matrix, Rowv=FALSE, Colv=FALSE, dendrogram="none", 
           col=cm.colors,
           cellnote=means.matrix, notecol="black", trace="none", 
           key=TRUE, margins=c(10,10),
           lwid = c(.01,.99),lhei = c(.01,.99))
#dev.off()
