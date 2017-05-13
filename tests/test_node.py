import json
from unittest.mock import MagicMock
from unittest.mock import patch
import sys

import pytest
from pytest_mock import mocker

# On import of seventweets.node below, pg8000.connect gets executed, so we nuke
# it completely because we don't want the database involved at all.
sys.modules['pg8000'] = MagicMock()

import seventweets.node


MIME_TYPE = 'application/json'
test_client = seventweets.node.app.test_client()


def check_keys(d):
    """Check if all tweet fields are present in tweet object."""

    keys = d.keys()
    assert 'id' in keys
    assert 'name' in keys
    assert 'tweet' in keys


TWEETS = [
    {'id': 1, 'name': 'nzp', 'tweet': 'Hello, World!'},
    {'id': 2, 'name': 'nzp', 'tweet': 'Hello, Again!'}
]


def test_get_tweets(mocker):
    mocker.patch.object(seventweets.node.Storage, 'get_all_tweets')
    seventweets.node.Storage.get_all_tweets.return_value = json.dumps(TWEETS)

    response = test_client.get('/tweets')

    try:
        decoded_response = json.loads(response.get_data(as_text=True))
    except json.JSONDecodeError:
        assert False

    assert type(decoded_response) == list

    for t in decoded_response:
        assert type(t) == dict
        check_keys(t)

    assert response.status_code == 200
    assert response.mimetype == MIME_TYPE


def test_get_tweet(mocker):
    mocker.patch.object(seventweets.node.Storage, 'get_tweet')
    seventweets.node.Storage.get_tweet.return_value = json.dumps(TWEETS[0])

    response = test_client.get('/tweets/1')

    args, kwargs = seventweets.node.Storage.get_tweet.call_args
    assert args[1] == 1

    try:
        decoded_response = json.loads(response.get_data(as_text=True))
    except json.JSONDecodeError:
        assert False

    assert type(decoded_response) == dict
    check_keys(decoded_response)
    assert response.status_code == 200
    assert response.mimetype == MIME_TYPE


def test_save_tweet(mocker):
    mocker.patch.object(seventweets.node.Storage, 'save_tweet')
    seventweets.node.Storage.save_tweet.return_value = json.dumps(TWEETS[1])

    response = test_client.post('/tweets', data='{"tweet": "New tweet!"}')

    args, kwargs = seventweets.node.Storage.save_tweet.call_args
    assert args[1] == 'New tweet!'

    try:
        decoded_response = json.loads(response.get_data(as_text=True))
    except json.JSONDecodeError:
        assert False

    assert type(decoded_response) == dict
    check_keys(decoded_response)
    assert response.status_code == 201
    assert response.mimetype == MIME_TYPE


def test_delete_tweet(mocker):
    mocker.patch.object(seventweets.node.Storage, 'delete_tweet')
    seventweets.node.Storage.delete_tweet.return_value = True

    response = test_client.delete('/tweets/1')

    args, kwargs = seventweets.node.Storage.delete_tweet.call_args
    assert args[1] == 1

    assert response.status_code == 204
    assert response.mimetype == MIME_TYPE

    seventweets.node.Storage.delete_tweet.return_value = False
    response = test_client.delete('/tweets/1')
    assert response.status_code == 404
