# Compare language detection stats

setwd("~/Development/pnlp-final-project/viz/matrices/")

person.name = "Frank Zappa" # Phil Hartman, Honoré de Balzac, William McKinley

# Get topic scores for this person in the three langs
# into a single matrix
person.df = eng[person.name, ]
person.df = rbind( person.df, fra[person.name, ])
person.df = rbind( person.df, spa[person.name, ])
row.names(person.df) <- c("English", "French", "Spanish")
person.matrix = data.matrix(person.df)

# now visualize it
heatmap.2( person.matrix, Rowv=FALSE, Colv=FALSE, dendrogram="none", 
           col=cm.colors, main=person.name, xlab=person.name,
           cellnote=person.matrix, notecol="black", trace="none", 
           key=TRUE, margins=c(10,10),
           lwid = c(.01,.99),lhei = c(.01,.99))