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
from nltk.classify import apply_features

            
def evaluate(filename, repeat=1, train_percent=.7):
    """Test the accuracy for the results in the target file."""
    total = 0
    correct = 0
    
    for i in range(repeat):
        data = load_data(filename, num_train_per_cat)
        
        classifier = ParagraphClassifier(training_data, feature_extractor)
        
        for (data, bio_type) in test_data:
            total += 1
            if classifier.classify(data) == bio_type:
                correct += 1

    print "Paragraph classifier on all data, results over " + str(repeat) + " runs: " + str(float(correct)/total)

    classifier.classifier.show_most_informative_features(50)
    return classifier
    
def get_classifier(filename):
    train_data = load_data(filename, 10)
    classifier = ParagraphClassifier(train_data, feature_extractor)
    return classifier
    
    
def get_article_nutritional_label(article_data_list, classifier):
    """This function will give you the nutritional label breakdown for an
    individual article. The arguments are the classifier and a list of
    "data", where the data is a paragraph - the argument to the classifier.
    It will return a list of all the categories in the article, in order.
    """
    cats = []
    for data in article_data_list:
        cat = classifier.classify(data)
        cats.append(cat)
    return cats
    
def get_nutritional_labels(filename, classifier, num_per_cat=25):
    """Get the training data from the target file with pickle.
    The filename specifies the topic_struct to use, e.g., paragraph_data.
    Num_per_cat specifies how many articles of each category to look at.
    
    This function generates the "breakdown", which is a map from bio_type
    to another map from category to total. Essentially, this says: give me a profile
    of what each category is like.
    
    Infobox data is the data for only bios with infoboxes.
    Full data is the data for all bios."""

    f = open(filename, 'r')
    topic_struct = pickle.load(f)
    
    # data is formatted as dict<'biography_type', dict<'article_name', (list<'section_heading'>, list<'infobox_feature'>)>>
    # want to format as list<('section_heading', 'biography_type')>
    training_data = list()
    test_data = list()
    avg_paragraphs = 0
    num_articles = 0
    for bio_type, articles in topic_struct.items():
        article_list = articles.items()
        random.shuffle(article_list)
        
        for article_name, data_list in article_list[:num_per_cat]: 
            avg_paragraphs += len(data_list)
            num_articles += 1
            test_data.append((article_name, data_list, bio_type))

    print "Average number of paragraphs per article:",float(avg_paragraphs)/num_articles
    
    breakdown = dict()
    # this should be a map from bio_type to another map, which is from category to total
    
    
    for info in test_data:
        article_name, data_list, bio_type = info
        labels = get_article_nutritional_label(data_list, classifier)
        
        histogram = dict()
        count = 0
        for label in labels:
            if label not in histogram:
                histogram[label]=0
            histogram[label] += 1
            count += 1
#        for label in labels:
#            num_in_cat = histogram[label]
#            prop = float(num_in_cat)/count
#            histogram[label] = prop
            
        print '\n\n\n',article_name, "\n", histogram, count
        
        if bio_type not in breakdown:
            breakdown[bio_type] = dict()
            
        current_histogram = breakdown[bio_type]
        for label in labels:
            if label not in current_histogram:
                current_histogram[label] = 0
            current_histogram[label] += 1
        breakdown[bio_type] = current_histogram
        
    print "breakdown"
    print breakdown
    
    for bio_type in breakdown.keys():
        histogram = breakdown[bio_type]
        
        count_paragraphs = 0
        for cat in histogram.keys():
            count_paragraphs += histogram[cat]
        for cat in histogram.keys():
            histogram[cat] = float(histogram[cat])/count_paragraphs
            
    print breakdown
    
    #return training_data, test_data
    
    
def load_data(filename, num_train_per_cat=15):
    """Get the training data from the target file with pickle.
    Only get num_train_per_cat articles per category.
    
    Infobox data is the data for only bios with infoboxes.
    Full data is the data for all bios."""
    
    f = open(filename, 'r')
    topic_struct = pickle.load(f)
    
    # data is formatted as dict<'biography_type', dict<'article_name', (list<'section_heading'>, list<'infobox_feature'>)>>
    # want to format as list<('section_heading', 'biography_type')>
    training_data = list()
#    test_data = list()
    avg_paragraphs = 0
    num_articles = 0
    for bio_type, articles in topic_struct.items():
        article_list = articles.items()
        random.shuffle(article_list)
        
        for article_name, data_list in article_list[:num_train_per_cat]: 
            avg_paragraphs += len(data_list)
            num_articles += 1
            for data in data_list:
                training_data.append((data, bio_type))
    print "Average number of paragraphs per article:",float(avg_paragraphs)/num_articles
    return training_data
        
class ParagraphClassifier():
    """Naive bayesian classifier that takes a list of section headings and
    tries to predict a biography category."""
    def __init__(self, golden_data, feature_extractor):
        self.feature_extractor = feature_extractor
        train_set = []
        
        train_set = apply_features(feature_extractor, golden_data)
        
        """numtimes = 0
        for (data, bio_type) in golden_data:
            numtimes += 1
            if numtimes % 100 == 0:
                print numtimes
            featureset = self.feature_extractor(data)
            train_set.append( (featureset, bio_type) )
        print "about to train"""
            
        self.classifier = nltk.NaiveBayesClassifier.train(train_set)
        print "done training"
    
    def classify(self, data):
        featureset = self.feature_extractor(data)
        return self.classifier.classify(featureset)
    
def feature_extractor(data):
    """Extract features from a relation for the classifier."""
    features = dict()
    lmtzr = WordNetLemmatizer()

    h2, h3, paragraph = data
    
    """
    features['h2_' + h2.lower()] = True
    for word in h2.split(' '):
        if word.lower() not in stopwords.words('english') and len(word) > 1:
            features['h2word_' + word.lower()] = True
    features['h_' + h2.lower()] = True
    for word in h2.split(' '):
        if word.lower() not in stopwords.words('english') and len(word) > 1:
            features['hword_' + word.lower()] = True
    """
    """
    if h3 != None:    
        features['h3_' + h3.lower()] = True
        for word in h3.split(' '):
            if word.lower() not in stopwords.words('english') and len(word) > 1:
                features['h3word_' + word.lower()] = True
        features['h_' + h3.lower()] = True
        for word in h3.split(' '):
            if word.lower() not in stopwords.words('english') and len(word) > 1:
                features['hword_' + word.lower()] = True
    """ 
    for word in nltk.wordpunct_tokenize(paragraph):
        if word.lower() not in stopwords.words('english') and len(word) > 1:
            """
            features[word] = True
            features['lower_' + word.lower()] = True
            features['lmtzr_' + lmtzr.lemmatize(word).lower()] = True
            """
            features[lmtzr.lemmatize(word).lower()] = True
    return features
    
if __name__ == '__main__':
    try:
        evaluate('../datasets/paragraph_data.pkl', repeat=sys.argv[1])
    except IndexError:
	    evaluate('../datasets/paragraph_data.pkl', repeat=1)

    