
data.frame.fold <- function(filename) {
  print(filename)
  # Start a dataframe for results of given fold, replace NA with 0
  my.fold <- read.csv(filename, sep='\t',header=TRUE,
                    row.names=1, check.names=FALSE) # read .csv file
  my.fold[is.na(my.fold)] <- 0
  return(my.fold)
}

data.frame.run.dups <- function(filenames) {
  # Given files with the results of three folds, 
  # loads them, binds them into one DF, and sorts it
  fold1 <- data.frame.fold(filenames[1])
  fold2 <- data.frame.fold(filenames[2])
  
  # remove duplicates, because apparently we have them!
  duprows <- rownames(fold2) %in% rownames(fold1)
  my.run <- rbind(fold1, fold2[!duprows,])
  
  fold3 <- data.frame.fold(filenames[3])
  
  # and again...
  duprows <- rownames(fold3) %in% rownames(my.run)
  my.run <- rbind(my.run, fold3[!duprows,])
  
  return(my.run[order(row.names(my.run)), ])
}

data.frame.run <- function(filenames) {
  # Given files with the results of three folds, 
  # loads them, binds them into one DF, and sorts it
  fold1 <- data.frame.fold(filenames[1])
  fold2 <- data.frame.fold(filenames[2])
  fold3 <- data.frame.fold(filenames[3])
  my.run <- rbind(fold1, fold2, fold3)
  return(my.run[order(row.names(my.run)), ])
}


main <- function(dir.name, output.filename) {
  sink()
  initial.dir <- getwd()
  setwd(dir.name)
  my.files <- list.files(pattern="*.txt")
  
  # In each run, articles are distributed differently between the folds,
  # So need to bind the folders before comaparing them. This is done by
  # data.frame.run
  run1 <- data.frame.run(my.files[1:3])
  run2 <- data.frame.run(my.files[4:6])
  run3 <- data.frame.run(my.files[7:9])
  
  if ( all(rownames(run1)==rownames(run2))
       & all(rownames(run2)==rownames(run3)) ) {
    print("Article vectors are equal across runs!")
  } else {
    print("Check article lists -- they're not equal")
  }
  
  # Average results
  all.runs <- (run1 + run2 + run3) /3
  
  setwd(initial.dir)
  write.table(all.runs, output.filename, 
             row.names=T, 
             col.names=NA, # convention for leaving header of first title empty
             sep='\t', quote=F)
}

args <- commandArgs(trailingOnly = TRUE)
print(args)
main(dir.name="es-topic-prop-names/", output.filename="es-article-topics-full2.txt")
