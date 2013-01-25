import sys, re, string, time, os, pickle, random, shutil

def make_article_size_lists(src_dir, file_1kb, file_5kb):
    list_1kb = list()
    list_5kb = list()

    listing = os.listdir(src_dir)
    for filename in listing:
        filesize = os.path.getsize(src_dir + '/' + filename)
        if filesize > 800:
            list_1kb.append(filename)
            if filesize > 4000:
                list_5kb.append(filename)

    # write the list of filenames over 1kb to the file
    f = open(file_1kb, 'w')
    f.write('\n'.join(list_1kb))
    f.close()

    # write the list of filenames over 5kb to the file
    f = open(file_5kb, 'w')
    f.write('\n'.join(list_5kb))
    f.close()

def combine_article_lists(file1, file2, intersection_file):
    f1 = open(file1, 'r')
    f2 = open(file2, 'r')

    set1 = set(f1.read().split('\n'))
    set2 = set(f2.read().split('\n'))
    intersection_set = set1.intersection(set2)
    f1.close()
    f2.close()

    f3 = open(intersection_file, 'w')
    f3.write('\n'.join(list(intersection_set)))
    f3.close()

def make_train_test_split(orig_file, train_file, test_file, src_dir, train_dir, test_dir):
    # 60% train, 40% test
    f = open(orig_file, 'r')
    names = f.read().split('\n')
    f.close()

    random.shuffle(names)

    train_names = names[:int(len(names)*.6)]
    test_names = names[int(len(names)*.6):]

    # Write down the splits
    f_train = open(train_file, 'w')
    f_train.write('\n'.join(train_names))
    f_train.close()

    f_test = open(test_file, 'w')
    f_test.write('\n'.join(test_names))
    f_test.close()

    # Create train and test folders
    if not os.path.exists(train_dir):
        os.makedirs(train_dir)

    if not os.path.exists(test_dir):
        os.makedirs(test_dir)

    # Actually copy the files into train and test dirs
    for name in train_names:
        shutil.copy(src_dir + '/' + name, train_dir + '/' + name)

    for name in test_names:
        shutil.copy(src_dir + '/' + name, test_dir + '/' + name)

def make_crossval_split(orig_file, file_prefix, src_dir, crossval_dir, k):
    """TODO"""
    """
    orig_file is the file with the list of all article names (both_5kb.txt)
    file_prefix is the prefix to use for the crossval file names
    src_dir is the root dir for where all the actual article content lives
    crossval_dir is the dir to put
    k is number of folds
    """
    # 60% train, 40% test
    f = open(orig_file, 'r')
    names = f.read().split('\n')
    f.close()

    random.shuffle(names)

    train_names = names[:int(len(names)*.6)]
    test_names = names[int(len(names)*.6):]

    # Write down the splits
    f_train = open(train_file, 'w')
    f_train.write('\n'.join(train_names))
    f_train.close()

    f_test = open(test_file, 'w')
    f_test.write('\n'.join(test_names))
    f_test.close()

    # Create train and test folders
    if not os.path.exists(train_dir):
        os.makedirs(train_dir)

    if not os.path.exists(test_dir):
        os.makedirs(test_dir)

    # Actually copy the files into train and test dirs
    for name in train_names:
        shutil.copy(src_dir + '/' + name, train_dir + '/' + name)

    for name in test_names:
        shutil.copy(src_dir + '/' + name, test_dir + '/' + name)

                
if __name__=='__main__':
    if sys.argv[1] == 'split':
        # all under datasets/par_corpus, both_5kb.txt, both_5kb_train.txt, both_5kb_test.txt, en/lowernostop-stem, en/5kbtrain, en/5kbtest
        make_train_test_split(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7])
    elif len(sys.argv) > 4 and sys.argv[4] == 'combine':
        combine_article_lists(sys.argv[1], sys.argv[2], sys.argv[3])
    else:
        make_article_size_lists(sys.argv[1], sys.argv[2], sys.argv[3])


    # if (len(sys.argv) < 3) or (not os.path.exists(sys.argv[1])):
    #     print "Usage: article_cleaner.py src_dir target_dir end_indicators_file. src_dir must exist."
    # else:
    #     if len(sys.argv) > 4:
    #         make_clean_dataset_directory(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]=='y')
    #     elif len(sys.argv) > 3:
    #         make_clean_dataset_directory(sys.argv[1], sys.argv[2], sys.argv[3])
    #     else:
    #         make_clean_dataset_directory(sys.argv[1], sys.argv[2])