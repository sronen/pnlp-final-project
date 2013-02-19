We use one word names for categories. Text in parentheses is not part of the category's name. In alphabetical order: 

Art	(incl. architecure)
Business
Education	(students and professors, incl. academia)
Explorers
Humanities	(and social sciences)
Law	(and crime)
Literature	(incl. journalism and adapations of narrative to other media, such as comics -> animated film)
Media	(incl. TV, film, popular culture such as reality or celebrity news -- hard to distinguish)
Music	(popular and classical)
Personal
Politics	(two main categories: elections/goverment and revolutions)
Religion	(mostly Catholicism)
Royalty	(two main categories: personal life and wars)
science	(and technology)
Sports
Warfare	(and military)

Process:
1) Run label_topics.py after labeling to convert topic IDs to number.
2) Run run_merge.R to generate an average topic share for language.
3)  


File naming convention:
<lang>-<classification><fold>-<content>
e.g., en-31-topic-names means English topic names for the 3rd classification, in its 1st fold 

Structure:
topic-keys: each file is a list of top 100 words per identified topic
topic-names: each file maps topic numbers to topic names. The orig/ subfolder contains my on-the-fly classification - a little more detailed.
topic-prop: proportions of topics for each article, topics identified by number.
topic-prop-names: proportions of topics for each article, topics identified by name

Notes:
1) en-20, topic 4 (also en-22, topic 1; en-31, t 13) which combines literature with what seems to be adaptations of literature to other media (comics -> anime, screenplay, etc) was classified as Literature .
2) en-21, topic 13, classified as Personal a little different than the standard Personal category. Occurs in other folds as well.
3) en-30, topic 27: Ignored. combines Literature with culture/personal.
3) es-12, topics 23,29 and es-22 topic 27: classified as Personal despite some doubts (words like Cielo (=sky), colors, etc.). There were other occurences as well.
4) es-21 topic 22: ignored - balanced combination of business and technology.
5) es-30 topic 21: classified as "Warfare"; moslty about vehicles (aircraft, ships, cars) for what seems like military use.


Missing Featured Articles:
1) Files ending with FA are the missing featured articles we classifed later
2) "Fascismo" was removed from the FA files -- not a bio
3) "Aristóteles" was removed from the FA files into a files of its own - not a FA (it is one of the top ten bios in Spanish)
4) Still missing (as of 2/19/2013): 
	English: "AC/DC"
	Spanish: "George Edward Bonsor Saint Martin", "Tutankamon", "Joaquín Sabina", "Elizabeth Bowes-Lyon"   