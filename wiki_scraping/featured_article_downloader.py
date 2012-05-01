import sys, urllib2, re, string, time, threading
from BeautifulSoup import BeautifulSoup
import os

def get_specific_wikipedia_article(wiki_url, markup=True):
    """
    Downloads a randomly selected Wikipedia article (via
    http://en.wikipedia.org/wiki/Special:Random) and strips out (most
    of) the formatting, links, etc. 

    This function is a bit simpler and less robust than the code that
    was used for the experiments in "Online VB for LDA."
    """

    articletitle = None
    failed = False
    try:
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
            base_url = 'http://en.wikipedia.org/w/index.php?title=Special:Export/%s&action=submit'
        else:
            base_url = 'http://en.wikipedia.org/w/api.php?action=query&format=xml&prop=extracts&titles=%s'
        
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

def get_featured_wikipedia_articles(dirname, markup=True):
    """
    Downloads n articles in parallel from Wikipedia and returns lists
    of their names and contents. Much faster than calling
    get_random_wikipedia_article() serially.
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
    t0 = time.time()

    get_featured_wikipedia_articles('markup_featured_bios', True)

    t1 = time.time()
    print 'took %f' % (t1 - t0)

if __name__ == '__main__':
    main()

