import json

import pytest

from seventweets import node
from seventweets import storage as s


MIME_TYPE = 'application/json'
test_client = node.app.test_client()


def check_keys(d):
    """Check if all tweet fields are present in tweet object."""

    keys = d.keys()
    assert 'id' in keys
    assert 'name' in keys
    assert 'tweet' in keys


@pytest.fixture(scope='module')
def populate_tweets():
    s.Storage.save_tweet('Hello, World!')
    s.Storage.save_tweet('Hello, World, Again!')

    yield None
    s.Storage._tweets.clear()
    s.Tweet._tw_id = 0


def test_get_tweets(populate_tweets):
    response = test_client.get('/tweets')

    try:
        decoded_response = json.loads(response.data)
    except JSONDecodeError:
        assert False

    assert type(decoded_response) == list

    for t in decoded_response:
        assert type(t) == dict
        check_keys(t)

    assert response.status_code == 200
    assert response.mimetype == MIME_TYPE


def test_get_tweet(populate_tweets):
    response = test_client.get('/tweets/1')

    try:
        decoded_response = json.loads(response.data)
    except JSONDecodeError:
        assert False

    assert type(decoded_response) == dict
    check_keys(decoded_response)
    assert response.status_code == 200
    assert response.mimetype == MIME_TYPE


def test_save_tweet(populate_tweets):
    response = test_client.post('/tweets', data='{"tweet": "New tweet!"}')

    try:
        decoded_response = json.loads(response.data)
    except JSONDecodeError:
        assert False

    assert type(decoded_response) == dict
    check_keys(decoded_response)
    assert response.status_code == 201
    assert response.mimetype == MIME_TYPE


def test_delete_tweet(populate_tweets):
    response = test_client.delete('/tweets/1')

    assert response.status_code == 204
