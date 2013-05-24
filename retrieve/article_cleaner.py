import sys, re, string, time, os, pickle

def clean_plaintext_article(text, extract, end_indicators_file):
    """As input, takes the plain text from a wikipedia article that we got from
    the Wikipedia API's extract field, which isn't quite plain text, and removes the
    remaining HTML tags."""
    f = open(end_indicators_file, 'r')
    lines = f.readlines()
    edit = lines[0].strip()
    for line in lines[1:]:
        if line.split()[0] == 'exact':
            text = re.sub([a.decode('utf-8') for a in line.split()][1] + r'.*', '', text, flags=re.DOTALL)
        else:
            text = re.sub(r'&lt;h[23]((?!&gt;).)*&gt;\s*' + ' '.join([a.decode('utf-8') for a in line.split()]) + r'\s*(\[.*?\])?\s*&lt;/h[23]&gt;.*', '', text, flags=re.DOTALL)
    
    text = re.sub(r'(\[\s*?' + edit + r'\s*?\])', '', text) # remove all [edit] markersa
    text = re.sub(r'&amp;amp;', '&', text) # display ampersands properly
    if extract:
        return text
    text = re.sub(r'&lt;.*?&gt;', '', text) # remove all html tags
    text = re.sub(r'&[^;\s]*?;', '', text) # remove all other markings, e.g. &quot;

    return text
 
def make_clean_dataset_directory(src_dir, target_dir, end_indicators_file, consolidate_folders=True):
    """Take in a dataset directory src_dir, which should have subdirectories that represent
    categories, and files in those subdirectories that are plaintext wikipedia articles.
    Clean those wikipedia articles and put them in a new dataset directory called target_dir."""
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    listing = os.listdir(src_dir)
    for subdir in listing: # This could either be a category folder, or an individual file.
        if os.path.isdir(src_dir + '/' + subdir):
            # We are in the setup where we have src_dir/category_dir/file
            process_subdir(target_dir, src_dir, subdir, end_indicators_file, consolidate_folders)
        #elif subdir[-4:] == '.txt':
        else:
            # We are in the setup where we have src_dir/file, and "subdir" are actually the files
            try:
                if not os.path.exists(target_dir + '/' + subdir):
                    process_file(src_dir + '/' + subdir, target_dir + '/' + subdir, end_indicators_file)
                else:
                    print 'olo'
            except Exception as e:
                print "Error cleaing file %s" % e


def process_subdir(target_dir, src_dir, subdir, end_indicators_file, consolidate_folders=True):
    if not consolidate_folders:
        if not os.path.exists(target_dir + '/' + subdir):
            os.mkdir(target_dir + '/' + subdir)
    
    files = os.listdir(src_dir + '/' + subdir)
    for filename in files:
        if consolidate_folders:
            process_file(src_dir + '/' + subdir + '/' + filename, target_dir + '/' + filename, end_indicators_file)
        else:
            process_file(src_dir + '/' + subdir + '/' + filename, target_dir + '/' + subdir + '/' + filename, end_indicators_file)

def process_file(file_path, target_path, end_indicators_file):
        orig_text = open(file_path).read().decode('utf-8')
        new_text = clean_plaintext_article(orig_text, False, end_indicators_file).encode('utf-8')
        f = open(target_path, 'w')
        f.write(new_text)
        f.close()

                
if __name__=='__main__':
    if (len(sys.argv) < 3) or (not os.path.exists(sys.argv[1])):
        print "Usage: article_cleaner.py src_dir target_dir end_indicators_file. src_dir must exist."
    else:
        if len(sys.argv) > 4:
            make_clean_dataset_directory(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]=='y')
        elif len(sys.argv) > 3:
            make_clean_dataset_directory(sys.argv[1], sys.argv[2], sys.argv[3])
        else:
            make_clean_dataset_directory(sys.argv[1], sys.argv[2])
