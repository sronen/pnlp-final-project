from wikitools import wiki, api

SITE_MEDIAWIKI_URL = 'http://www.mediawiki.org/w/api.php'
SITE_WIKI_EN_URL = 'http://en.wikipedia.org/w/api.php'

# TODO: get plain text!

def get_article_other_languages(site, article_name, max_results=500):
	'''
	Get a list of all the other languages in which the given aritcle exists.
	The default number for max results, 500, is the maximum value for llimit.
	
	Example: http://en.wikipedia.org/w/api.php?action=query&prop=langlinks&titles=Pizza&lllimit=500&redirects=
	'''
	
	params = {'action':'query', 'prop':'langlinks', 'titles':article_name, \
	'lllimit':max_results, 'redirect':''}
	
	req = api.APIRequest(site_en, params)
	res = req.query(querycontinue=False) # item from which the query continues
	
	# 'res' is a big messy nested dictionary. The first tuple on 'pages' holds 
	# the 'lanklists' list in its second item. 
	langlinks = res['query']['pages'].items()[0][1]['langlinks']
	
	return [x['lang'] for x in langlinks]


def is_article_in_languages(site, article_name, lang_list):
	'''
	Return a list of (lang, True/False) tuples for each language in lang_list, indicating whether article_name exists in this language
	'''
	article_langs = get_article_other_languages(site, article_name)
	
	return [(lang, True if lang in article_langs else False) for lang in lang_list ]


if __name__ == "__main__":
	articles = ['David_Ben-Gurion', 'Tiger_Woods', 'Harry_Houdini', 'Barack_Obama']
	my_langs = ['fr', 'he']
	
	site_en = wiki.Wiki(SITE_WIKI_EN_URL)
	
	for article in articles:
		print article,
		article_langs = get_article_other_languages(site_en, article)
		print '>>>', len(article_langs), '>>>', \
			is_article_in_languages(site_en, article, my_langs)