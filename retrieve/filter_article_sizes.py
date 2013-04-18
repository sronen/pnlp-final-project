import sys, re, string, time, os, pickle, random, shutil, unicodedata

def make_article_size_lists(src_dir, file_2kb, file_5kb):
    list_2kb = list()
    list_5kb = list()

    listing = os.listdir(src_dir)
    for filename in listing:
        filesize = os.path.getsize(src_dir + '/' + filename)
        if filesize > 1600:
            list_2kb.append(filename)
            if filesize > 4000:
                list_5kb.append(filename)

    # write the list of filenames over 2kb to the file
    f = open(file_2kb, 'w')
    f.write('\n'.join(list_2kb))
    f.close()

    # write the list of filenames over 5kb to the file
    f = open(file_5kb, 'w')
    f.write('\n'.join(list_5kb))
    f.close()

def combine_article_lists(file_en, file_es, name_match_file, intersection_file):
    # (output): intersection file: has list of all articles that are 5kb and above with same name 
    # file_en: list of all english article names
    # file_es: list of all spanish article names
    # name_match_file: file where each line has an english and spanish name for a file

    # go through match_file, build spanish to english dictionary
    # go through es file, and convert all es to en

    # OR, do same, but eng->spa with eng_to_spa dict. 4000 accents instead of 6000...

    fn = open(name_match_file)
    spa_to_eng = dict()
    eng_to_spa = dict()
    lines = fn.read().split('\n')[1:]
    for line in lines:
        contents = line.split('\t')
        en_name = unicodedata.normalize('NFC', (contents[0].replace(' ', '_')+'.txt').decode('utf-8'))
        es_name = unicodedata.normalize('NFC', (contents[1].replace(' ', '_') + '.txt').decode('utf-8'))
        spa_to_eng[es_name] = en_name
        eng_to_spa[en_name] = es_name
    fn.close()

    f_en = open(file_en, 'r')
    f_es = open(file_es, 'r')

    list_en = f_en.read().split('\n')
    list_en = map(lambda en_name: unicodedata.normalize('NFC', en_name.decode('utf-8')), list_en)
    list_es = f_es.read().split('\n')
    list_es = map(lambda es_name: unicodedata.normalize('NFC', es_name.decode('utf-8')), list_es)
    spa_list_en = map(lambda en_name: convert_english_name_to_spanish(eng_to_spa, en_name), list_en) # look up en. name
    spa_set_en = set(spa_list_en)
    set_es = set(list_es)
    intersection_set = spa_set_en.intersection(set_es)
    f_en.close()
    f_es.close()

    list_to_print = list()
    for spa_name in list(intersection_set):
        # Englishname,Spanishname
        list_to_print.append(spa_to_eng[spa_name] + '\t' + spa_name)
    f3 = open(intersection_file, 'w')
    f3.write('\n'.join(list_to_print).encode('utf-8')) # write all SPANISH names to file
    f3.close()

def convert_english_name_to_spanish(eng_to_spa, en_name):
    if en_name in eng_to_spa:
        return eng_to_spa[en_name]
    else:
        raise Exception

