from collections import defaultdict
from nltk.probability import *

def make_freqs(text, size=3):
    """
    For each context, make a FreqDist of what comes next.
    """
    # This defaultdict acts like a dictionary, but it will create an
    # empty FreqDist() when asked about a word it hasn't seen.
    freqs = defaultdict(FreqDist)
 
    # Scan over windows of the appropriate size.
    for left in xrange(len(text)-size):
        # If we are creating a model based on N-grams, then the context we
        # use for Markov chaining will contain (N-1) words and we will predict
        # the Nth.
        right = left + size - 1
        nextword = text[right]
        
        # Make the sequence of words something that we can store in a
        # dictionary.
        context = tuple(text[left:right])

        # Record the fact that this word appeared in this context once.
        freqs[context].inc(nextword)

        # Also record that this context appeared at all. You might want to
        # choose a random context, for example, to get the process started,
        # or to fall back on if you end up in a state where no known word
        # comes next.
        freqs[None].inc(context)
    return freqs

def make_probs(text, size=3):
    """
    Convert the FreqDists to ProbDists using the maximum likelihood estimate.
    """
    freqs = make_freqs(text, size)
    probs = {}
    for context in freqs:
        # Use a maximum likelihood estimate, so that we're always generating
        # words we know about.
        probs[context] = MLEProbDist(freqs[context])
    return probs

