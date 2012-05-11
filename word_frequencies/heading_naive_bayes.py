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

            
def evaluate(filename, topics_list=['Transport biographies',\
           'Biology biographies', 'Physics and astronomy biographies',\
           'Law biographies'], exclude=True):
    """Test the accuracy for the results in the target file."""
    num_times_to_repeat = 10
    
    correct = 0
    total = 0
    for i in range(num_times_to_repeat):
        training_data, test_data = load_data(filename, 20, topics_list, exclude)
        
        classifier = BiographyClassifier(training_data, feature_extractor)
        
        for (section_headings, bio_type) in test_data:
            total += 1

            if classifier.classify(section_headings) == bio_type:
                correct += 1
            else:
                pass
                #print "Misclassified", bio_type, "as", classifier.classify(section_headings)

    print "Average results over " + str(num_times_to_repeat) + " runs:" + str(float(correct)/total)
          
def load_data(filename, num_train_per_cat, topics_list=[], exclude_topics_in_list=True):
    """Get the training data from the target file with pickle."""
    f = open(filename, 'r')
    topic_struct = pickle.load(f)
    
    # data is formatted as dict<'biography_type', dict<'article_name', list<'section_heading'>>>
    # want to format as list<(list<'section_headings'>, 'biography_type')>
    training_data = list()
    test_data = list()
    for bio_type, articles in topic_struct.items():
        if ((exclude_topics_in_list and (bio_type not in topics_list)) or \
               ((not exclude_topics_in_list) and (bio_type in topics_list))):
            article_list = articles.items()
            random.shuffle(article_list)
            
            for article_name, section_headings in article_list[:num_train_per_cat]:
                training_data.append((section_headings, bio_type))
            for article_name, section_headings in article_list[num_train_per_cat:]:
                test_data.append((section_headings, bio_type))
    return training_data, test_data
        
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
        features['heading_lower_' + heading.lower()] = True
        words = re.findall(r'\w+', heading, flags = re.UNICODE)
        for word in words:
            if word.lower() not in stopwords.words('english'):
                features[word] = True
                features[word.lower()] = True
                features[lmtzr.lemmatize(word).lower()] = True
    return features
    
if __name__ == '__main__':
    evaluate('../datasets/topics_pickle')

    