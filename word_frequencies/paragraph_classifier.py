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

            
def evaluate(filename, repeat=1, num_train_per_cat=100):
    """Test the accuracy for the results in the target file."""
    total = 0
    correct = 0
    
    for i in range(repeat):
        training_data, test_data = load_data(filename, num_train_per_cat)
        
        classifier = ParagraphClassifier(training_data, feature_extractor)
        
        for (data, bio_type) in test_data:
            total += 1
            if classifier.classify(data) == bio_type:
                correct += 1

    print "Paragraph classifier on all data, results over " + str(repeat) + " runs: " + str(float(correct)/total)

    classifier.classifier.show_most_informative_features(50)
    return classifier
    
def get_classifier(filename):
    training_data, test_data = load_data(filename, 999999)
    classifier = HeadingClassifier(training_data, feature_extractor)
    # do classifier.classifier.prob('Warfare biographies') to get the probability
    # that this heading is from warfare biographies.
    # To get a histogram for a given heading name:
    # probdist = classifier.classifer.prob_classify(classifier.feature_extractor('Background and family')
    # print zip(a.samples(), [a.prob(h) for h in a.samples()])
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
        
        for article_name, data_list in article_list[:num_train_per_cat]: 
            for data in data_list:
                training_data.append((data, bio_type))
        for article_name, data_list in article_list[num_train_per_cat:]:
            for data in data_list:
                test_data.append((data, bio_type))
    return training_data, test_data
        
class ParagraphClassifier():
    """Naive bayesian classifier that takes a list of section headings and
    tries to predict a biography category."""
    def __init__(self, golden_data, feature_extractor):
        self.feature_extractor = feature_extractor
        train_set = []
        
        for (data, bio_type) in golden_data:
            featureset = self.feature_extractor(data)
            train_set.append( (featureset, bio_type) )
            
        self.classifier = nltk.NaiveBayesClassifier.train(train_set)
    
    def classify(self, data):
        featureset = self.feature_extractor(data)
        return self.classifier.classify(featureset)
    
def feature_extractor(data):
    """Extract features from a relation for the classifier."""
    features = dict()
    lmtzr = WordNetLemmatizer()

    h2, h3, paragraph = data
    
    features['h2_' + h2.lower()] = True
    for word in h2.split(' '):
        features['h2word_' + word.lower()] = True
    features['h_' + h2.lower()] = True
    for word in h2.split(' '):
        features['hword_' + word.lower()] = True

    if h3 != None:    
        features['h3_' + h3.lower()] = True
        for word in h3.split(' '):
            features['h3word_' + word.lower()] = True
        features['h_' + h3.lower()] = True
        for word in h3.split(' '):
            features['hword_' + word.lower()] = True
        
    for word in nltk.wordpunct_tokenize(paragraph):
        if word not in stopwords.words('english') and len(word) > 1:
            features[word] = True
            features['lower_' + word.lower()] = True
            features['lmtzr_' + lmtzr.lemmatize(word).lower()] = True
    return features
    
if __name__ == '__main__':
    try:
        evaluate('../datasets/paragraph_data.pkl', repeat=sys.argv[1])
    except IndexError:
	    evaluate('../datasets/paragraph_data.pkl', repeat=1)

    