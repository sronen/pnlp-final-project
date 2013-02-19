# RUN THIS AFTER MERGE RUNS

ENG.TOP.TEN <- c("Whitney Houston", "Barack Obama", "Mitt Romney", 
        "Nicki Minaj", "Justin Bieber", "Adele (singer)",
        "Eminem", "Rihanna", "Adolf Hitler", "Lionel Messi" 
)

SPA.TOP.TEN <- c("Lionel Messi", "Pablo Escobar", "Justin Bieber",
                 "Leonardo da Vinci", "Adele", "Albert Einstein",
                 "Simón Bolívar", "Adolf Hitler", "Aristóteles", "Selena Gomez" )

write.topics.for.top.ten.viewed <- function(top.ten.list, topics.table, output.file) {
  res <- round(topics.table[rownames(topics.table) %in% top.ten.list,]*100, 1)
  
  write.table(res, output.file, 
              row.names=T, 
              col.names=NA, # convention for leaving header of first title empty
              sep='\t', quote=F)
}

main <- function() {
  write.topics.for.top.ten.viewed(ENG.TOP.TEN, eng.final, "en_topics_for_top_ten.tsv")
  write.topics.for.top.ten.viewed(SPA.TOP.TEN, spa.final, "es_topics_for_top_ten.tsv")
}

main()
