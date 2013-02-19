# Set working directoy to script directory!

data.frame.fold <- function(filename) {
  print(filename)
  # Start a dataframe for results of given fold, replace NA with 0
  my.fold <- read.csv(filename, sep='\t',header=TRUE,
                    row.names=1, check.names=FALSE) # read .csv file
  my.fold[is.na(my.fold)] <- 0
  return(my.fold)
}

data.frame.run <- function(filenames) {
  # Given files with the results of three folds, 
  # loads them, binds them into one DF, and sorts it
  fold1 <- data.frame.fold(filenames[1])
  fold2 <- data.frame.fold(filenames[2])
  fold3 <- data.frame.fold(filenames[3])
  my.run <- rbind(fold1, fold2, fold3)
#   my.run <- fold1 # Hack for FA
  return(my.run[order(row.names(my.run)), ])
}

write.full.article.topics.talbe <- function(input.dir, output.file) {
  ### combine results from all folds, and average results across runs 
  setwd(input.dir)
  
  my.files <- list.files(pattern="*.txt")
  
  # In each run, articles are distributed differently between the folds,
  # So need to bind the folders before comaparing them. This is done by
  # data.frame.run
  run1 <- data.frame.run(my.files[1:3])
  run2 <- data.frame.run(my.files[4:6])
  run3 <- data.frame.run(my.files[7:9])
#   run1 <- data.frame.run(my.files[1]) # hack for FA
#   run2 <- data.frame.run(my.files[2])
#   run3 <- data.frame.run(my.files[3])
  
  if ( all(rownames(run1)==rownames(run2))
       & all(rownames(run2)==rownames(run3)) ) {
    print("Article vectors are equal across runs!")
  } else {
    print("Check article lists -- they're not equal")
  }
  
  # Average results
  all.runs <- (run1 + run2 + run3) /3
  
  setwd(INIT.DIR)
  write.table(all.runs, output.file, 
             row.names=T, 
             col.names=NA, # convention for leaving header of first title empty
             sep='\t', quote=F)
  print("DONE!")
  return(all.runs)
}

### MAIN ####
INIT.DIR <- getwd()
eng.final <- write.full.article.topics.talbe("en-topic-prop-names/", "en-article-topics-full.txt")
spa.final <- write.full.article.topics.talbe("es-topic-prop-names/", "es-article-topics-full.txt")

# For FA
#eng.final <- write.full.article.topics.talbe("en-topic-prop-names/en-fa/", "en-article-topics-fa.txt")
#spa.final <- write.full.article.topics.talbe("es-topic-prop-names/es-fa/", "es-article-topics-fa.txt")