import json

import pytest

from seventweets import storage as s


def clear_globals():
    """Clear global tweets dictionary and id counter."""

    s.Storage._tweets.clear()
    s.Tweet._tw_id = 0


@pytest.fixture(scope='class')
def tweets():
    FIRST_TWEET = 'First tweet.'
    SECOND_TWEET = 'Second tweet.'

    yield {'t1': s.Tweet(FIRST_TWEET),
           't2': s.Tweet(SECOND_TWEET),
           'FIRST_TWEET': FIRST_TWEET,
           'SECOND_TWEET': SECOND_TWEET,}

    # It would persist for all tests in this module so we have to reset it.
    s.Tweet._tw_id = 0

@pytest.fixture
def populate_tweets():
    TWEET1 = 'Get ALL the tweets!'
    TWEET2 = 'Get ALL the tweets, AGAIN!'

    s.Storage._tweets = {
        0: s.Tweet(TWEET1),
        1: s.Tweet(TWEET2)
    }

    # Return tweet strings so we can access them in the test.
    yield [TWEET1, TWEET2]

    clear_globals()


@pytest.mark.usefixtures('tweets')
class TestTweet:

    def test_tweet_ids(self, tweets):
        assert tweets['t1'].id == 0
        assert tweets['t2'].id == 1

    def test_node_name(self, tweets):
        assert tweets['t1'].name == s.NODE_NAME
        assert tweets['t2'].name == s.NODE_NAME

    def test_tweet_text(self, tweets):
        assert tweets['t1'].tweet == tweets['FIRST_TWEET']
        assert tweets['t2'].tweet == tweets['SECOND_TWEET']

    def test_tweet_str_representation(self, tweets):
        assert str(tweets['t1']) == tweets['FIRST_TWEET']
        assert str(tweets['t2']) == tweets['SECOND_TWEET']


class TestStorage:

    def test_save_tweet(self):
        tweet = 'Hello, World!'
        json_tweet = s.Storage.save_tweet(tweet)

        try:
            decoded_tweet = json.loads(json_tweet)
        except JSONDecodeError:
            assert False

        assert type(decoded_tweet) == dict

        assert type(s.Storage._tweets[0]) == s.Tweet
        assert len(s.Storage._tweets) == 1
        assert s.Storage._tweets[0].id == 0
        assert s.Storage._tweets[0].tweet == tweet
        assert s.Storage._tweets[0].name == s.NODE_NAME

        clear_globals()

    def test_get_all(self, populate_tweets):
        tweets = s.Storage.get_all()

        try:
            decoded_tweets = json.loads(tweets)
        except JSONDecodeError:
            assert False

        assert type(decoded_tweets) == list
        assert len(decoded_tweets) == 2

        t1 = decoded_tweets[0]
        t2 = decoded_tweets[1]

        assert t1['id'] == 0
        assert t2['id'] == 1

        assert t1['name'] == s.NODE_NAME
        assert t2['name'] == s.NODE_NAME

        assert t1['tweet'] == populate_tweets[0]
        assert t2['tweet'] == populate_tweets[1]

    def test_get_tweet(self, populate_tweets):

        # Get the second tweet.
        tweet = s.Storage.get_tweet(1)

        try:
            decoded_tweet = json.loads(tweet)
        except JSONDecodeError:
            assert False

        # JSON output is a single dictionary with 3 keys, not a list of
        # length 1.
        assert type(decoded_tweet) == dict
        assert len(decoded_tweet) == 3

        assert decoded_tweet['id'] == 1
        assert decoded_tweet['name'] == s.NODE_NAME
        assert decoded_tweet['tweet'] == populate_tweets[1]

    def test_delete_tweet(self, populate_tweets):
        s.Storage.delete_tweet(0)

        assert len(s.Storage._tweets) == 1
        assert 0 not in s.Storage._tweets.keys()
