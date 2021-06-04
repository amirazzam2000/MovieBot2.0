from nltk.sentiment import SentimentIntensityAnalyzer
from rasa.nlu.components import Component
from rasa.nlu import utils
from rasa.nlu.model import Metadata
import re, string, random
from DataManagement.MoviesRecommender import MoviesManager
import nltk
from nltk.classify import NaiveBayesClassifier
import os
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import twitter_samples, stopwords
from nltk.tag import pos_tag
from nltk.tokenize import word_tokenize
from nltk import FreqDist, classify, NaiveBayesClassifier

import typing
from typing import Any, Optional, Text, Dict

SENTIMENT_MODEL_FILE_NAME = "sentiment_classifier.pkl"


class SentimentAnalyzer(Component):
    """A custom sentiment analysis component"""
    name = "sentiment"
    provides = ["entities"]
    requires = ["tokens"]
    defaults = {}
    language_list = ["en"]
    print('initialised the class')

    def __init__(self, component_config=None):
        super(SentimentAnalyzer, self).__init__(component_config)
        self.classifier = None
        self.manager = MoviesManager()
        self.train()

    def remove_noise(self, tweet_tokens, stop_words=()):

        cleaned_tokens = []

        for token, tag in pos_tag(tweet_tokens):
            token = re.sub('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+#]|[!*\(\),]|' \
                           '(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', token)
            token = re.sub("(@[A-Za-z0-9_]+)", "", token)

            if tag.startswith("NN"):
                pos = 'n'
            elif tag.startswith('VB'):
                pos = 'v'
            else:
                pos = 'a'

            lemmatizer = WordNetLemmatizer()
            token = lemmatizer.lemmatize(token, pos)

            if len(token) > 0 and token not in string.punctuation and token.lower() not in stop_words:
                cleaned_tokens.append(token.lower())
        return cleaned_tokens

    def get_all_words(self, cleaned_tokens_list):
        for tokens in cleaned_tokens_list:
            for token in tokens:
                yield token

    def get_tweets_for_model(self, cleaned_tokens_list):
        for tweet_tokens in cleaned_tokens_list:
            yield dict([token, True] for token in tweet_tokens)

    def train(self, arg1=None, arg2=None, **kwargs):
        """Load the sentiment polarity labels from the text
           file, retrieve training tokens and after formatting
           data train the classifier."""
        nltk.download('averaged_perceptron_tagger')
        nltk.download('wordnet')
        nltk.download('twitter_samples')
        nltk.download('punkt')
        nltk.download('stopwords')
        nltk.download('vader_lexicon')

        positive_tweets = twitter_samples.strings('positive_tweets.json')
        negative_tweets = twitter_samples.strings('negative_tweets.json')
        text = twitter_samples.strings('tweets.20150430-223406.json')
        tweet_tokens = twitter_samples.tokenized('positive_tweets.json')[0]

        stop_words = stopwords.words('english')

        positive_tweet_tokens = twitter_samples.tokenized('positive_tweets.json')
        negative_tweet_tokens = twitter_samples.tokenized('negative_tweets.json')

        positive_cleaned_tokens_list = []
        negative_cleaned_tokens_list = []

        for tokens in positive_tweet_tokens:
            positive_cleaned_tokens_list.append(self.remove_noise(tokens, stop_words))

        for tokens in negative_tweet_tokens:
            negative_cleaned_tokens_list.append(self.remove_noise(tokens, stop_words))

        all_pos_words = self.get_all_words(positive_cleaned_tokens_list)

        freq_dist_pos = FreqDist(all_pos_words)
        print(freq_dist_pos.most_common(20))

        positive_tokens_for_model = self.get_tweets_for_model(positive_cleaned_tokens_list)
        negative_tokens_for_model = self.get_tweets_for_model(negative_cleaned_tokens_list)

        positive_dataset = [(tweet_dict, "Positive")
                            for tweet_dict in positive_tokens_for_model]

        negative_dataset = [(tweet_dict, "Negative")
                            for tweet_dict in negative_tokens_for_model]

        dataset = positive_dataset + negative_dataset

        random.shuffle(dataset)

        train_data = dataset[:7000]
        test_data = dataset[7000:]

        self.classifier = NaiveBayesClassifier.train(train_data)

    def convert_to_rasa(self, value, confidence, name):
        """Convert model output into the Rasa NLU compatible output format."""

        entity = {"value": value,
                  "confidence": confidence,
                  "entity": "sentiment",
                  "extractor": name}

        return entity

    def convert_movie_to_rasa(self, value, found):
        """Convert model output into the Rasa NLU compatible output format."""

        entity = {"name": value,
                  "found": found,
                  "entity": "movie_name",
                  "extractor": "our_fuzzy_logic"}

        return entity

    def preprocessing(self, tokens):
        """Create bag-of-words representation of the training examples."""

        return ({word: True for word in tokens})

    def process(self, message, **kwargs):
        """Retrieve the tokens of the new message, pass it to the classifier
            and append prediction results to the message class."""
        if self.classifier is None:
            self.train()

        if message.get("text") is not None:
            sid = SentimentIntensityAnalyzer()
            res = sid.polarity_scores(message.get("text"))
            key, value = max(res.items(), key=lambda x: x[1])

            if key == "pos":
                key = "Positive"
            elif key == "neg":
                key = "Negative"
            else:
                key = "Neutral"

            custom_tokens = self.remove_noise(word_tokenize(message.get("text")))
            t = self.classifier.prob_classify(dict([token, True] for token in custom_tokens))

            sentiment = 'Positive' if t.prob('Positive') > t.prob('Negative') else 'Negative'
            confidence = max(t.prob('Positive'), t.prob('Negative'))

            found, entry = self.manager.getMovieName(message.get("text"))
            movie = str(entry['original_title'].item())

            if len(message.get("text")) > 20:
                entity = self.convert_to_rasa(sentiment, confidence, name="our_sentiment_extractor")
            else:
                entity = self.convert_to_rasa(key, value, name="builtin_sentiment_extractor")

            message.set("sentiment", [entity], add_to_output=True)
            entity = self.convert_movie_to_rasa(movie, found)
            message.set("movies", [entity], add_to_output=True)

    def persist(self, file_name, model_dir):
        """Persist this model into the passed directory
        classifier_file = os.path.join(model_dir, SENTIMENT_MODEL_FILE_NAME)
        utils.json_pickle(classifier_file, self)
        return {"classifier_file": SENTIMENT_MODEL_FILE_NAME}
        ."""
        pass
