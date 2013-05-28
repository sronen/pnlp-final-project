from os import listdir

from os.path import isfile, join

import codecs

#fout = codecs.open("blah.txt", "w", encoding='utf-8')
fout = codecs.open("blah.txt", "w")

mypath = "temp/"
#onlyfiles = [ f.decode('utf-8') for f in listdir(u'temp/') if isfile(join(mypath,f)) ]
onlyfiles = [ f for f in listdir(unicode(mypath)) if isfile(join(mypath,f)) ]

#for x in onlyfiles:
#	print x.encode('utf-8')

for x in onlyfiles:
	#newx = x if isinstance(x, unicode) else x.encode('utf-8')

	fout.write(x.encode('utf-8') + "\n")

fout.close()