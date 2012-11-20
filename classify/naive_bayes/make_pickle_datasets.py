def make_topic_dataset(src_dir):
    """Take in a dataset directory src_dir, which should have subdirectories that represent
    categories, and files in those subdirectories that are plaintext wikipedia articles.
    Clean those wikipedia articles return them."""
    listing = os.listdir(src_dir)
    topic_struct = dict()
    for subdir in listing:
        if os.path.isdir(src_dir + '/' + subdir):
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
    
def make_paragraph_dataset(src_dir):
    """Take in a dataset directory src_dir, which should have subdirectories that represent
    categories, and files in those subdirectories that are plaintext wikipedia articles.
    Clean those wikipedia articles return them."""
    listing = os.listdir(src_dir)
    paragraph_struct = dict()
    for subdir in listing:
        if os.path.isdir(src_dir + '/' + subdir):
            paragraph_struct[subdir] = dict()
            files = os.listdir(src_dir + '/' + subdir)
            for filename in files:
                orig_text = open(src_dir + '/' + subdir + '/' + filename).read().decode('utf-8')
                
                new_text = clean_plaintext_article(orig_text, True)
                lines = new_text.split("\n")
                
                current_h2 = 'Intro' # our artificial name for the heading at the start of the text
                current_h3 = None
                
                paragraph_struct[subdir][filename] = list()
                for line in lines:
                    if len(line) == 0:
                        continue
                    heading_match = re.search(r'&lt;h[23]&gt;.*?&lt;/h[23]&gt;', line)
                    if heading_match:
                        heading = heading_match.string
                        # find out if h2 or h3 before removing
                        is_h2 = ';h2&' in heading
                        heading = re.sub(r'&lt;h[23]&gt;', '', heading)
                        heading = re.sub(r'&lt;/?h[23]&gt;', '', heading)
                        heading = re.sub(r'&lt;.*?&gt;', '', heading)
                        heading = re.sub(r'&[^;\s]*?;', '', heading)
                        # update heading
                        if is_h2:
                            current_h2 = heading
                            current_h3 = None
                        else:
                            current_h3 = heading
                    paragraph_match = re.search(r'&lt;p&gt;.*?&lt;/p&gt;', line)
                    if paragraph_match:
                        paragraph = paragraph_match.string
                        paragraph = re.sub(r'&lt;p&gt; ', '', paragraph)
                        paragraph = re.sub(r'&lt;/p&gt;', '', paragraph)
                        paragraph = re.sub(r'&lt;.*?&gt;', '', paragraph)
                        paragraph = re.sub(r'&[^;\s]*?;', '', paragraph)
                        # add to paragraph struct
                        paragraph_struct[subdir][filename].append((current_h2, current_h3, paragraph))
                        
                """    
                topic_headings = re.findall(r'&lt;h[23]&gt;.*?&lt;/h[23]&gt;', new_text)
                topic_headings = [re.sub(r'&lt;h[23]&gt; ', '', h) for h in topic_headings]
                topic_headings = [re.sub(r'&lt;/?h[23]&gt;', '', h) for h in topic_headings]
                topic_headings = [re.sub(r'&lt;.*?&gt;', '', h) for h in topic_headings]
                topic_headings = [re.sub(r'&[^;\s]*?;', '', h) for h in topic_headings]
                paragraph_struct[subdir][filename] = topic_headings
                """
    return paragraph_struct
    
    
def make_infobox_dataset(src_dir):
    """Take in a raw dataset directory, and extract infobox data."""
    listing = os.listdir(src_dir)
    infobox_struct = dict()
    
    for subdir in listing:
        if os.path.isdir(src_dir + '/' + subdir):
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
                        # extract the features from the line
                        if len(line) > 0 and re.search(r'^\s*?\|', line):
                            match = re.search(r'^\s*?|\s?.*?\s*?=', line)
                            if match:
                                feature_name = re.sub(r'^\s*?\|\s?', "", match.string)
                                feature_name = re.sub(r'^\s*', "", feature_name)
                                feature_name = re.sub(r'=.*', "", feature_name)
                                feature_name = re.sub(r'\s*$', "", feature_name)
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
                infobox_struct[subdir][filename] = infobox_features
    return infobox_struct
    
def make_combined_dataset_pickle(raw_dir, clean_dir, target_file):
    """Take in a raw dir and a cleaned dir, and generate a combined pickle file
    that contains both infobox data and topic data."""
    infobox_struct = make_infobox_dataset(raw_dir)
    topic_struct = make_topic_dataset(clean_dir)
    combined_struct = dict()
    
    for bio_type, articles in topic_struct.items():
        combined_struct[bio_type] = dict()
        article_list = articles.items()
        for article_name, section_headings in article_list:
            if article_name in infobox_struct[bio_type]:
                infobox = infobox_struct[bio_type][article_name]
            else:
                infobox = []
            combined_struct[bio_type][article_name] = (section_headings, infobox)
    pickle.dump(combined_struct, open(target_file, 'w'))
    return combined_struct

if __name__=='__main__':
    if (len(sys.argv) < 3) or (not os.path.exists(sys.argv[1])):
        print "Usage: make_pickle_datasets.py src_dir . src_dir must exist."
    make_topic_dataset_pickle(sys.argv[1], sys.argv[2])