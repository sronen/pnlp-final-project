#!/bin/bash

# Copy to your mallet/bin directory and execute there.
# Usage: ./run_mallet.sh INPUT_FILE_NO_EXTENSION NUM_TOP_WORDS
 #bin/mallet train-topics --input wiki_lemm2.mallet --num-topics 30 --output-state sample-data/wiki_bios_lem/wiki_bios_lemm2_30.gz --output-doc-topics wiki_bios_lemm_doc_topics2_30.txt --output-topic-keys wiki_bios_lemm_keys2_30.txt --num-top-words 200

INPUT_FILE=$1
NUM_TOP_WORDS=$2
#NUM_TOPICS=$3

OUTPUT_DIR=$INPUT_FILE"_output"
mkdir $OUTPUT_DIR

for NUM_TOPICS in 10 30 50 200
do	
	bin/mallet train-topics --input $INPUT_FILE".mallet" --num-topics $NUM_TOPICS \
	--output-state $OUTPUT_DIR"/"$INPUT_FILE"_"$NUM_TOPICS".gz" \
	--output-doc-topics $OUTPUT_DIR"/"$INPUT_FILE"_topics_"$NUM_TOPICS".txt" \
	--output-topic-keys $OUTPUT_DIR"/"$INPUT_FILE"_keys_"$NUM_TOPICS".txt" \
	--num-top-words $NUM_TOP_WORDS
done
