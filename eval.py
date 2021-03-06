'''
Code to evaluate a particular trained network. Think about formatting results
here well to be tables in the paper.
'''
import sklearn.metrics as skmetrics

from collections import Counter

from util import get_window


class Eval:
    '''
    Methods to evaluate different models.
    '''
    def __init__(self, test_data):
        '''
        Arguments:
            test_data (util.MetaphorDataTest): test data
        '''
        self.test_data = test_data
        self.test_df = test_data.test_df

        self.test_sentences = self.test_data.text_sentences

        self.false_negatives = self.test_df[['text', 'word']][
            (self.test_data.predicted_is_metaphor_vec == 0) &
            (self.test_data.is_metaphor_vec == 1)
        ]
        self.false_positives = self.test_df[['text', 'word']][
            (self.test_data.predicted_is_metaphor_vec == 1) &
            (self.test_data.is_metaphor_vec == 0)
        ]
        self.true_negatives = self.test_df[['text', 'word']][
            (self.test_data.predicted_is_metaphor_vec == 0) &
            (self.test_data.is_metaphor_vec == 0)
        ]
        self.true_positives = self.test_df[['text', 'word']][
            (self.test_data.predicted_is_metaphor_vec == 1) &
            (self.test_data.is_metaphor_vec == 1)
        ]

        self.true = self.test_data.is_metaphor_vec
        self.pred = self.test_data.predicted_is_metaphor_vec

        # Compute performance measures.
        # http://scikit-learn.org/stable/modules/model_evaluation.html
        self.confusion_matrix = \
            skmetrics.confusion_matrix(self.true, self.pred)

        tn, fp, fn, tp = self.confusion_matrix.ravel()

        self.accuracy = (tp + tn) / (tp + tn + fp + fn)
        self.precision = tp / (tp + fp)    # how often a positive is true pos.
        self.sensitivity = tp / (tp + fn)  # recall, true positive rate
        self.specificity = tn / (tn + fp)  # true negative rate

        self.auc = skmetrics.roc_auc_score(
            self.true, self.test_data.probabilities[:, 1]
        )

    def word_counts(self, n_most_common=10):
        '''
        For both the false negatives and false positives, create word counts

        Returns:
            (dict): keyed by false_{negative,positive} true_{negative,positive}
                with word counts as values
        '''
        def count_words(df, n_most_common):
            'Count of most common words in window of text/focal_word'

            # Compact way to flatten list of all windowings and do word count.
            words = (
                word
                for row in df.as_matrix()
                for word in get_window(row[0], row[1], 5)
            )

            return Counter(words).most_common(n_most_common)

        return {
            k: count_words(getattr(self, k), n_most_common)
            for k in [
                'false_negatives',
                'false_positives',
                'true_negatives',
                'true_positives'
            ]
        }
