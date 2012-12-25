# -*- coding: utf-8 -*-
import sys
from collections import defaultdict

import httplib
import urllib, urllib2, simplejson
from wikitools import wiki, api

'''
Helper module for querying Wikipedia for article metadata.
This module uses two alternative implementations: a homegrown one (default, 
provides better support for non-English editions) and a wikitools-based one.
The two implementations can be alternated 

Performance wise, it makes sense to:
- Use find_articles_languages() to get langs and names for all articles in all 
  languages
- For each language edition, prepare a list of all articles in it.
- Call find_articles_length() separately on the articles of each language to get
  their lengths.
'''

# Pick query implemetation:
USE_HOMEGROWN_QUERY_IMP = True

MEDIAWIKI_API_URL = 'http://www.mediawiki.org/w/api.php'

# use Wikipedia Edition language code, e.g., 'en' or 'de' 
WIKIPEDIA_API_URL = 'http://%s.wikipedia.org/w/api.php'

# maximum number of languages to return (Wikipedia doesn't allow >500)
LLLIMIT_MAX_VALUE = 500

def _query_using_urllib(wiki_edition_api_url, params):
	'''
	Query implemented using urllib and simplejson 
	'''
	params['format'] = 'json' # ask for result in JSON format
	req = urllib2.Request(url=wiki_edition_api_url, data=urllib.urlencode(params))
	res = urllib2.urlopen(req)
	
	json_string = res.read()
	json_dic = simplejson.loads(json_string)
	
	return json_dic
	

def _query_using_wikitools(wiki_edition_api_url, params):
	'''
	Query implemented using wikitools.
	Note: wiki.Wiki fails on some Wikipedia editions (e.g, fr, he, tr) due to
	encoding issues.
	'''
	site = wiki.Wiki(wiki_edition_api_url) # Initialize Wiki API
	
	req = api.APIRequest(site, params)
	res = req.query(querycontinue=False) # item from which the query continues 
	
	return res


def _query_wikipedia_metadata(articles, wiki_lang, params):
	'''
	Query the given articles on the given language edition using the given
	parameters, and return the result as a Python dictionary.
	'''
	# Set debug level
	httplib.HTTPConnection.debuglevel = 1 
	
	# Set base URL, article title to look for, and action type  
	wiki_site = WIKIPEDIA_API_URL % wiki_lang
	article_list = '|'.join([article.encode('utf-8') for article in articles])
	params['titles'] = article_list
	params['action'] = 'query'
	
	try:
		# Choose implementation
		if USE_HOMEGROWN_QUERY_IMP==True:
			res = _query_using_urllib(wiki_site, params) 
		else:
			res = _query_using_wikitools(wiki_site, params) 
	except:
		print "Exception logging to %s: %s" % (wiki_lang, sys.exc_info()[0])
		return None
		
	pages = res['query']['pages'].items() # 'json_dic' is a messy nested dictionary
	
	return pages
	

def find_articles_languages(articles, orig_lang='en'):
	'''
	Return a dictionary whose key is the article title in the original language
	and whose values are a dictionary with the codes for the language editions
	that have a version of this article (key) and its name in each edition 
	(value). Thus for each item in the returned dictionary, keys() lists 
	language editions, and values() lists names in different languages.
	E.g., {'en':'Peace', 'es':'Paz', 'it':'Pace'}.
	--If you get awkward results for an article name, try to replace spaces 
	  with underscores in passed values. 
	'''
	params = {'prop':'langlinks', 'lllimit':LLLIMIT_MAX_VALUE, 'redirects':''}
	
	pages = _query_wikipedia_metadata(articles, orig_lang, params)
	if pages==None:
		return None
	
	# extract language information
	article_in_languages = defaultdict(defaultdict)
	
	# Each item on 'pages' represents a different person. 
	# 'langlinks' is a list with a dictionary for each language edition.
	for i, page in enumerate(pages):
		langs_and_titles = {}
		
		# Check if article exists and get its title
		orig_article_title = page[1]['title']
		if page[0]=='-1':
			# Name not found in original edition, move to next article
			print ">>> %s not found in language \'%s\'!" % \
				(orig_article_title, orig_lang)
			continue
			
		try:
			langlinks = page[1]['langlinks']
			
			# Get the lanugages along with the article name in each language
			langs_and_titles = { x['lang']:x['*'] for x in langlinks }
			#print '>>>', orig_article_title
			#print langs_and_titles
		
		except KeyError:
			# No langlinks means aricle doesn't exist in other languages
			# print ">>> %s exists only in language \'%s\'!" % \
			#	(orig_article_title, orig_lang) # debug
			pass
		
		# add the original language and original name
		langs_and_titles[orig_lang] = orig_article_title
		
		# add metadata for this article to the main dictionary, using
		# name in original language as key
		article_in_languages[orig_article_title] = langs_and_titles 
		
	return article_in_languages if article_in_languages else None

	
