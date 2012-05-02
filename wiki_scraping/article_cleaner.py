import sys, re, string, time, os

def clean_plaintext_article(text):
    """As input, takes the plain text from a wikipedia article that we got from
    the Wikipedia API's extract field, which isn't quite plain text, and removes the
    remaining HTML tags."""
    try:
        text = re.sub(r'&lt;h2&gt;\s*[Ee]xternal [Ll]inks\s*&lt;/h2&gt;.*', '', text, flags=re.DOTALL)
        text = re.sub(r'&lt;h2&gt;\s*[Ee]xternal [Ll]inks and [Rr]eferences\s*&lt;/h2&gt;.*', '', text, flags=re.DOTALL)
        text = re.sub(r'&lt;h2&gt;\s*Notes\s*&lt;/h2&gt;.*', '', text, flags=re.DOTALL)
        text = re.sub(r'&lt;h2&gt;\s*[Ss]ource\s*&lt;/h2&gt;.*', '', text, flags=re.DOTALL)
        text = re.sub(r'&lt;h2&gt;\s*[Rr]eferences\s*&lt;/h2&gt;.*', '', text, flags=re.DOTALL)
        text = re.sub(r'&lt;h2&gt;\s*[Ss]ee [Aa]lso\s*&lt;/h2&gt;.*', '', text, flags=re.DOTALL)
        text = re.sub(r'&lt;.*?&gt;', '', text)
        text = re.sub(r'&amp;amp;', '&', text)
        text = re.sub(r'&[^;\s]*?;', '', text)
        """
        all = re.sub(r'\n', ' ', all)
        all = re.sub(r'\{\{.*?\}\}', r'', all)
        all = re.sub(r'\[\[Category:.*', '', all)
        all = re.sub(r'==\s*[Ss]ource\s*==.*', '', all)
        all = re.sub(r'==\s*[Rr]eferences\s*==.*', '', all)
        all = re.sub(r'==\s*[Ee]xternal [Ll]inks\s*==.*', '', all)
        all = re.sub(r'==\s*[Ee]xternal [Ll]inks and [Rr]eferences==\s*', '', all)
        all = re.sub(r'==\s*[Ss]ee [Aa]lso\s*==.*', '', all)
        all = re.sub(r'http://[^\s]*', '', all)
        all = re.sub(r'\[\[Image:.*?\]\]', '', all)
        all = re.sub(r'Image:.*?\|', '', all)
        all = re.sub(r'\[\[.*?\|*([^\|]*?)\]\]', r'\1', all)
        all = re.sub(r'\&lt;.*?&gt;', '', all)
        """
    except:
        # Something went wrong, try again. (This is bad coding practice.)
        print 'oops. there was a failure parsing %s.' \
            % articletitle
        return "error"
    return text
 
def make_clean_dataset_directory(src_dir, target_dir):
    """Take in a dataset directory src_dir, which should have subdirectories that represent
    categories, and files in those subdirectories that are plaintext wikipedia articles.
    Clean those wikipedia articles and put them in a new dataset directory called target_dir."""
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    listing = os.listdir(src_dir)
    for subdir in listing:
        if not os.path.exists(target_dir + '/' + subdir):
            os.mkdir(target_dir + '/' + subdir)
        
        files = os.listdir(src_dir + '/' + subdir)
        for filename in files:
            orig_text = open(src_dir + '/' + subdir + '/' + filename).read().decode('utf-8')
            
            new_text = clean_plaintext_article(orig_text).encode('utf-8')
            f = open(target_dir + '/' + subdir + '/' + filename, 'w')
            f.write(new_text)
                
if __name__=='__main__':
    if (len(sys.argv) < 3) or (not os.path.exists(sys.argv[1])):
        print "Usage: article_cleaner.py src_dir target_dir. src_dir must exist."
    else:
        make_clean_dataset_directory(sys.argv[1], sys.argv[2])