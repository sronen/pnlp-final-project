import sys, urllib2, re, string, time, threading
from BeautifulSoup import BeautifulSoup
import os, errno
import random

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

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



def get_new_language_versions_of_downloaded_articles(original_dirname, new_dirname, 
                                                    language='fr', markup=True, original_language='en'):
    """
    original_dirname should be a directory full of category folders, which are each full of articles
    where the filenames are Wikipedia_Article_Name.txt.

    This procedure will look up all the English articles, find the name of the corresponding French articles,
    and then download them and put them in new_dirname with the same directory structure.
    """
    if not os.path.exists(original_dirname):
        raise Exception("Original directory doesn't exist.")
    if not os.path.exists(new_dirname):
        mkdir_p(new_dirname);

    listing = os.listdir(original_dirname)
    for subdir in listing:
        if not os.path.isdir(original_dirname + '/' + subdir):
            continue
        if not os.path.exists(new_dirname + '/' + subdir):
            os.mkdir(new_dirname+ '/' + subdir)
        
        files = os.listdir(original_dirname + '/' + subdir)
        for filename in files:

            #eng_text = open(original_dirname + '/' + subdir + '/' + filename).read().decode('utf-8')

            original_url = 'http://' + original_language + '.wikipedia.org/wiki/' + urllib2.quote(urllib2.unquote(filename))

            if language == original_language:

                article_title = urllib2.quote(urllib2.unquote(filename))
                (article_text, article_title) = get_specific_wikipedia_article(original_url, markup, language, articletitle=article_title)
                newf = open(new_dirname + '/' + subdir + '/' + urllib2.unquote(filename), 'w')
                newf.write(article_text)

            else:
                
                try:
                    req = urllib2.Request(original_url, None, { 'User-Agent' : 'x'})
                    f = urllib2.urlopen(req)
                except (urllib2.HTTPError, urllib2.URLError):
                    continue

                re_result = re.search(r'<li class="interwiki-' + language + r'"><a href="(.*)" title="(.*)" lang=', f.read())
                if (re_result != None):
                    new_url = 'http:' + re_result.group(1)
                    new_title = re.search(r'/wiki/(.*)', new_url).group(1)
                    result = get_specific_wikipedia_article(new_url, markup, language, articletitle=new_title)

                    if result != None:
                        (article_text, article_title) = result
                        article_title = urllib2.unquote(article_title).replace('/', '_')
                        f = open(new_dirname + '/' + subdir + '/' + article_title, 'w')
                        f.write(article_text)
                    else:
                        print 'Failed to download ',article_title



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
    """
class WikiThread(threading.Thread):
    articles = list()
    articlenames = list()
    lock = threading.Lock()

    def __init__(self, language, article_title):
        self.article_title = article_title
        self.language = self.language

    def run(self):
        result = get_specific_wikipedia_article(None, False, self.language, articletitle=self.article_title)
        if result != None:
            (article_text, article_title) = result
            article_title = article_title.replace('/', '_')
            f = open(new_dir + '/' + article_title, 'w')
            f.write(article_text)
        else:
            print "fail"
    """
    
def download_articles_from_list(filename, new_dirname, language='en', direction=1):
    # 1: download all, forward
    # 2,3: download halves
    # 4-7: download quarters
    # 10-17: download eighths
    print "Downloading articles"
    if not os.path.exists(new_dirname):
        os.makedirs(new_dirname)
    maxthreads = 8

    f = open(filename, 'r')
    names = f.read().split('\n')
    f.close()
    num = len(names)

    if direction == 'random':
        for i in range(len(names)*4):
            download(new_dirname, language, names[int(random.random()*len(names))])
    else:
        direction = int(direction)

        if direction == 1:
            for i in range(len(names)):
                download(new_dirname, language, names[i])
                print "%d / %d" %(i, num)
        elif direction == 2 or direction == 3:
            for i in range((direction-2)*len(names)/2, (direction-1)*len(names)/2, 1):
                download(new_dirname, language, names[i])
                print "language: %s, direction: %d, %d / %d" %(language, direction, i, num)
        elif direction => 4 or direction <= 7:
            for i in range((direction-4)*len(names)/4, (direction-3)*len(names)/4, 1):
                download(new_dirname, language, names[i])
                print "language: %s, direction: %d, %d / %d" %(language, direction, i, num)
        elif direction == str(-2):
            for i in range(len(names)/2, 0,-1):
                download(new_dirname, language, names[i])
                print "%d / %d" %(i, num)
        
        elif direction >= 10:
            dire = direction - 10
            for i in range(dire*len(names)/8, (dire+1)*len(names)/8, 1):
                download(new_dirname, language, names[i])
                print "language: %s, direction: %d, %d / %d" %(language, direction, i, num)

def download(new_dirname, language, line):
    if not os.path.exists(new_dirname + '/' + line):
        try:
            article_title = urllib2.quote(urllib2.unquote(line))
            (article_text, article_title) = get_specific_wikipedia_article(None, False, language, articletitle=article_title)
            newf = open(new_dirname + '/' + urllib2.unquote(article_title), 'w')
            newf.write(article_text)
            newf.close()
            print 'downloaded %s' % article_title
        except Exception as e:
            print 'Error: %s' % article_title
            import traceback
            traceback.print_exc()



def main():
    if len(sys.argv) > 2 and sys.argv[1] == 'list':
        download_articles_from_list(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
        return
    try:
        if len(sys.argv) > 3:
            markup = False
            old_lang = 'en'
            if len(sys.argv) > 4:
                markup = bool(int(sys.argv[4]))
            if len(sys.argv) > 5:
                old_lang = sys.argv[5]
            get_new_language_versions_of_downloaded_articles(sys.argv[1], sys.argv[2], sys.argv[3], markup, old_lang)
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

