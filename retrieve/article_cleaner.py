import sys, re, string, time, os, pickle

def clean_plaintext_article(text, extract=False, language='en'):
    """As input, takes the plain text from a wikipedia article that we got from
    the Wikipedia API's extract field, which isn't quite plain text, and removes the
    remaining HTML tags."""
    try:
        if language=='en':
            end_phrases = [r'[Ee]xternal [Ll]inks', r'[Ee]xternal [Ll]inks and [Rr]eferences', r'Notes',
                            r'Footnotes', r'Further reading', r'[Ss]ource', r'[Rr]eferences', r'[Ss]ee [Aa]lso']
            inside_lt = []
        elif language=='fr':
            end_phrases = [r'Notes et [Rr]\xc3\xa9f\xc3\xa9rences', r'Voir aussi', r'R\xc3\xa9f\xc3\xa9rences', 
                            r'[Ll]iens [Ee]xternes',
                            r'Notes', r'[Aa]nnexe', r'[Aa]nnexes', r'[Ss]ource(s)?', r'[Bb]ibliographie', 
                            r'[Ll]ien [Ee]xterne']
            inside_lts = [r'ul\s*id=&quot;bandeau-portail&quot;\s*class=&quot;bandeau-portail&quot;']
        else:
            raise Exception('language ' + language + ' not supported yet.')

        for end_phrase in end_phrases:
            text = re.sub(r'&lt;h[23]&gt;\s*' + end_phrase + r'\s*&lt;/h[23]&gt;.*', '', text, flags=re.DOTALL)
        for inside_lt in inside_lts:
            text = re.sub(r'&lt;' + inside_lt + r'&gt;.*', '', text, flags=re.DOTALL)
        text = re.sub(r'&amp;amp;', '&', text) # display ampersands properly
        if extract:
            return text
        text = re.sub(r'&lt;.*?&gt;', '', text) # remove all html tags
        text = re.sub(r'&[^;\s]*?;', '', text) # remove all other markings, e.g. &quot;
    except:
        # Something went wrong, try again. (This is bad coding practice.)
        print 'oops. there was a failure parsing %s.' % articletitle
        return "error"
    return text
 
def make_clean_dataset_directory(src_dir, target_dir, language='en'):
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
            
            new_text = clean_plaintext_article(orig_text, False, language).encode('utf-8')
            f = open(target_dir + '/' + subdir + '/' + filename, 'w')
            f.write(new_text)
            

                
if __name__=='__main__':
    if (len(sys.argv) < 3) or (not os.path.exists(sys.argv[1])):
        print "Usage: article_cleaner.py src_dir target_dir [language]. src_dir must exist. For lang, use 'en' or 'fr'."
    else:
        if len(sys.argv) > 3:
            make_clean_dataset_directory(sys.argv[1], sys.argv[2], sys.argv[3])
        else:
            make_clean_dataset_directory(sys.argv[1], sys.argv[2])