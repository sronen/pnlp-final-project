#!/bin/bash

#####
# Parallel corpus instructions


#
# python retrieve/article_cleaner.py datasets/parallel_corpora/parallel_corpus/par_corpus_xml/en datasets/parallel_corpora/parallel_corpus/par_corpus_clean/en datasets/en/end_indicators.txt
# python retrieve/filter_article_sizes.py -> generate the ultimate list of articles you want to use, article_list.txt
# python $CLASSIFY_DIR/tf_idf/str_corpus_cleaner.py $DATASETS_DIR/$LANG/clean $DATASETS_DIR/$LANG/lowernostop-stem y n $LANGUAGE y $STOPWORDS
# /Applications/mallet-2.0.7/bin/mallet import-dir --input en/5kb_train_test_split/5kbtrain --keep-sequence --output en/5kb_train_test_split/5kbmallet/5kbtrain_data.mallet --token-regex '[\p{L}\p{M}]+'
# /Applications/mallet-2.0.7/bin/mallet train-topics --input en/5kb_train_test_split/5kbmallet/5kbtrain_data.mallet --num-topics 30 --output-state en/5kb_train_test_split/5kbmallet/state.gz --output-doc-topics en/5kb_train_test_split/5kbmallet/doc-topic-proportions.txt --output-topic-keys en/5kb_train_test_split/5kbmallet/topic-keys.txt --num-top-words 100 --inferencer-filename en/5kb_train_test_split/5kbmallet/inferencer.mallet

#( to classify all spanish, from par_corpus/es, /Applications/mallet-2.0.7/bin/mallet train-topics --input 2kb_all_train.mallet --num-topics 30 --output-state 2kb_all_train_state_30_5000.gz --output-doc-topics 2kb_all_train_doc_topic_proportions_30_5000.txt --output-topic-keys 2kb_all_train_topic_keys_30_5000.txt --num-top-words 100 --num-iterations 5000 --optimize-interval 10)
#
# /Applications/mallet-2.0.7/bin/mallet import-dir --input en/5kb_train_test_split/5kbtest --keep-sequence --output en/5kb_train_test_split/5kbmallet/5kbtest_data.mallet --token-regex '[\p{L}\p{M}]+' --use-pipe-from en/5kb_train_test_split/5kbmallet/5kbtrain_data.mallet 
# /Applications/mallet-2.0.7/bin/mallet infer-topics --input en/5kb_train_test_split/5kbmallet/5kbtest_data.mallet --output-doc-topics en/5kb_train_test_split/5kbmallet/test-doc-topic-proportions.txt --inferencer en/5kb_train_test_split/5kbmallet/inferencer.mallet
# 
#####

# Copy this script to the project root.
# ./main.sh english en
# ./main.sh french fr
# ./main.sh spanish es

# ./main.sh english en y both_5kb.txt

