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

            
def evaluate(filename):
    """Test the accuracy for the results in the target file."""
    golden_data = load_golden_data(filename)
    
    num_times_to_repeat = 1
    
    correct = 0
    total = 0
    for i in range(num_times_to_repeat):
        random.shuffle(golden_data)
        
        num_total = len(golden_data)
        num_train = (num_total*2)/3
        num_test = num_total - num_train
        
        classifier = BiographyClassifier(golden_data[:num_train], feature_extractor)
        
        for (section_headings, bio_type) in golden_data[num_train:]:
            total += 1
            print classifier.classify(section_headings), ", ", bio_type
            if classifier.classify(section_headings) == bio_type:
                correct += 1

    print "Average results over " + str(num_times_to_repeat) + " runs:" + str(float(correct)/total)
          
def load_golden_data(filename):
    """Get the training data from the target file with pickle."""
    f = open(filename, 'r')
    topic_struct = pickle.load(f)
    
    # data is formatted as dict<'biography_type', dict<'article_name', list<'section_heading'>>>
    # want to format as list<(list<'section_headings'>, 'biography_type')>
    golden_data = list()
    for bio_type, articles in topic_struct.items():
        for article_name, section_headings in articles.items():
            tup = (section_headings, bio_type)
            golden_data.append(tup)
    return golden_data
        
class BiographyClassifier():
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
    
def feature_extractor(section_headings):
    """Extract features from a relation for the classifier."""
    features = dict()
    lmtzr = WordNetLemmatizer()
    for heading in section_headings:
        features['heading_' + heading] = True
        words = re.findall(r'\w+', heading, flags = re.UNICODE)
        for word in words:
            if word.lower() not in stopwords.words('english'):
                features[word] = True
                features[word.lower()] = True
                features[lmtzr.lemmatize(word).lower()] = True
    return features

    