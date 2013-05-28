#import easy to use xml parser called minidom:
from xml.dom.minidom import parseString
#all these imports are standard on most modern python implementations

def get_users(historydump, tagname):
    #open the xml file for reading:
    file = open(historydump,'r')
    #convert to string:
    data = file.read()
    #close file because we dont need it anymore:
    file.close()
    #parse the xml you got from the file
    dom = parseString(data)
    #retrieve the first xml tag (<tag>data</tag>) that the parser finds with name tagName:
    xmlTags = dom.getElementsByTagName(tagname)[0]
    for node in xmlTags:
        
    #strip off the tag (<tag>data</tag>  --->   data):
    xmlData=xmlTag.replace('<'+tagname+'>','').replace('</'+tagname+'>','')
    #print out the xml tag and data in this format: <tag>data</tag>
    print xmlTag
    #just print the data
    print xmlData



'''

    #GET RID OF NON-ARTICLES
    toremove = [namespace.text for namespace in \
                root[0][4].findall('{http://www.mediawiki.org/xml/export-0.6/}namespace')]
    print toremove
    removei = []
    for elt in toremove:
        for i in range(len(titles)):
            if str(elt) in titles[i]:
                removei.append(i)
    removei = list(set(removei))
    for x in reversed(removei):
        titles.pop(x)
        uniqueusers.pop(x)
        datecreated.pop(x)

'''


    '''
    for i in range(len(root.findall('{http://www.mediawiki.org/xml/export-0.6/}page'))):
        if root[i][1].text == '0':
            
            #TITLE: root[i][0] is the title
            titles.append(root[i][0].text)

            #DATE CREATED
            datecreated.append(root[i].find('{http://www.mediawiki.org/xml/export-0.6/}revision')[1].text)

            #LISTS OF EDITORS
            #root[i][j] is the level 'revision' would be on -- looks for that
            #root[i][j][2] is 'contributor'; root[i][j][2][0] is username or IP

            userlist.append([rev[2][0].text for rev in root[i].getiterator('{http://www.mediawiki.org/xml/export-0.6/}revision')])

            #EDITS PER DAY
            start = datetime.datetime.strptime(root[i].find('{http://www.mediawiki.org/xml/export-0.6/}revision')\
                                               [1].text, "%Y-%m-%dT%H:%M:%SZ").date()
            #should end date be the current date or the date of last edit?
            #this is currently the date of the last edit
            end = datetime.datetime.strptime(root[i][len(root[i])-1][1].text, "%Y-%m-%dT%H:%M:%SZ").date()
            if start == end:
                edits.append(len(root[i]))
            else:
                edits.append(len(root[i])/float((end-start).days))

            #PAGE SIZE
            sizes.append(root[i][len(root[i])-1].find(\
                '{http://www.mediawiki.org/xml/export-0.6/}text').get('bytes'))
    '''




##            for rev in page.getiterator('{http://www.mediawiki.org/xml/export-0.6/}revision'):
##                if rev[2][0] != None:
##                    users.append(rev[2][0].text)
##                if rev[2].find('{http://www.mediawiki.org/xml/export-0.6/}username' or '{http://www.mediawiki.org/xml/export-0.6/}ip') != None:
##                    users.append(rev[2].find('{http://www.mediawiki.org/xml/export-0.6/}username' or \
##                                             '{http://www.mediawiki.org/xml/export-0.6/}ip').text)