if [ $# -lt 2 ]
then
	echo "Usage: ./main.sh language-name wiki-language-code [run-mallet=y/n, default:y]"
else

PARALLEL_CORPUS=2 # 0, 1

# PARAMS
LANGUAGE=$1
LANG=$2
if [ $# -gt 2 ]
then
	RUN_MALLET=$3
else
	RUN_MALLET=y
fi
if [ $# -eq 4 ]
then
	ARTICLE_LIST=$4
else
	ARTICLE_LIST=both_5kb.txt
fi
NUM_TOP_WORDS=100
#MALLET_BIN_DIR='/Applications/mallet-2.0.7/bin'
MALLET_BIN_DIR='mallet-2.0.7/bin'
CLASSIFY_DIR='classify'
RETRIEVE_DIR='retrieve'
if [ $PARALLEL_CORPUS -eq 1 ]
then
	DATASETS_DIR='datasets/par_corpus'
else
	DATASETS_DIR='datasets'
fi
ENGLISH_DATA_DIR='plaintext_featured_bios'
END_INDICATORS="$DATASETS_DIR/$LANG/end_indicators.txt"
if [ -e "datasets/$LANG/stopwords.txt" ];
then
	STOPWORDS="datasets/$LANG/stopwords.txt"
else
	STOPWORDS=n
fi
STEMMED_FOLDER_NAME='2kb-lower-nostop-lemma'

if [ $PARALLEL_CORPUS -eq 0 ]
then
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

	# the second "n" in the next two commands signals that we don't want to just blindly remove every capitalized word.
	# we can change it to "y" if we would like to do that.
	if [ ! -e $DATASETS_DIR/$LANG/lowernostop ]
	then
		echo "running lowernostop str_corpus_cleaner"
		python $CLASSIFY_DIR/tf_idf/str_corpus_cleaner.py $DATASETS_DIR/$LANG/clean $DATASETS_DIR/$LANG/lowernostop n n $LANGUAGE y $STOPWORDS
	fi
fi

if [ ! -e $DATASETS_DIR/$LANG/$STEMMED_FOLDER_NAME ]
then
	echo "running $STEMMED_FOLDER_NAME str_corpus_cleaner"
	if [ $PARALLEL_CORPUS -eq 0 ]
	then
		python $CLASSIFY_DIR/tf_idf/str_corpus_cleaner.py $DATASETS_DIR/$LANG/clean $DATASETS_DIR/$LANG/$STEMMED_FOLDER_NAME y n $LANGUAGE y $STOPWORDS
	else
		python $CLASSIFY_DIR/tf_idf/str_corpus_cleaner.py $DATASETS_DIR/$LANG/clean $DATASETS_DIR/$LANG/$STEMMED_FOLDER_NAME y n $LANGUAGE y $STOPWORDS $DATASETS_DIR/$ARTICLE_LIST
	fi
fi

#if [ $RUN_MALLET == "y" ]
#then
	echo "running mallet"

	FOLDERNAME=$STEMMED_FOLDER_NAME
	# Run mallet
	MALLET_ROOT=$DATASETS_DIR/$LANG/mallet
	#mkdir -p $MALLET_ROOT/lowernostop
	mkdir -p $MALLET_ROOT/$STEMMED_FOLDER_NAME
	#RAW_DATA=$MALLET_ROOT/lowernostop/data.mallet
	STEM_DATA=$MALLET_ROOT/$STEMMED_FOLDER_NAME/data.mallet
	# if [ ! -e $RAW_DATA ]
	# then
	# 	$MALLET_BIN_DIR/mallet import-dir --input $DATASETS_DIR/$LANG/lowernostop \
	# 	--keep-sequence --output $RAW_DATA --token-regex '[\p{L}\p{M}]+'
	# fi
	if [ ! -e $STEM_DATA ]
	then
	        echo "sup"
		echo "sudo $MALLET_BIN_DIR/mallet import-dir --input $DATASETS_DIR/$LANG/$STEMMED_FOLDER_NAME --keep-sequence --output $STEM_DATA --token-regex '[\p{L}\p{M}]+'"
	        sudo $MALLET_BIN_DIR/mallet import-dir --input $DATASETS_DIR/$LANG/$STEMMED_FOLDER_NAME \
		--keep-sequence --output $STEM_DATA --token-regex '[\p{L}\p{M}]+'
	fi

	#for NUM_TOPICS in 10 30 50 200
	for NUM_TOPICS in 50 #30
	do	
		# RAW_ROOT=$MALLET_ROOT/lowernostop/$NUM_TOPICS
		# mkdir -p $RAW_ROOT
		STEM_ROOT=$MALLET_ROOT/$STEMMED_FOLDER_NAME/$NUM_TOPICS
		mkdir -p $STEM_ROOT
		# if [ ! \( \( -e $RAW_ROOT/topic-keys.txt \) -a \( -e $RAW_ROOT/doc-topic-proportions.txt \) -a \( -e $RAW_ROOT/state.gz \) \) ]
		# then
		# 	$MALLET_BIN_DIR/mallet train-topics --input $RAW_DATA --num-topics $NUM_TOPICS \
		# 	--output-state $RAW_ROOT/state.gz \
		# 	--output-doc-topics $RAW_ROOT/doc-topic-proportions.txt \
		# 	--output-topic-keys $RAW_ROOT/topic-keys.txt \
		# 	--num-top-words $NUM_TOP_WORDS
		# fi
     	if [ ! \( \( -e $STEM_ROOT/topic-keys.txt \) -a \( -e $STEM_ROOT/doc-topic-proportions.txt \) -a \( -e $STEM_ROOT/state.gz \) \) ]
		then
			sudo $MALLET_BIN_DIR/mallet train-topics --input $STEM_DATA --num-topics $NUM_TOPICS \
			--output-state $STEM_ROOT/state.gz \
			--output-doc-topics $STEM_ROOT/doc-topic-proportions.txt \
			--output-topic-keys $STEM_ROOT/topic-keys.txt \
			--num-top-words $NUM_TOP_WORDS
		fi
	done
	fi
#fi
