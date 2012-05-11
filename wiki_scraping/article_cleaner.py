import sys, re, string, time, os, pickle

def clean_plaintext_article(text, extract_topics=False):
    """As input, takes the plain text from a wikipedia article that we got from
    the Wikipedia API's extract field, which isn't quite plain text, and removes the
    remaining HTML tags."""
    try:
        text = re.sub(r'&lt;h2&gt;\s*[Ee]xternal [Ll]inks\s*&lt;/h2&gt;.*', '', text, flags=re.DOTALL)
        text = re.sub(r'&lt;h2&gt;\s*[Ee]xternal [Ll]inks and [Rr]eferences\s*&lt;/h2&gt;.*', '', text, flags=re.DOTALL)
        text = re.sub(r'&lt;h2&gt;\s*Notes\s*&lt;/h2&gt;.*', '', text, flags=re.DOTALL)
        text = re.sub(r'&lt;h2&gt;\s*Footnotes\s*&lt;/h2&gt;.*', '', text, flags=re.DOTALL)
        text = re.sub(r'&lt;h2&gt;\s*Further reading\s*&lt;/h2&gt;.*', '', text, flags=re.DOTALL)
        text = re.sub(r'&lt;h2&gt;\s*[Ss]ource\s*&lt;/h2&gt;.*', '', text, flags=re.DOTALL)
        text = re.sub(r'&lt;h2&gt;\s*[Rr]eferences\s*&lt;/h2&gt;.*', '', text, flags=re.DOTALL)
        text = re.sub(r'&lt;h2&gt;\s*[Ss]ee [Aa]lso\s*&lt;/h2&gt;.*', '', text, flags=re.DOTALL)
        text = re.sub(r'&amp;amp;', '&', text) # display ampersands properly
        if extract_topics:
            return text
        text = re.sub(r'&lt;.*?&gt;', '', text) # remove all html tags
        text = re.sub(r'&[^;\s]*?;', '', text) # remove all other markings, e.g. &quot;
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
            
            new_text = clean_plaintext_article(orig_text, False).encode('utf-8')
            f = open(target_dir + '/' + subdir + '/' + filename, 'w')
            f.write(new_text)
            
def make_topic_dataset(src_dir):
    """Take in a dataset directory src_dir, which should have subdirectories that represent
    categories, and files in those subdirectories that are plaintext wikipedia articles.
    Clean those wikipedia articles return them."""
    listing = os.listdir(src_dir)
    topic_struct = dict()
    for subdir in listing:
        topic_struct[subdir] = dict()
        files = os.listdir(src_dir + '/' + subdir)
        for filename in files:
            orig_text = open(src_dir + '/' + subdir + '/' + filename).read().decode('utf-8')
            
            new_text = clean_plaintext_article(orig_text, True)
            topic_headings = re.findall(r'&lt;h[23]&gt;.*?&lt;/h[23]&gt;', new_text)
            topic_headings = [re.sub(r'&lt;h[23]&gt; ', '', h) for h in topic_headings]
            topic_headings = [re.sub(r'&lt;/?h[23]&gt;', '', h) for h in topic_headings]
            topic_headings = [re.sub(r'&lt;.*?&gt;', '', h) for h in topic_headings]
            topic_headings = [re.sub(r'&[^;\s]*?;', '', h) for h in topic_headings]
            topic_struct[subdir][filename] = topic_headings
    return topic_struct
    
def make_infobox_dataset(src_dir):
    """Take in a raw dataset directory, and extract infobox data."""
    listing = os.listdir(src_dir)
    infobox_struct = dict()
    
    for subdir in listing:
        infobox_struct[subdir] = dict()
        files = os.listdir(src_dir + '/' + subdir)
        for filename in files:
            orig_text = open(src_dir + '/' + subdir + '/' + filename).read().decode('utf-8')
            
            infobox_features = []
            infobox = False
            ignore = 0
            for line in orig_text.splitlines():
                if not infobox:
                    match = re.search(r'{{Infobox',line)
                    if match:
                        infobox = True
                        infobox_features.append(match.string[10:])
                if infobox:
                    print line
                    # extract the features from the line
                    if len(line) > 1 and line[0] == '|':
                        match = re.search(r'\s?.*?\s*?=', line[1:])
                        if match:
                            feature_name = re.sub(r'=.*', "", match.string)
                            infobox_features.append(feature_name)
                    
                    # ignore enclosed multiline double-braces
                    if re.search(r'{{',line) and not re.search(r'{{Infobox',line):
                        ignore += 1
                    if re.search(r'}}',line):
                        if not re.search(r'{{',line):
                            if not ignore:
                                break 
                        # ignore enclosed single-line double-braces
                        ignore -= 1
            if len(infobox_features) > 0:
                infobox_struct[subdir][filename] = infobox_features
    return make_infobox_dataset
    
def make_combined_dataset_pickle(raw_dir, clean_dir, target_file):
    """Take in a raw dir and a cleaned dir, and generate a combined pickle file
    that contains both infobox data and topic data."""
    infobox_struct = make_infobox_dataset(raw_dir)
    topic_struct = make_topic_dataset(clean_dir)
    
                
if __name__=='__main__':
    if (len(sys.argv) < 3) or (not os.path.exists(sys.argv[1])):
        print "Usage: article_cleaner.py src_dir target_dir. src_dir must exist."
    else:
        if len(sys.argv) > 3 and sys.argv[3] == 'topics':
            make_topic_dataset_pickle(sys.argv[1], sys.argv[2])
        else:
            make_clean_dataset_directory(sys.argv[1], sys.argv[2])