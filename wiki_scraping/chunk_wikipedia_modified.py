'''
Rob's code
'''

import nltk
import re

def chunk_wikitext(text):
    text = nltk.clean_html(text)
    text = re.sub(r'\[\[.*?:.*?\]\]', '', text)    # remove interwiki links
    template_depth = 0
    in_link = in_ext_link = False
    link_words = []
    pieces = []
    headers = []
    for word in nltk.wordpunct_tokenize(text):
        # skip everything in template braces
        if '{{' in word:
            template_depth += 1
        elif '}}' in word:
            template_depth -= 1
        elif template_depth == 0:
            # detect links
            if '[[' in word:
                in_link = True
            elif ']]' in word:
                # at the end of a link, output it as a named entity chunk
                if link_words:
                    #pieces.append(nltk.Tree('NE', link_words))
                    pieces.extend(link_words) # add words to list
                    link_words = []
                    in_link = False
            elif '[' in word:
                # start over if the link has | marking an alternate name
                in_ext_link = True
            elif in_ext_link and ']' in word:
                in_ext_link = False
            elif '|' in word and in_link:
                link_words = []
            else:
                if in_link:
                    link_words.append(word)
                elif not in_ext_link:
                    pieces.append(word)
    return ' '.join(pieces)

if __name__ == '__main__':
    #a = chunk_wikitext(open('articles/Pigeon_photography.txt').read().decode('utf-8'))
    a = chunk_wikitext(open('../HW4/pnlp-wikipedia-relations/articles/Blackbeard.txt').read().decode('utf-8'))
    print a.encode('utf-8')
	#print unicode(a).encode('utf-8')
    #print ' '.join(unicode(a))
