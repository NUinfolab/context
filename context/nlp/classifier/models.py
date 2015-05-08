import math
from nltk import FreqDist
import utils

class Model():

    def __init__(self, data, minimum_vocab_fraction=.02, include_ngrams=True):
        self.doc_freq = FreqDist()
        for count, (label, text) in enumerate(data, start=1):
            for word in set(utils.tokenize(text, include_ngrams, limit_ngrams=True)):
                self.doc_freq.inc(word)
        self.doc_count = count

        self.min_vocab_freq = 1
        self.max_vocab_freq = .95 * self.doc_count
        print 'Min/max vocabulary frequency:', self.min_vocab_freq, self.max_vocab_freq

        self.features = sorted(filter(self._is_valid_feature, self.doc_freq))

    def _is_valid_feature(self, feature):
        doc_freq = self.doc_freq[feature]
        return doc_freq > self.min_vocab_freq and doc_freq < self.max_vocab_freq

class LibSVMModel(Model):

    def feature_vector(self, instance):
        lines = [str(instance.label_value())]

        for i, f in enumerate(self.features, start=1):
            feature_value = instance.feature_value(f)
            if feature_value != 0:
                lines.append('%s:%s' % (i, feature_value))

        return ' '.join(lines) + '\n'

class NormalizedBinaryInstance(object):

    def __init__(self, label, features, model_features):
        self.label = label
        self.common_features = [f for f in set(features) if f in model_features]
        if self.common_features:
            self.normalized_true = 1 / float(
                math.sqrt(len(self.common_features)))

    def label_value(self):
        return self.label

    def feature_values(self):
        for f in self.common_features:
            yield f, self.normalized_true

class NormalizedBinaryTextInstance(NormalizedBinaryInstance):

    def __init__(self, label, text, model_features):
        words = utils.tokenize(text)
        super(NormalizedBinaryTextInstance, self).__init__(
            label,
            words,
            model_features)

def debug_features(features):
    print 'Vocabulary size:', len(features)
    print [f for f in features if ',' in f]
    print 'Vocabulary, alpha words:', len(
        [w for w in features if w.isalpha()])
    print 'Vocabulary, bigrams:', len(
        [w for w in features if len(w.split()) == 2])
    print 'Vocabulary, trigrams:', len(
        [w for w in features if len(w.split()) == 3])
