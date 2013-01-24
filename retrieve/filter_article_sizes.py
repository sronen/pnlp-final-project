import sys, re, string, time, os, pickle

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

                
if __name__=='__main__':
    if len(sys.argv) > 4 and sys.argv[4] == 'combine':
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