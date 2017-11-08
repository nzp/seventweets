"""This module implements a network node.

A simple Flask app in which routes (API endpoint) act as thin wrappers for
database access functions, etc.

Attributes:
    HEADERS (dict): Common HTTP response headers.
    PROTECTED_ENDPOINTS (dict): A dictionary indicating which endpoints are auth
        protected.
    single_mode (bool): Boolean indicating if we are the only node.

Functions:
    delete_node: Endpoint for removing inactive nodes.
    delete_tweet: Endpoint for deleting own tweets.
    get_known_nodes: “Private” endpoint, returns nodes we are aware of.
    get_tweet: Endpoint to get tweet by ID.
    get_tweets: Endpoint to get all own tweets.
    join_network: Initiate network join.
    register_node: Register the node in request.
    save_tweet: Save the tweet in request.
    search: Search local or all tweets.

"""

from collections import OrderedDict
from contextlib import contextmanager
from functools import wraps
import json

from flask import Flask
from flask import request
import pg8000
import requests

from seventweets.config import Config
from seventweets.registry import Registry
from seventweets.storage import Storage


HEADERS = {'Content-Type': 'application/json; charset=utf=8'}
PROTECTED_ENDPOINTS = {'get_tweets': False,
                       'get_tweet': False,
                       'save_tweet': True,
                       'delete_tweet': True,
                       'register_node': False,
                       'delete_node': False,
                       'search': False,
                       'join_network': True,
                       'get_known_nodes': True,
                       }

app = Flask(__name__)


#  TODO:  Privatize the name.
@contextmanager
def get_db_cursor():
    # Context manager which returns a database connection, and closes it
    # after processing is done.

    _connection = pg8000.connect(**Config.DB_CONFIG)
    cursor = _connection.cursor()

    yield cursor

    cursor.close()
    _connection.commit()
    _connection.close()


def auth(f):
    # Authentication decorator for API endpoints.  Each endpoint is decorated
    # regardless of actually needing authentication.

    @wraps(f)
    def wrapper(*args, **kwargs):
        protected = PROTECTED_ENDPOINTS

        if protected[request.endpoint]:
            # A feature, not a bug: we can disable authentication by
            # initializing the application without a token configured and not
            # sending any in the request.  In that case this is None == None.
            # But maybe it would be better to not allow for this.
            if request.headers.get('X-Api-Token') == Config.API_TOKEN:
                return f(*args, **kwargs)
            else:
                return '{}', 401, HEADERS
        else:
            return f(*args, **kwargs)

    return wrapper


@app.route('/tweets')
@auth
def get_tweets():
    """Return all tweets by this node.

    This endpoint is not protected by authentication.

    Returns:
        (str, int, dict): JSON array of tweet objects
            (``"[{"id": <int>, "name": <str>, "tweet": <str>}, ...]"``),
            HTTP status code (200 on success) , headers.

    """
    with get_db_cursor() as cursor:
        tweets = Storage.get_all_tweets(cursor)

    return tweets, 200, HEADERS


@app.route('/tweets/<int:id>')
@auth
def get_tweet(id):
    """Return tweet by id.

    This endpoint is not protected by authentication.

    Args:
        id (int): ID of the tweet to retrieve.

    Returns:
        (str, int, dict): JSON object of the tweet (``"{"id": <int>,
            "name": <str>, "tweet": <str>}"``), HTTP status code (200 on
            success, 404 if no result) , headers.

    """
    with get_db_cursor() as cursor:
        tweet = Storage.get_tweet(cursor, id)

    if tweet:
        return tweet, 200, HEADERS
    else:
        return '{}', 404, HEADERS


@app.route('/tweets', methods=['POST'])
@auth
def save_tweet():
    """Save tweet in POST request body to this node.

    Used by this node's frontend to post an original tweet to the service.
    This endpoint is authenticated.

    Request body format is a JSON object with the tweet as value of string
    ``"tweet"``, e.g.: ``{"tweet": "Hot takes! Get your hot takes!"}``.

    Returns:
        (str, int, dict): JSON object of the tweet (``"{"id": <int>,
            "name": <str>, "tweet": <str>}"``), HTTP status code 201, headers.

    """
    tweet = json.loads(request.get_data(as_text=True))

    with get_db_cursor() as cursor:
        result = Storage.save_tweet(cursor, tweet['tweet'])

    return result, 201, HEADERS


@app.route('/tweets/<int:id>', methods=['DELETE'])
@auth
def delete_tweet(id):
    """Delete own tweet or retweet by id.

    Used by this node's frontend to delete own tweet or retweet.  This endpoint
    is authenticated.  On success returns HTTP code 204.

    Args:
        id (int): ID of the tweet to delete.

    Returns:
        (str, int, dict): Empty JSON object, HTTP status code (204 on success,
            404 if there was no such ID), headers.)

    """
    with get_db_cursor() as cursor:
        result = Storage.delete_tweet(cursor, id)

    if result:
        return '{}', 204, HEADERS
    else:
        return '{}', 404, HEADERS