def find_articles_length(articles, wiki_lang='en'):
	'''
	Return a dictionary whose keys are article names and values are article sizes
	(in bytes/characters) of the latest revision of this article.	
	'''
	params = {'prop':'revisions', 'rvprop':'size', 'redirects':''}
	
	pages = _query_wikipedia_metadata(articles, wiki_lang, params)
	if pages==None:
		return None
	
	# extract language information
	article_sizes = defaultdict(defaultdict)
	
	# Each item on 'pages' represents a different person. 
	# 'langlinks' is a list with a dictionary for each language edition.
	for i, page in enumerate(pages):
		try:
			orig_article_title = page[1]['title']
			revisions = page[1]['revisions']
			article_length = page[1]['revisions'][0]['size']
			
			# add metadata for this article to the main dictionary, using
			# name in original language as key
			article_sizes[orig_article_title] = article_length 
		except KeyError:
			# article_name couldn't be found for this language, go to next item 
			print ">>> %s not found in language \'%s\'!" % \
				(orig_article_title, wiki_lang)
			pass
	
	return article_sizes if article_sizes else None
	

def find_first_revision_stats(article, wiki_lang='en'):
	'''
	Return the date, time, and name of the editor for the first revision of the
	given article. Due to Wikipedia API limitations, the query can handle only
	one article at a time.
	'''
	params = {'prop':'revisions', 'rvprop':'timestamp', 'rvdir':'newer', 'rvlimit':1, 'redirects':''}
	
	pages = _query_wikipedia_metadata([article], wiki_lang, params)
	if pages==None:
		return None
	
	page = pages[0] # only one returned item for now
	
	if page[0]=='-1':
		# Name not found in original edition
		print ">>> %s not found in language \'%s\'!" % \
			(article, wiki_lang)
		return None
	
	try:
		title = page[1]['title']
		timestamp = page[1]['revisions'][0]['timestamp']
		date, time = timestamp.rstrip('Z').split('T')
	except KeyError, IndexError:
		print ">>> Unexpected structure for %s in lang \'%s\'!" % \
			(article, wiki_lang)
	
	return {title: {'date':date, 'time':time}}


def is_article_in_languages(site, article_name, lang_list):
	'''
	TODO: update to match changes to the rest of the code!
	Return a list of (lang, True/False) tuples for each language in lang_list,
	indicating whether article_name exists in this language
	'''
	article_langs = get_article_other_languages(site, article_name)
	
	return [(lang, True if lang in article_langs else False) for lang in lang_list ]


if __name__ == "__main__":
	#articles = ['David Ben-Gurion', 'TigerXX Woods', 'Cantinflas', 
	#	'Steffi Graf', 'Barack Obama', 'Orel Dgani']
	#articles = ['Cantinflas', 'TigerXX_Woods', 'Orel_Dgani']
	#articles = ['Augusto Pinochet']
	articles = ['David Jason']
	print find_first_revision_stats('David Jason')

	try:
		orig_lang = sys.argv[1]
	except IndexError:
		orig_lang = 'en'
	
	langs = find_articles_languages(articles, orig_lang)
	print langs
	
	# TODO: improve test for length. 
	# Should test multiple articles at the same time
	lengths = defaultdict(defaultdict)
	# Wikipedia returns the normalized form of names, e.g., w/o underscores
	article_name_orig = 'Cantinflas'
	articles_for_size = langs[article_name_orig]
	
	# The following code work with all editions when called from a shell,
	# but not when running as part of a script this script
	for lang, article_name_translated in articles_for_size.iteritems():
		print lang,
		article_length = find_articles_length([article_name_translated], lang)
		if article_length!=None:
			lengths[lang] = article_length
			print article_length # print article name and length
	