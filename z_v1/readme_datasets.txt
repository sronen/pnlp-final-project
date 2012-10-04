# datasets/readme.txt

Datasets:
raw_featured_bios: contains featured bios from the 10 categories we used with full wikipedia markup.

plaintext_featured_bios: contains featured bios from the 10 categories we used. Mostly plain text, but they contain tokens like "&lt;h2&gt;" to signify headers, italics, bold, paragraph endings, and symbols. These also include all categories, such as references.

cleaned_featured_bios: contains featured bios from the 10 categories we used. These files are totally cleaned - they contain pure plain text of the paragraph content and heading info, and nothing else.

non_featured_bios: these are cleaned versions of non-featured biographies of interesting people.

excluded_bios: contains bios from the 4 categories we didn't use. includes raw, plaintext, and cleaned versions.

sample_clean_corpora: TF*IDF stuff


classifier_data.pkl:
topics_pickle: