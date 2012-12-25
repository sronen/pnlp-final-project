# datasets/wikipedia_bio_lists

Folder Contents:
- people_on_english_wikipedia: 
	a) person_wiki.tsv.zip: list of people retrived from Freebase, 
	and their matching English Wikipedia names and ID.
	b) person_wiki_test.tsv: partial version of the above, for testing.
	c) head.tsv: header of person_wiki.tsv, for reference.

- people_in_langs:
	a) all_person_matched.tsv.zip: language edition + article name in each 
	language for people in person_wiki.tsv (~900k people on 12/25/2012)
	b) spanish_and_english_bios.tsv.zip: only people with articles in English
	and Spanish (~120k on 12/25/2012)


Instructions:
1) Copy person_wiki.tsv to the same folder as find_wiki_langlinks.py 
and wiki_article_meta.py. These are found in retrieve/.
2) Run find_wiki_langlinks.py. Output is a tab-then-||-separated file
with all languages that have an article about the people listed in 
person_wiki.tsv, and the article names in the respective languages.
3) Optional: Grep for the languages you want, e.g. "es||" for Spanish.
Will speed up the next script.
4) Run filter_specified_languages.py on the result. Output is a tab-then-||
separated file containing only the requested languages and article names.