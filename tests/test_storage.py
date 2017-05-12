import json
from unittest.mock import MagicMock

import pytest

from seventweets.storage import Tweet
from seventweets.storage import Storage


NODE_NAME = 'nzp'
TWEET_1_ID = 1
TWEET_1 = 'Hello, World!'

TWEET_2_ID = 2
TWEET_2 = 'Hello, Again!'


@pytest.fixture(scope='class')
def tweet():
    return Tweet([TWEET_1_ID, NODE_NAME, TWEET_1])


@pytest.fixture(scope='function')
def db_cursor():
    FETCHALL_RESULT = (
        [TWEET_1_ID, NODE_NAME, TWEET_1],
        [TWEET_2_ID, NODE_NAME, TWEET_2]
    )
    ALL_TWEETS = [
        {'id': TWEET_1_ID, 'name': NODE_NAME, 'tweet': TWEET_1},
        {'id': TWEET_2_ID, 'name': NODE_NAME, 'tweet': TWEET_2}
    ]

    cursor = MagicMock()
    cursor.execute = MagicMock()
    cursor.fetchone = MagicMock(return_value=FETCHALL_RESULT[1])
    cursor.fetchall = MagicMock(return_value=FETCHALL_RESULT)

    return {
        'cursor': cursor,
        'all_tweets': ALL_TWEETS,
        'tweet_1': {'id': TWEET_1_ID, 'name': NODE_NAME, 'tweet': TWEET_1},
        'tweet_2': {'id': TWEET_2_ID, 'name': NODE_NAME, 'tweet': TWEET_2}
    }


@pytest.mark.usefixtures('tweet')
class TestTweet:

    def test_tweet_init(self, tweet):
        assert tweet.id == TWEET_1_ID
        assert tweet.name == NODE_NAME
        assert tweet.tweet == TWEET_1

    def test_tweet_str(self, tweet):
        assert str(tweet) == TWEET_1


@pytest.mark.usefixture('db_cursor')
class TestStorage:

    def test_get_all_tweets(self, db_cursor):
        cursor = db_cursor['cursor']
        all_tweets = db_cursor['all_tweets']

        tweets = Storage.get_all_tweets(cursor)

        cursor.execute.assert_called_with('SELECT id, name, tweet FROM tweets')

        try:
            decoded_tweets = json.loads(tweets)
        except json.JSONDecodeError:
            assert False

        assert decoded_tweets == all_tweets

    def test_get_tweet(self, db_cursor):
        cursor = db_cursor['cursor']
        tweet_2 = db_cursor['tweet_2']
        id = TWEET_2_ID

        tweet = Storage.get_tweet(cursor, id)

        cursor.execute.assert_called_with(
            'SELECT id, name, tweet FROM tweets WHERE id = {}'.format(TWEET_2_ID))

        try:
            decoded_tweet = json.loads(tweet)
        except json.JSONDecodeError:
            assert False

        assert decoded_tweet == tweet_2

    def test_save_tweet(self, db_cursor):
        cursor = db_cursor['cursor']
        tweet = TWEET_2
        test_result = db_cursor['tweet_2']

        result = Storage.save_tweet(cursor, tweet)

        cursor.execute.assert_called_with(
            "INSERT INTO tweets (name, tweet) \
            VALUES ('nzp', '{}') RETURNING id, name, tweet".format(tweet))

        try:
            decoded_result = json.loads(result)
        except json.JSONDecodeError:
            assert False

        assert decoded_result == test_result

    def test_delete_tweet(self, db_cursor):
        # TODO: Test case where id doesn't exist.

        cursor = db_cursor['cursor']
        id = TWEET_2_ID

        result = Storage.delete_tweet(cursor, id)

        cursor.execute.assert_called_with(
            "DELETE FROM tweets WHERE id = {} RETURNING id".format(id))

