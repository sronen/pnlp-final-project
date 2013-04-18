#!/bin/bash

# Copy this script to your mallet/bin directory and execute there.
# Under wiki_input, create a folder of your choice with a sub-folder named "en",
# and place your docs there.
# Usage: ./run_mallet.sh INPUT_FILE_NO_EXTENSION NUM_TOP_WORDS
#bin/mallet train-topics --input wiki_lemm2.mallet --num-topics 30 --output-state sample-data/wiki_bios_lem/wiki_bios_lemm2_30.gz --output-doc-topics wiki_bios_lemm_doc_topics2_30.txt --output-topic-keys wiki_bios_lemm_keys2_30.txt --num-top-words 200

INPUT_FILE=$1
NUM_TOP_WORDS=$2
#NUM_TOPICS=$3

INPUT_ROOT="wiki_input/"
OUTPUT_ROOT="wiki_output/"
LANG="en/"
OUTPUT_DIR=$OUTPUT_ROOT$LANG$INPUT_FILE"_output/"
MALLET_FILE=$OUTPUT_DIR$INPUT_FILE".mallet"

echo $INPUT_ROOT$INPUT_FILE"/"$LANG
echo $OUTPUT_DIR

# Create intermediate dirs
mkdir -p $OUTPUT_DIR
bin/mallet import-dir --input $INPUT_ROOT$INPUT_FILE"/"$LANG --keep-sequence --output $MALLET_FILE

for NUM_TOPICS in 10 30 50 200
do	
	bin/mallet train-topics --input $MALLET_FILE --num-topics $NUM_TOPICS \
	--output-state $OUTPUT_DIR"/"$INPUT_FILE"_"$NUM_TOPICS".gz" \
	--output-doc-topics $OUTPUT_DIR"/"$INPUT_FILE"_topics_"$NUM_TOPICS".txt" \
	--output-topic-keys $OUTPUT_DIR"/"$INPUT_FILE"_keys_"$NUM_TOPICS".txt" \
	--num-top-words $NUM_TOP_WORDS
done
