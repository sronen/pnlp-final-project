'''
Functions for handling OS aspects of corpus preparation
'''

import os
import shutil
import random


def get_items_in_folder(root_path):
	'''
	Return a list of items (files and folders) in the passed folder, discarding
	hidden files (starting with '.') and POS directories (starting with '_')
	'''
	PREFIXES_TO_DISCARD = ['.', '_']
	
	os.listdir(root_path)
	sub_items = []
	for item in os.listdir(root_path):
		if item[0] not in PREFIXES_TO_DISCARD:
			sub_items.append(item)
			
	return sub_items


def split_training_and_test(root_path, train_percent=70):
	'''
	Split the passed corpus into training and test document.
	Copy the files to folders named _test_ and _training_ under root_path
	-Return: training and test path, respectively
	'''
	
	# Create folders for test and training
	training_root_path = os.path.join(root_path, '_training_articles_')
	try:
		os.mkdir(training_root_path)
	except OSError:
		# alredy exists, delete and recreate
		shutil.rmtree(training_root_path)
		os.mkdir(training_root_path)
	
	test_root_path = os.path.join(root_path, '_test_articles_')
	try:
		os.mkdir(test_root_path)
	except OSError:
		# alredy exists, delete and recreate
		shutil.rmtree(test_root_path)
		os.mkdir(test_root_path)
	
	for category_folder in get_items_in_folder(root_path):
		category_path = os.path.join(root_path, category_folder)
		
		# Create category folders under test and training folders 
		category_training_path = os.path.join(training_root_path, category_folder)
		try:
			os.mkdir(category_training_path)
		except OSError:
			# alredy exists, delete and recreate
			shutil.rmtree(category_training_path)
			os.mkdir(category_training_path)
		
		category_test_path = os.path.join(test_root_path, category_folder)
		try:
			os.mkdir(category_test_path)
		except OSError:
			# alredy exists, delete and recreate
			shutil.rmtree(category_test_path)
			os.mkdir(category_test_path)
		
		# Determine number of articles to match requested percentage,
		# and randomally choose them
		all_articles = get_items_in_folder(category_path)
		num_training_articles = len(all_articles) * train_percent / 100 # round down
		random.shuffle(all_articles)
		training_articles = all_articles[:num_training_articles]
		test_articles = all_articles[num_training_articles:]
			
		# Copy articles to respective categroy folders under training or test
		# folder
		for filename in training_articles:
			shutil.copy(os.path.join(category_path, filename), category_training_path)
			
		for filename in test_articles:
			shutil.copy(os.path.join(category_path, filename), category_test_path)
			
	return training_root_path, test_root_path
			
