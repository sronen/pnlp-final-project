import sys, urllib2, re, string, time, threading
from BeautifulSoup import BeautifulSoup
import os

def get_specific_wikipedia_article(wiki_url, markup=True, language='en', articletitle=None):  
    """
    Gets a specific wikipedia article, given the url.
    Note: you should really pass the title if you are working with non-English.
    """
    failed = False
    try:
        if articletitle == None:
            req = urllib2.Request(wiki_url,
                                  None, { 'User-Agent' : 'x'})
            f = urllib2.urlopen(req)

            while not articletitle:
                line = f.readline()
                result = re.search(r'title="Edit this page" href="/w/index.php\?title=(.*)\&amp;action=edit" /\>', line)
                if (result):
                    articletitle = result.group(1)
                    break
                elif (len(line) < 1):
                    return None

        if markup:
            base_url = 'http://' + language + '.wikipedia.org/w/index.php?title=Special:Export/%s&action=submit'
        else:
            base_url = 'http://' + language + '.wikipedia.org/w/api.php?action=query&format=xml&prop=extracts&titles=%s'
        
        req = urllib2.Request(base_url % (articletitle),
                              None, { 'User-Agent' : 'x'})
        f = urllib2.urlopen(req)
        all = f.read()
    except (urllib2.HTTPError, urllib2.URLError):
        print 'oops. there was a failure downloading %s. retrying...' \
            % articletitle
        failed = True
        return None
    #print 'downloaded %s. parsing...' % articletitle
    

    try:
        # extract the text section of the xml. this is the wiki markup text.
        if markup:
            all = re.search(r'<text.*?>(.*)</text', all, flags=re.DOTALL).group(1)
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
        else:
            all = re.search(r'<extract.*?>(.*)</extract', all, flags=re.DOTALL).group(1)
    except:
        # Something went wrong, try again. (This is bad coding practice.)
        print 'oops. there was a failure parsing %s.' \
            % articletitle
        return None

    return(all, articletitle)

class WikiThread(threading.Thread):
    articles = list()
    articlenames = list()
    lock = threading.Lock()

    def run(self):
        result = get_specific_wikipedia_article(url)
        if result != None:
            (article_text, article_title) = result
            article_title = article_title.replace('/', '_')
            f = open(new_dir + '/' + article_title, 'w')
            f.write(article_text)
        else:
            print "fail"

def get_french_versions_of_downloaded_articles(english_dirname, french_dirname, markup=True):
    """
    english_dirname should be a directory full of category folders, which are each full of articles
    where the filenames are Wikipedia_Article_Name.txt.

    This procedure will look up all the English articles, find the name of the corresponding French articles,
    and then download them and put them in french_dirname with the same directory structure.
    """
    if not os.path.exists(english_dirname):
        raise Exception("English directory doesn't exist.")
    if not os.path.exists(french_dirname):
        os.mkdir(french_dirname);

    listing = os.listdir(english_dirname)
    for subdir in listing:
        if not os.path.isdir(english_dirname + '/' + subdir):
            continue
        if not os.path.exists(french_dirname + '/' + subdir):
            os.mkdir(french_dirname+ '/' + subdir)
        
        files = os.listdir(english_dirname + '/' + subdir)
        for filename in files:

            #eng_text = open(english_dirname + '/' + subdir + '/' + filename).read().decode('utf-8')

            english_url = 'http://en.wikipedia.org/wiki/' + filename
            try:
                req = urllib2.Request(english_url, None, { 'User-Agent' : 'x'})
                f = urllib2.urlopen(req)
            except (urllib2.HTTPError, urllib2.URLError):
                continue

            re_result = re.search(r'<li class="interwiki-fr"><a href="(.*)" title="(.*)" lang=', f.read())
            if (re_result != None):
                french_url = 'http:' + re_result.group(1)
                french_title = re.search(r'/wiki/(.*)', french_url).group(1)
                result = get_specific_wikipedia_article(french_url, markup, language='fr', articletitle=french_title)

                if result != None:
                    (article_text, article_title) = result
                    article_title = article_title.replace('/', '_')
                    f = open(french_dirname + '/' + subdir + '/' + article_title, 'w')
                    f.write(article_text)
                else:
                    print 'Failed to download ',article_title


def get_featured_french_articles(dirname, markup=True):
    pass

def get_featured_wikipedia_articles(dirname, markup=True):
    """
    Get the featured articles from Wikipedia
    """

    """All biographies have the following structure:
    <h3>
      <span id="x_biographies">X biographies</span>
    </h3>
    <p>
      <span class="featured_article_metadata has_been_on_main_page">
        <a href="/wiki/Richard_Barre" title=Richard Barre">Richard Barre</a>
      </span>
      --or--
      <a href="/wiki/Richard_Barre" title=Richard Barre">Richard Barre</a>
      
      ^^one of the two above patterns, repeated
    </p>"""
    featured_url = 'http://en.wikipedia.org/wiki/Wikipedia:Featured_articles'
    try:
        req = urllib2.Request(featured_url,
                              None, { 'User-Agent' : 'x'})
        f = urllib2.urlopen(req)
        doc = f.readlines()
    except (urllib2.HTTPError, urllib2.URLError):
        print 'oops. there was a failure downloading'

    if not os.path.exists(dirname):
        os.makedirs(dirname)

    soup = BeautifulSoup(''.join(doc))
    sections = soup.findAll('span', id=re.compile('.*biographies'))
    for section in sections:
        section_name = section.text
        new_dir = dirname + '/' + section_name
        if not os.path.exists(new_dir):
            os.makedirs(new_dir)
        
        all_subtext = section.next.next.next.__repr__()
        relative_url_list = re.findall('href="[^"]*"', all_subtext)
        for rel_url in relative_url_list:
            url = 'http://en.wikipedia.org' + rel_url[6:-1]
            
            result = get_specific_wikipedia_article(url, markup)
            if result != None:
                (article_text, article_title) = result
                article_title = article_title.replace('/', '_')
                f = open(new_dir + '/' + article_title, 'w')
                f.write(article_text)
    """
    maxthreads = 8
    WikiThread.articles = list()
    WikiThread.articlenames = list()
    wtlist = list()
    for i in range(0, n, maxthreads):
        print 'downloaded %d/%d articles...' % (i, n)
        for j in range(i, min(i+maxthreads, n)):
            wtlist.append(WikiThread())
            wtlist[len(wtlist)-1].start()
        for j in range(i, min(i+maxthreads, n)):
            wtlist[j].join()
    """

def main():
    try:
        if sys.argv[1] == 'french':
            if len(sys.argv) > 3:
                markup = False
                if len(sys.argv) > 4:
                    markup = bool(int(sys.argv[4]))
                get_french_versions_of_downloaded_articles(sys.argv[2], sys.argv[3], False)
            else:
                print 'usage: french english_dirname french_dirname'
            return
        else:
            corpus_root_path = sys.argv[1]
    except IndexError:
        corpus_root_path = 'markup_featured_bios'

    t0 = time.time()

    get_featured_wikipedia_articles(corpus_root_path, False)

    t1 = time.time()
    print 'took %f' % (t1 - t0)

if __name__ == '__main__':
    main()

