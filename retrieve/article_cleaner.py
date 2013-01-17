import sys, re, string, time, os, pickle

def clean_plaintext_article(text, extract, end_indicators_file):
    """As input, takes the plain text from a wikipedia article that we got from
    the Wikipedia API's extract field, which isn't quite plain text, and removes the
    remaining HTML tags."""
    f = open(end_indicators_file, 'r')
    for line in f.readlines():
        if line.split()[0] == 'exact':
            text = re.sub([a.decode('utf-8') for a in line.split()][1] + r'.*', '', text, flags=re.DOTALL)
        else:
            text = re.sub(r'&lt;h[23]&gt;\s*' + ' '.join([a.decode('utf-8') for a in line.split()]) + r'\s*&lt;/h[23]&gt;.*', '', text, flags=re.DOTALL)
    
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
    for subdir in listing:
        if not os.path.isdir(src_dir + '/' + subdir):
            continue
        if not consolidate_folders:
            if not os.path.exists(target_dir + '/' + subdir):
                os.mkdir(target_dir + '/' + subdir)
        
        files = os.listdir(src_dir + '/' + subdir)
        for filename in files:
            orig_text = open(src_dir + '/' + subdir + '/' + filename).read().decode('utf-8')
            
            new_text = clean_plaintext_article(orig_text, False, end_indicators_file).encode('utf-8')
            if consolidate_folders:
                f = open(target_dir + '/' + filename, 'w')
            else:
                f = open(target_dir + '/' + subdir + '/' + filename, 'w')
            f.write(new_text)
            

                
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
