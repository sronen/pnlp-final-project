#!/bin/bash

# Copy this script to the project root.
# ./main.sh english en
# ./main.sh french fr
# ./main.sh spanish es

if [ $# < 2 ]
then
	echo "Usage: ./main.sh language-name wiki-language-code [run-mallet=y/n, default:y]"
else

# PARAMS
LANGUAGE=$1
LANG=$2
if [ $# -eq 3 ]
then
	RUN_MALLET=$3
else
	RUN_MALLET=y
fi
NUM_TOP_WORDS=100
MALLET_BIN_DIR='/Applications/mallet-2.0.7/bin'
CLASSIFY_DIR='classify'
RETRIEVE_DIR='retrieve'
DATASETS_DIR='datasets'
ENGLISH_DATA_DIR='plaintext_featured_bios'
END_INDICATORS="$DATASETS_DIR/$LANG/end_indicators.txt"
if [ -e "$DATASETS_DIR/$LANG/stopwords.txt" ];
then
	STOPWORDS="$DATASETS_DIR/$LANG/stopwords.txt"
fi


# Download articles
if [ ! -e $DATASETS_DIR/$LANG/plain ]
then
	echo "downloading articles"
	python $RETRIEVE_DIR/featured_article_downloader.py $DATASETS_DIR/$ENGLISH_DATA_DIR $DATASETS_DIR/$LANG/plain $LANG
fi

# Clean articles
if [ ! -e $DATASETS_DIR/$LANG/clean ]
then
	echo "running article article_cleaner"
	python $RETRIEVE_DIR/article_cleaner.py $DATASETS_DIR/$LANG/plain $DATASETS_DIR/$LANG/clean $END_INDICATORS
fi


if [ ! -e $DATASETS_DIR/$LANG/lowernostop ]
then
	echo "running lowernostop str_corpus_cleaner"
	python $CLASSIFY_DIR/tf_idf/str_corpus_cleaner.py $DATASETS_DIR/$LANG/clean $DATASETS_DIR/$LANG/lowernostop n n $LANGUAGE y $STOPWORDS
fi

if [ ! -e $DATASETS_DIR/$LANG/lowernostop-stem ]
then
	echo "running lowernostop-stem str_corpus_cleaner"
	python $CLASSIFY_DIR/tf_idf/str_corpus_cleaner.py $DATASETS_DIR/$LANG/clean $DATASETS_DIR/$LANG/lowernostop-stem y n $LANGUAGE y $STOPWORDS
fi

if [ $RUN_MALLET == "y" ]
then
	echo "running mallet"
	# Run mallet
	MALLET_ROOT=$DATASETS_DIR/$LANG/mallet
	mkdir -p $MALLET_ROOT/lowernostop
	mkdir -p $MALLET_ROOT/lowernostop-stem
	RAW_DATA=$MALLET_ROOT/lowernostop/data.mallet
	STEM_DATA=$MALLET_ROOT/lowernostop-stem/data.mallet
	$MALLET_BIN_DIR/mallet import-dir --input $DATASETS_DIR/$LANG/lowernostop \
	--keep-sequence --output $RAW_DATA --token-regex '[\p{L}\p{M}]+'
	$MALLET_BIN_DIR/mallet import-dir --input $DATASETS_DIR/$LANG/lowernostop-stem \
	--keep-sequence --output $STEM_DATA --token-regex '[\p{L}\p{M}]+'

	for NUM_TOPICS in 10 30 50 200
	do	
		RAW_ROOT=$MALLET_ROOT/lowernostop/$NUM_TOPICS
		mkdir -p $RAW_ROOT
		STEM_ROOT=$MALLET_ROOT/lowernostop-stem/$NUM_TOPICS
		mkdir -p $STEM_ROOT
		$MALLET_BIN_DIR/mallet train-topics --input $RAW_DATA --num-topics $NUM_TOPICS \
		--output-state $RAW_ROOT/state.gz \
		--output-doc-topics $RAW_ROOT/doc-topic-proportions.txt \
		--output-topic-keys $RAW_ROOT/topic-keys.txt \
		--num-top-words $NUM_TOP_WORDS
		$MALLET_BIN_DIR/mallet train-topics --input $STEM_DATA --num-topics $NUM_TOPICS \
		--output-state $STEM_ROOT/state.gz \
		--output-doc-topics $STEM_ROOT/doc-topic-proportions.txt \
		--output-topic-keys $STEM_ROOT/topic-keys.txt \
		--num-top-words $NUM_TOP_WORDS
	done
	fi
fi
