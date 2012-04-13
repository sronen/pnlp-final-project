import pprint # Used for formatting the output for viewing, not necessary for most code
from wikitools import wiki, api

SITE_MEDIAWIKI_URL = 'http://www.mediawiki.org/w/api.php'
SITE_WIKI_EN_URL = 'http://en.wikipedia.org/w/api.php'

site_en = wiki.Wiki(SITE_WIKI_EN_URL)

def get_article_other_languages(article_name, max_results=500):
	'''
	Get a list of all the other languages in which the given aritcle exists.
	The default number for max results, 500, is the maximum value for llimit.
	
	 '''
	params = {'action':'query',
    'prop':'langlinks',
    'titles':article_name,
	'lllimit':max_results,
	'redirect':''}
	
	req = api.APIRequest(site_en, params)
	res = req.query(querycontinue=False) # item from which the query continues
	
	langlinks = res['query']['pages'].items()[0][1]['langlinks']
	
	return [x['lang'] for x in langlinks]
	
}

if __name__ == "__main__":
	articles = ['Pizza']
	
	for article in articles:
		print article, '>>>', get_article_other_languages(article, max_results=500):
	
'''

req = api.APIRequest(site, params)
res = req.query(querycontinue=False)
pprint.pprint(res)

site_en = wiki.Wiki(SITE_WIKI_EN_URL)

params['prop']='langlinks'
pramas['titles']='Pizza'
params['titles']='Pizza'
params['lllimit']=500
params
params.pop('siteinfo')
params.pop('meta')
params.pop('siprop')
%paste
params
params['redirect']=''
params
%paste
site
site_en = wiki.Wiki('http://en.wikipedia.org/w/api.php')
req = api.APIRequest(site_en, params)
%paste
res
res['query']
res['query']['langlinks']
res['query']['langlink']
res['query']['pages']
res['query']['pages'].keys()
res['query']['pages'].keys()[0]
res['query']['pages'].keys()
res['query']['pages'].items()
res['query']['pages'].items()[0]
res['query']['pages'].items()[0]['langlinks']
res['query']['pages'].items()[0]['langlinks'].keys()
res['query']['pages'].items()
res['query']['pages'].items()[1]
res['query']['pages'].items()[0][1]
res['query']['pages'].items()[0][1]['langlinks']
langlinks = res['query']['pages'].items()[0][1]['langlinks']
langlinks
langlinks[0]
langlinks[0]['lang']
langs = [x['lang'] for x in langlinks]
langs
'en' in langs
'fr' in langs
'he' in langs
langs = [x['lang'] for x in langlinks]
langs
%history
'''