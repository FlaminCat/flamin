from collections import Counter
from math import log


class NaiveBayesClassifier:

    def __init__(self, alpha=1):
        self.alpha = alpha

    def fit(self, X, y):
        """ Fit Naive Bayes classifier according to X, y. """

        # COUNT freqs of words and labels.
        labeled_words = []
        for doc, label in zip(X, y):
            for word in doc.split():
                labeled_words.append((word, label))

        # (word, label) count
        self.word_lab_counted = dict(Counter(labeled_words))

        # label count
        self.labels_counted = dict(Counter(y))

        # word count
        words = [word for doc in str(X) for word in doc.split()]
        self.words_counted = dict(Counter(words))

        # CREATE dicts with main info of words and classes for navigation.
        self.info_labels = {}  # p(C)

        for label in self.labels_counted:
            self.info_labels[label] = {
                'number_of_words': self.count_words_for_label(label),
                'apr_prob': self.labels_counted[label] / len(y)
            }

        self.info_words = {}  # p(w_i|C)

        for word in self.words_counted:
            attrs = {}
            for label in self.labels_counted:
                attrs[label] = self.smoothing(word, label)
            self.info_words[word] = attrs

        # Calculated p(C), p(w_i|C).

    def predict(self, X):
        """ Perform classification on an array of test vectors X. """
        answers = []
        words = X.split()
        predictions = []

        # ln(p(C))
        for label in self.info_labels:
            apr_prob = self.info_labels[label]['apr_prob']
            result = log(apr_prob)

            # ln(p(w_i|C))
            for word in words:
                curr_word = self.info_words.get(word)
                if curr_word:
                    result += log(curr_word[label])
            predictions.append((result, label))
        score, predicted = max(predictions)
        answers.append(predicted)

        return answers


    def score(self, X_test, y_test):
        """ Returns the mean accuracy on the given test data and labels. """
        total = len(y_test)
        correct = 0
        prediction = self.predict(X_test)

        for i in range(len(prediction)):
            if prediction[i] == y_test[i]:
                correct += 1

        return correct / total

    def count_words_for_label(self, label):
        c = 0
        for word, word_label in self.word_lab_counted:
            if word_label == label:
                c += self.word_lab_counted[(word, word_label)]
        return c

    def smoothing(self, word, label):

        # параметр сглаживания:
        alpha = self.alpha
        # число наблюдений слова для данного класса:
        n_ic = self.word_lab_counted.get((word, label), 0)
        # общее количество слов в классе:
        n_c = self.info_labels[label]['number_of_words']
        # размерность вектора слов:
        d = len(self.words_counted)

        return (n_ic + alpha) / (n_c + alpha * d)