def make_train_test_split(orig_file, train_file, test_file, src_dir, train_dir, test_dir):
    """
    Assume:
    orig_file (exists already): both_5kb.txt, 5kb_real.txt
    train_file: both_5kb_train.txt, 5kb_real_train.txt
    test_file: both_5kb_test.txt, 5kb_real_test.txt
    src_dir (both exist already): lowernostop-stem -> en/lowernostop-stem + es/lowernostop-stem, 5kb_strcorpuscleaned -> en/..., es/...
    train_dir: 5kbtrain -> en/5kbtrain + es/5kbtrain, 5kb_train -> en/5kb_train, es/5kb_train
    test_dir: 5kbtest -> en/5kbtest + es/5kbtest, same as above
    """
    en_src_dir = 'en/' + src_dir
    es_src_dir = 'es/' + src_dir
    en_train_dir = 'en/' + train_dir
    es_train_dir = 'es/' + train_dir
    en_test_dir = 'en/' + test_dir
    es_test_dir = 'es/' + test_dir

    # 60% train, 40% test
    f = open(orig_file, 'r')
    lines = f.read().split('\n')
    f.close()

    random.shuffle(lines)

    english_names = list()
    spanish_names = list()
    for line in lines:
        english_names.append(line.split('\t')[0])
        spanish_names.append(line.split('\t')[1])

    train_lines = lines[:int(len(lines)*.6)]
    test_lines = lines[int(len(lines)*.6):]

    train_english_names = [line.split('\t')[0] for line in train_lines]
    test_english_names = [line.split('\t')[0] for line in test_lines]
    train_spanish_names = [line.split('\t')[1] for line in train_lines]
    test_spanish_names = [line.split('\t')[1] for line in test_lines]

    # Write down the splits
    f_train = open(train_file, 'w')
    f_train.write('\n'.join(train_lines))
    f_train.close()

    f_test = open(test_file, 'w')
    f_test.write('\n'.join(test_lines))
    f_test.close()

    for cur_dir in [en_train_dir, en_test_dir, es_train_dir, es_test_dir]:
        if not os.path.exists(cur_dir):
            os.makedirs(cur_dir)

    # Actually copy the files into train and test dirs
    for line in train_lines:
        en_name = line.split('\t')[0]
        es_name = line.split('\t')[1]
        shutil.copy(en_src_dir + '/' + en_name, en_train_dir + '/' + en_name)
        shutil.copy(es_src_dir + '/' + es_name, es_train_dir + '/' + es_name)

    for line in test_lines:
        en_name = line.split('\t')[0]
        es_name = line.split('\t')[1]
        shutil.copy(en_src_dir + '/' + en_name, en_test_dir + '/' + en_name)
        shutil.copy(es_src_dir + '/' + es_name, es_test_dir + '/' + es_name)

def process_occupation_file(occupation_file):
    """TODO: when the occupation file format is specified"""
    pass

def make_crossval_split(orig_file, src_dir, crossval_dir, num_folds):
    """TODO"""
    """
    orig_file is the file with the list of all article names (both_5kb.txt)
    src_dir is the root dir for where all the actual article content lives
    crossval_dir is the dir to put
    num_folds is number of folds
    """
    #occupation_dict = process_occupation_file(occupation_file) # english_name -> occupation

    f = open(orig_file, 'r')
    lines = f.read().split('\n')
    f.close()

    num_folds = int(num_folds)

    # random split up
    en_folds = list()
    es_folds = list()

    random.shuffle(lines)

    en_names = list()
    es_names = list()
    for line in lines:
        en_names.append(line.split('\t')[0])
        es_names.append(line.split('\t')[1])

    for i in range(num_folds):
        en_folds.append( en_names[i:len(lines):num_folds] )
        es_folds.append( es_names[i:len(lines):num_folds] )

    for lang in ['en', 'es']:
        if lang == 'en':
            folds = en_folds
        elif lang == 'es':
            folds = es_folds

        lang_crossval_dir = lang + '/' + crossval_dir
        lang_src_dir = lang + '/' + src_dir
        # Create crossval directory
        if not os.path.exists(lang_crossval_dir):
            os.makedirs(lang_crossval_dir)

        fold_name_lists = lang_crossval_dir + '/fold_name_lists'
        if not os.path.exists(fold_name_lists):
            os.makedirs(fold_name_lists)

        # Create fold directories
        for i in range(num_folds):
            f_name_list = open(fold_name_lists + '/fold' + str(1) + '_list.txt', 'w')
            f_name_list.write('\n'.join(folds[i]))
            f_name_list.close()

            if not os.path.exists(lang_crossval_dir + '/fold' + str(i)):
                os.makedirs(lang_crossval_dir + '/fold' + str(i))
                for name in folds[i]:
                    shutil.copy(lang_src_dir + '/' + name, lang_crossval_dir + '/fold' + str(i))
            """if not os.path.exists(lang_crossval_dir + '/all_but_fold' + str(i)):
                os.makedirs(lang_crossval_dir + '/all_but_fold' + str(i))
                for j in range(num_folds):
                    if i != j:
                        for name in folds[j]:
                            shutil.copy(lang_src_dir + '/' + name, lang_crossval_dir + '/all_but_fold' + str(i))
            """

                
if __name__=='__main__':
    if sys.argv[1] == 'cross':
        make_crossval_split(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
    elif sys.argv[1] == 'split':
        # all under datasets/par_corpus, both_5kb.txt, both_5kb_train.txt, both_5kb_test.txt, en/lowernostop-stem, en/5kbtrain, en/5kbtest
        make_train_test_split(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7])
    elif sys.argv[1] == 'combine':
        combine_article_lists(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
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
