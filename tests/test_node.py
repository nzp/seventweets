import json
from unittest.mock import MagicMock
from unittest.mock import patch
from unittest.mock import call
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


def test_auth(mocker):
    with seventweets.node.app.test_request_context('/tweets/1',
                                                   method='DELETE',
                                                   headers={'X-Api-Token': 'false-token'}):
        mocker.patch.object(seventweets.config.Config, 'API_TOKEN')
        seventweets.config.Config.API_TOKEN = 'test-token'

        g = seventweets.node.auth(lambda: ('{}', 201))
        result = g()
        assert result[1] == 401


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

    mocker.patch.object(seventweets.config.Config, 'API_TOKEN')
    seventweets.config.Config.API_TOKEN = 'test-token'

    response = test_client.post('/tweets',
                                data='{"tweet": "New tweet!"}',
                                headers={'X-Api-Token': 'test-token'})

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

    mocker.patch.object(seventweets.config.Config, 'API_TOKEN')
    seventweets.config.Config.API_TOKEN = 'test-token'

    response = test_client.delete('/tweets/1',
                                  headers={'X-Api-Token': 'test-token'})

    args, kwargs = seventweets.node.Storage.delete_tweet.call_args
    assert args[1] == 1

    assert response.status_code == 204
    assert response.mimetype == MIME_TYPE

    seventweets.node.Storage.delete_tweet.return_value = False
    response = test_client.delete('/tweets/1',
                                  headers={'X-Api-Token': 'test-token'})
    assert response.status_code == 404


def test_register_node(mocker):
    mocker.patch.object(seventweets.registry.Registry, 'register')
    mocker.patch.object(seventweets.registry.Registry, 'known_nodes')

    node_list = [
        {'name': 'node1', 'address': 'node1.example.com'},
        {'name': 'node2', 'address': 'node2.example.com'},
    ]
    seventweets.registry.Registry.known_nodes = json.dumps(node_list)

    mocker.patch.object(seventweets.config.Config, 'API_TOKEN')
    seventweets.config.Config.API_TOKEN = 'test-token'

    data = '{"name": "test-node", "address": "node.example.com"}'

    response = test_client.post('/registry',
                                data=data,
                                headers={'X-Api-Token': 'test-token'})

    seventweets.registry.Registry.register.assert_called_with(json.loads(data))

    try:
        decoded_response = json.loads(response.get_data(as_text=True))
    except json.JSONDecodeError:
        assert False

    assert decoded_response == node_list
    assert response.status_code == 200
    assert response.mimetype == MIME_TYPE


def test_delete_node(mocker):
    mocker.patch.object(seventweets.registry.Registry, 'delete_node')

    test_client.delete('/registry/test-name')

    seventweets.registry.Registry.delete_node.assert_called_with('test-name')


def test_join_network(mocker):
    mocker.patch.object(seventweets.node.Registry, 'register')
    mocker.patch.object(seventweets.node.requests, 'post')

    node_list = [
        {'name': 'node1', 'address': 'node1.example.com'},
        {'name': 'node2', 'address': 'node2.example.com'},
    ]
    seventweets.node.requests.post.return_value = json.dumps(node_list)

    mocker.patch.object(seventweets.config.Config, 'API_TOKEN')
    seventweets.config.Config.API_TOKEN = 'test-token'

    mocker.patch.object(seventweets.config.Config, 'NAME')
    seventweets.config.Config.NAME = 'me'
    mocker.patch.object(seventweets.config.Config, 'ADDRESS')
    seventweets.config.Config.ADDRESS = 'me.example.com'

    data = '{"name": "test-node", "address": "node.example.com"}'

    response = test_client.post('/join_network',
                                data=data,
                                headers={'X-Api-Token': 'test-token'})

    register_calls = [call(json.loads(data)),
                      call(node_list[0]),
                      call(node_list[1]),]
    seventweets.node.Registry.register.assert_has_calls(register_calls)

    body = '{"address": "me.example.com", "name": "me"}'
    request_post_calls = [
        call('http://node.example.com/registry', data=body),
        call('http://{address}/registry'.format(address=node_list[0]['address']),
             data=body),
        call('http://{address}/registry'.format(address=node_list[1]['address']),
             data=body)
    ]
    seventweets.node.requests.post.assert_has_calls(request_post_calls)

    assert response.status_code == 200
