import math

def cosine_similarity_dict(dict1, dict2):
	'''
	Calculate the cosine similarity of two dictionaries. Tested with keys=terms
	(type string) and values=scores (type float)
	'''
	
	# loop through terms in dict1
	# if term also exists in dict2, multiply both scores and add to numerator
	numerator = 0.0
	for dict1_term, dict1_term_score in dict1.iteritems():
		dotscore = dict1_term_score * dict2.get(dict1_term, 0.0)
		numerator += dotscore
		
	# compute the l2 norm of each vector
	denominator = 0.0
	dict1_norm = sum( [score**2 for score in dict1.values()] )
	dict1_norm = math.sqrt(dict1_norm)
	dict2_norm = sum( [score**2 for score in dict2.values()] )
	dict2_norm = math.sqrt(dict2_norm)
	denominator = dict1_norm * dict2_norm + 1.0
	
	similarity = numerator / denominator
	
	return similarity