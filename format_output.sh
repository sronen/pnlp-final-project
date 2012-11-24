#!/bin/bash

# Copy this script to the project root.

if [ $# -lt 3 ]
then
	echo "Usage: ./main.sh lang processingname numtopics, e.g. fr lowernostop-stem 30"
else

	LANG=$1
	PROCESSING=$2
	NUMTOPICS=$3
	DATASETS=datasets
	DIR=$DATASETS/$LANG/mallet/$PROCESSING/$NUMTOPICS
	TOPIC_PROPS=$DIR/doc-topic-proportions.txt
	TOPIC_NAMES=$DIR/topic-names.txt
	OUTPUT_FILE=$DIR/human-output.txt
	if [ ! -e $TOPIC_NAMES ]
	then
		echo "You need to name the topics and save them to $TOPIC_NAMES"
	else
		python classify/output_formatter.py $TOPIC_PROPS $TOPIC_NAMES $OUTPUT_FILE
	fi
fi