@app.route('/registry', methods=['POST'])
@auth
def register_node():
    """Register node in POST request body as active.

    This is where nodes announce themselves to others by sending their name and
    address in request body.  Request body is a JSON object with the name of
    node and its address: ``{"name": <str>, "address": <str>}``.This endpoint
    is not authenticated.

    Returns:
        (str, int, dict): JSON array of known node objects (in the same format
            as in the request body), HTTP status code 200, headers.

    """
    node = json.loads(request.get_data(as_text=True))

    Registry.register(node)

    return Registry.known_nodes, 200, HEADERS


@app.route('/registry/<string:name>', methods=['DELETE'])
@auth
def delete_node(name):
    """Delete node by name from the list of known nodes.

    Nodes use this endpoint to announce their own shutdown.  It is not
    authenticated (but should in future have some sort of validation of the
    name).

    Args:
        name (str): Name of the node to delete/unregister.

    Returns:
        (str, int, dict): Empty JSON object, HTTP status code 204, headers.

    """
    Registry.delete_node(name)

    return '{}', 204, HEADERS


@app.route('/search')
@auth
def search():
    """Search for, and return tweets satisfying query string parameters.

    This endpoint is used to initiate a search of node's local tweets, or
    a global search of the whole network.  It is not authenticated.  The
    accepted query string parameters are:

    *  ``content`` -- String to search for;
    *  ``created_from`` -- Earliest date of tweet;
    *  ``created_to`` -- Last date of tweet;
    *  ``all`` -- If set, do a global search.

    Returns:
        (str, int, dict): JSON array of tweet objects (``[{"id": <int>, "name":
            <str>, "tweet": <str>}, ...]``), HTTP status code 200, headers.

    """
    # TODO: Some validation.  Or switch to having an ORM.

    # pg8000 chokes on '%', one solution is escaping: '%%'.
    if request.args.get('content'):
        content = '%%' + request.args.get('content') + '%%'
    else:
        content = '%%'

    if request.args.get('created_from'):
        created_from = request.args.get('created_from')
    else:
        created_from = '-infinity'

    if request.args.get('created_to'):
        created_to = request.args.get('created_to')
    else:
        created_to = 'infinity'

    query = """
    SELECT id, node_name, content FROM tweet
    WHERE content ILIKE '{content}' AND
    (pub_datetime > '{frm}' AND pub_datetime < '{to}');
    """.format(content=content, frm=created_from, to=created_to)

    with get_db_cursor() as cursor:
        result = Storage.search(cursor, query)

    if request.args.get('all') in ['1', 'true', 'yes']:
        for node in Registry._known_nodes:
            url = ('http://{}/search?'.format(node.address) +
                   'content={}'.format(request.args.get('content')) +
                   '&created_from={}'.format(request.args.get('created_from')) +
                   '&created_to={}'.format(request.args.get('created_to')))

            r = request.get(url)
            result.extend(json.loads(r))

    return json.dumps(result), 200, HEADERS


@app.route('/join_network', methods=['POST'])
@auth
def join_network():
    """Initiate joining the network if not already in.

    This endpoint is used by node's frontend to make it join the network.  It
    is authenticated.  The request body contains the name and address of the
    initial node we should register to, as a JSON object of format:
    ``{"name": <str>, "address": <str>}``.  After the initial node returns its
    list of known nodes, we register to each of those.

    Returns:
        (str, int, dict): Response body (API does not specify any), HTTP status
            code 200, headers.

    """
    init_node = json.loads(request.get_data(as_text=True))

    # Preserving the order of keys mainly because of easier unit testing.
    # Without ordering, sometimes the order would be reversed and the tests
    # involving this would fail.
    self_node = OrderedDict([('name', Config.NAME), ('address', Config.ADDRESS)])
    body = json.dumps(self_node)

    # In case others not returning self in list of known nodes.
    Registry.register(init_node)

    all_nodes_json = requests.post(
        'http://{address}/registry'.format(address=init_node['address']),
        data=body)

    all_nodes = json.loads(all_nodes_json)

    for node in all_nodes:
        # TODO: Remove initial node if present.
        Registry.register(node)

        r = requests.post(
            'http://{address}/registry'.format(address=node['address']),
            data=body)

    return "Joined network", 200, HEADERS


@app.route('/private/nodes')
@auth
def get_known_nodes():
    # Not part of API specification, used only by the frontend to get a list
    # of known nodes for diagnostic purposes.

    return Registry.known_nodes, 200, HEADERS


if __name__ == '__main__':
    app.run()
