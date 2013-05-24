from wmf import dump

#This would probably come from the command line, but let's pretend.
#files = ["/dumps/enwiki/20110115/enwiki-20110115-pages-meta-history%s.xml.7z" % i for i in range(1, 16)]
#files = ["eswiki-20130429-pages-meta-history.xml.7z"]
files = ["enwiki-20130503-pages-meta-history2.xml-p000024118p000025000.bz2"]

def revAndUserCount(dumpIterator, page):
        count = 0
        users = set()
        for rev in page.readRevisions():
                count += 1
                users.add(rev.getContributor().getUsername())
        
        yield (page.getId(), count, len(users))

for pageId, revisionCount, userCount in dump.map(files, revAndUserCount, threads=3):
        print("\t".join(str(v) for v in [pageId, revisionCount, userCount]))