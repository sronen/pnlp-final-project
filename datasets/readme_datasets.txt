# datasets/readme.txt

Datasets:
raw_featured_bios: contains featured bios from the 10 categories we used with full wikipedia markup.

plaintext_featured_bios: contains featured bios from the 10 categories we used. Mostly plain text, but they contain tokens like "&lt;h2&gt;" to signify headers, italics, bold, paragraph endings, and symbols. These also include all categories, such as references.

plaintext_featured_bios_uncat: containts all the plaintext bios in the same directory.

cleaned_featured_bios: contains featured bios from the 10 categories we used. These files are totally cleaned - they contain pure plain text of the paragraph content and heading info, and nothing else.

cleaned_lemmatized_featured_bios_uncat: cleaned and lemmatized, all files are in the same directory. This is used with Mallet.

classifier_data.pkl:
paragraph_data.pkl:
topics_pickle:

The following folders can be found under z_v1: 

on_featured_bios: these are cleaned versions of non-featured biographies of interesting people.

excluded_bios: contains bios from the 4 categories we didn't use. includes raw, plaintext, and cleaned versions.

sample_clean_corpora: TF*IDF stuff

