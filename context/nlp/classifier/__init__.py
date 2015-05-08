'''
Classifier using LIBLINEAR (based on textclassifier)

context.cfg should contain a 'classifier' section with 'linear_data_path'
set to the location of the model and feature files
'''
import os
from collections import defaultdict
import liblinearutil
import math
from models import NormalizedBinaryTextInstance
from utils import clean_text, clean_tweet_text
from ..config import get_section_data

#
# map indicies to category names
#
_cat_map = [
    'politics', 
    'sports', 
    'science-technology', 
    'food',
    'business',
    'healthy-living',
    'arts',
    'entertainment',
    'education',
    'religion',
    'other'
]

#
# set paths
#

_data_dir = get_section_data('classifier')['linear_data_path']

_model_path = os.path.join(_data_dir, 'train_huffpocategories.model')
_feature_path = os.path.join(_data_dir, 'features_huffpocategories')


class SVMTextClassifier:
    def __init__(self, model_filename, features_filename, output_probability=False):
        self.model = liblinearutil.load_model(model_filename)
        self.feature_indices = self._load_features(features_filename)
        self.output_probability = output_probability
       
    def _load_features(self, features_filename):
        feature_indices = {}
        with open(features_filename, 'r') as f:
            # Liblinear expects a one-based feature vector.
            for feature_i, feature in enumerate(f.read().split(','), 1):
                for translation in feature.split('|'):
                    feature_indices[translation] = feature_i
        return feature_indices

    def classify(self, text):
        instance = NormalizedBinaryTextInstance(
            None, text, self.feature_indices)

        # Construct the feature vector.
        feature_vector = {}
        for f, v in instance.feature_values():
            feature_index = self.feature_indices.get(f)
            if feature_index != None:
                feature_vector[feature_index] = v

        options = '-b 1' if self.output_probability else ''
        p_labs, p_acc, p_vals = liblinearutil.predict([], [feature_vector], self.model, options)

        response = []
        vals = dict(enumerate(p_vals[0]))
        for label in sorted(vals, key=vals.get, reverse=True):
            response.append((label, self._soft_max_scaling(vals[label])))
        return response
    
    def _soft_max_scaling(self, z):
        """
        Source:
        "A Simple Method For Estimating Conditional Probabilities For SVMs"
        By: Ruping, Stefan
        """
        return 1 / (1 + math.exp(-2 * z))

    def _pp_scaling(self, z):
        """
        Source:
        "A Simple Method For Estimating Conditional Probabilities For SVMs"
        By: Ruping, Stefan
        """
        if z > 1:
            return 1
        elif z < -1:
            return 0
        else:
            return .5 * (1 + z)        
        

class SVMTweetClassifier:
    def __init__(self, model_filename, features_filename, output_probability=False):
        self.text_classifier = SVMTextClassifier(
            model_filename,
            features_filename,
            output_probability)
        self.MIN_TWEET_LEN = 20

    def classify_text(self, text):
        return self.text_classifier.classify(clean_text(text))

    def classify_tweet(self, tweet):
        assert isinstance(tweet, dict) and tweet.get('text'), \
            "Invalid tweet format."

        clean_tweet = clean_tweet_text(tweet)
        if not clean_tweet.startswith('@') and len(clean_tweet) >= self.MIN_TWEET_LEN:
            return self.text_classifier.classify(clean_tweet)         
        return []


#
# Create classifier
#
_svmc = None
try:
    _svmc = SVMTweetClassifier(_model_path, _feature_path)
except IOError:
    print '\nWARNING: SVMTweetClassifier not created. To use classifier, be sure to set the linear_data_path in the classifier section of context.cfg.\n'

def classify_text(text):
    """
    Classify text.  Returns  [[category, score]].
    """
    return [(_cat_map[i], v) for (i, v) in _svmc.classify_text(text)]
    
def classify_tweet(tweet):
    """
    Classify tweet.  Returns  [[category, score]].
    """
    return [(_cat_map[i], v) for (i, v) in _svmc.classify_tweet(tweet)]

