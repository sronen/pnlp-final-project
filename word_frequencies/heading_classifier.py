import nltk
import re
import codecs
import os
from nltk.corpus import stopwords
import sys, urllib2, string, time, threading
import pickle
import random
from nltk.corpus import wordnet as wn
from nltk.stem.wordnet import WordNetLemmatizer

            
def evaluate(filename, repeat=1, num_train_per_cat=20):
    """Test the accuracy for the results in the target file."""
    total = 0
    correct = 0
    
    for i in range(repeat):
        training_data, test_data = load_data(filename, num_train_per_cat)
        
        classifier = HeadingClassifier(training_data, feature_extractor)
        
        # could experiment with boosting?
        for (heading, bio_type) in test_data:
            total += 1
            if classifier.classify(heading) == bio_type:
                correct += 1

    print "Heading classifier on all data, results over " + str(repeat) + " runs: " + str(float(correct)/total)

    classifier.classifier.show_most_informative_features(50)
    return classifier
    
def load_data(filename, num_train_per_cat):
    """Get the training data from the target file with pickle.
    Infobox data is the data for only bios with infoboxes.
    Full data is the data for all bios."""
    
    f = open(filename, 'r')
    topic_struct = pickle.load(f)
    
    # data is formatted as dict<'biography_type', dict<'article_name', (list<'section_heading'>, list<'infobox_feature'>)>>
    # want to format as list<('section_heading', 'biography_type')>
    training_data = list()
    test_data = list()
    for bio_type, articles in topic_struct.items():
        article_list = articles.items()
        random.shuffle(article_list)
        
        for article_name, data in article_list[:num_train_per_cat]:
            for heading in data[0]:
                training_data.append((heading, bio_type))
        for article_name, data in article_list[num_train_per_cat:]:
            for heading in data[0]:
                test_data.append((heading, bio_type))
    return training_data, test_data
        
class HeadingClassifier():
    """Naive bayesian classifier that takes a list of section headings and
    tries to predict a biography category."""
    def __init__(self, golden_data, feature_extractor):
        self.feature_extractor = feature_extractor
        train_set = []
        
        for (section_headings, bio_type) in golden_data:
            featureset = self.feature_extractor(section_headings)
            train_set.append( (featureset, bio_type) )
            
        self.classifier = nltk.NaiveBayesClassifier.train(train_set)
    
    def classify(self, section_headings):
        featureset = self.feature_extractor(section_headings)
        return self.classifier.classify(featureset)
    
def feature_extractor(heading):
    """Extract features from a relation for the classifier."""
    features = dict()
    lmtzr = WordNetLemmatizer()

    features['heading_' + heading] = True
    features['heading_lower_' + heading.lower()] = True
    words = re.findall(r'\w+', heading, flags = re.UNICODE)
    for word in words:
        if word.lower() not in stopwords.words('english'):
            features[word] = True
            features[word.lower()] = True
            features[lmtzr.lemmatize(word).lower()] = True
            
    return features
    
if __name__ == '__main__':
    try:
        evaluate('../datasets/classifier_data.pkl', repeat=sys.argv[1])
    except IndexError:
	    evaluate('../datasets/classifier_data.pkl', repeat=1)

    