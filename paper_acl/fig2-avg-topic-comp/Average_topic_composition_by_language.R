# Bar chart - figure 1
library(ggplot2)

# Load DF and assign rownames
eng.topic.df <- read.csv("outfile_en.txt", sep = "\t", header=T)
rownames(eng.topic.df) <- eng.topic.df[,1]
eng.topic.df[,1] <- NULL

spa.topic.df <- read.csv("outfile_es.txt", sep = "\t", header=T)
rownames(spa.topic.df) <- spa.topic.df[,1]
spa.topic.df[,1] <- NULL

# Create data frame for language and give columns standard names
# Rows are categories, column are mean, STDev, and language indicator
topic.aggr.eng <- data.frame(colMeans(eng.topic.df), 
                             sapply(eng.topic.df, sd), 
                             "eng", # language name
                             row.names = colnames(eng.topic.df))
colnames(topic.aggr.eng) <- c("mean", "stdev", "lang")

topic.aggr.spa <- data.frame(colMeans(spa.topic.df), 
                             sapply(spa.topic.df, sd), 
                             "spa", # language name
                             row.names = colnames(spa.topic.df))
colnames(topic.aggr.spa) <- c("mean", "stdev", "lang")

# Now merge!
topic.aggr <- rbind(topic.aggr.eng, topic.aggr.spa)
print(topic.aggr)

p <- ggplot(topic.aggr, aes(x=row.names, y=value, fill=lang)) + 
  geom_bar(stat = "identity") +
  coord_flip()
print(p)

#ggplot(all.table, aes(avg))
# 
# p <- ggplot(, aes(x=indeps, y=deps, label=labels)) +
#   geom_point(aes(size=sizes, color=colors)) +
#   geom_smooth(method="lm", se=FALSE) #+
# geom_text(size=3)