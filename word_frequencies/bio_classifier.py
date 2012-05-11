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
    boosting_correct = 0
    all_total = 0
    
    full_both_correct = 0
    both_correct = 0
    infobox_total = 0
    
    for i in range(repeat):
        infobox_training_data, infobox_test_data, full_training_data, full_test_data = load_data(filename, num_train_per_cat)
        
        headings_classifier = BiographyClassifier(full_training_data, heading_feature_extractor)
        both_classifier = BiographyClassifier(infobox_training_data, full_feature_extractor)
        
        # could experiment with boosting?
        for (data, bio_type) in full_test_data:
            all_total += 1
            if both_classifier.classify(data) == bio_type:
                full_both_correct += 1
                
            if len(data[1]) > 0:
                infobox_total += 1
                if both_classifier.classify(data) == bio_type:
                    both_correct += 1
                    boosting_correct += 1
            else:
                if headings_classifier.classify(data) == bio_type:
                    boosting_correct += 1

    print "Boosting classifier on all data, results over " + str(repeat) + " runs: " + str(float(boosting_correct)/all_total)
    print "Full classifier on all data, results over " + str(repeat) + " runs: " + str(float(full_both_correct)/all_total)
    print "Full classifier on infobox data, results over " + str(repeat) + " runs: " + str(float(both_correct)/infobox_total)

    headings_classifier.classifier.show_most_informative_features(50)
    both_classifier.classifier.show_most_informative_features(50)
    
def load_data(filename, num_train_per_cat):
    """Get the training data from the target file with pickle.
    Infobox data is the data for only bios with infoboxes.
    Full data is the data for all bios."""
    
    f = open(filename, 'r')
    topic_struct = pickle.load(f)
    
    # data is formatted as dict<'biography_type', dict<'article_name', (list<'section_heading'>, list<'infobox_feature'>)>>
    # want to format as list<((list<'section_headings'>, list<'infobox_feature'>)'biography_type')>
    infobox_training_data = list()
    full_training_data = list()
    infobox_test_data = list()
    full_test_data = list()
    for bio_type, articles in topic_struct.items():
        article_list = articles.items()
        random.shuffle(article_list)
        
        for article_name, data in article_list[:num_train_per_cat]:
            if len(data[1]) > 0: #only if has infobox info
                infobox_training_data.append((data, bio_type))
            full_training_data.append((data, bio_type))
        for article_name, data in article_list[num_train_per_cat:]:
            if len(data[1]) > 0: #only if has infobox info
                infobox_test_data.append((data, bio_type))
            full_test_data.append((data, bio_type))
    return infobox_training_data, infobox_test_data, full_training_data, full_test_data
        
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
    
def infobox_feature_extractor(data):
    """Extract features from a relation for the classifier."""
    features = dict()
    lmtzr = WordNetLemmatizer()
    section_headings, infobox_features = data
    for feature in infobox_features:
        words = nltk.word_tokenize(feature)
        for word in words:
            features['infobox_word_' + word] = True
        features['infobox_' + feature] = True
    return features
    
def heading_feature_extractor(data):
    """Extract features from a relation for the classifier."""
    features = dict()
    lmtzr = WordNetLemmatizer()
    section_headings, infobox_features = data
    for position_in_headings, heading in enumerate(section_headings):
        num_headings = len(section_headings)
        features['heading_' + heading] = True
        features['heading_lower_' + heading.lower()] = True
        features['heading_pos_' + heading] = position_in_headings
        words = re.findall(r'\w+', heading, flags = re.UNICODE)
        for word in words:
            if word.lower() not in stopwords.words('english'):
                features[word] = True
                features[word.lower()] = True
                features[lmtzr.lemmatize(word).lower()] = True
    return features
    
def full_feature_extractor(data):
    features = infobox_feature_extractor(data) 
    for k, v in heading_feature_extractor(data).items():
        features[k] = v
    return features
    
if __name__ == '__main__':
    try:
        evaluate('../datasets/classifier_data.pkl', repeat=sys.argv[1])
    except IndexError:
	    evaluate('../datasets/classifier_data.pkl', repeat=1)

    