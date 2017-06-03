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
                       'retweet': True,
                       'register_node': False,
                       'delete_node': False,
                       'search': False,
                       'join_network': True,
                       'get_known_nodes': True,
                       }
single_mode = True

app = Flask(__name__)


@contextmanager
def get_db_cursor():
    _connection = pg8000.connect(**Config.DB_CONFIG)
    cursor = _connection.cursor()

    yield cursor

    cursor.close()
    _connection.commit()
    _connection.close()


def auth(f):
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

    with get_db_cursor() as cursor:
        tweets = Storage.get_all_tweets(cursor)

    return tweets, 200, HEADERS


@app.route('/tweets/<int:id>')
@auth
def get_tweet(id):

    with get_db_cursor() as cursor:
        tweet = Storage.get_tweet(cursor, id)

    if tweet:
        return tweet, 200, HEADERS
    else:
        return '{}', 404, HEADERS


@app.route('/tweets', methods=['POST'])
@auth
def save_tweet():
    tweet = json.loads(request.get_data(as_text=True))

    with get_db_cursor() as cursor:
        result = Storage.save_tweet(cursor, tweet['tweet'])

    return result, 201, HEADERS


@app.route('/tweets/<int:id>', methods=['DELETE'])
@auth
def delete_tweet(id):

    with get_db_cursor() as cursor:
        result = Storage.delete_tweet(cursor, id)

    if result:
        return '{}', 204, HEADERS
    else:
        return '{}', 404, HEADERS


@app.route('/tweets/retweet', methods=['POST'])
@auth
def retweet():
    tweet = json.loads(request.get_data(as_text=True))

    with get_db_cursor() as cursor:
        Storage.save_retweet(cursor, tweet)

    return '', 200, HEADERS


@app.route('/registry', methods=['POST'])
@auth
def register_node():
    node = json.loads(request.get_data(as_text=True))

    Registry.register(node)

    return Registry.known_nodes, 200, HEADERS


@app.route('/registry/<string:name>', methods=['DELETE'])
@auth
def delete_node(name):
    Registry.delete_node(name)

    return '{}', 204, HEADERS


@app.route('/search')
@auth
def search():
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
    if single_mode:
        init_node = json.loads(request.get_data(as_text=True))
        body = json.dumps({'name': Config.NAME, 'address': Config.ADDRESS})

        Register.register(init_node)  # Just in case self is not returned.

        all_nodes_json = requests.post(
            'http://{address}/registry'.format(address=init_node['address']),
            data=body)

        all_nodes = json.loads(all_nodes_json)

        for node in all_nodes:
            Registry.register(node)

            r = request.post(
                'http://{address}/registry'.format(address=node['address']),
                data=body)

        single_mode = False
        return "Joined network", 200, HEADERS
    else:
        return "Already in network mode", 200, HEADERS


@app.route('/private/nodes')
@auth
def get_known_nodes():
    return Registry.known_nodes, 200, HEADERS


if __name__ == '__main__':
    app.run()
