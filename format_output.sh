#!/bin/bash

# Copy this script to the project root.

if [ $# < 2 ]
then
	echo "Usage: ./main.sh topic-props-file topic-names-file"
else

TOPIC_PROPS=$1
TOPIC_NAMES=$2
OUTPUT_FILE=`dirname $TOPIC_PROPS/human-output.txt`

python output_formatter.py $TOPIC_PROPS $TOPIC_NAMES $OUTPUT_FILE

fi