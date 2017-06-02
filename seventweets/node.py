from contextlib import contextmanager
from functools import wraps
import json

from flask import Flask
from flask import request
import pg8000

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
                       'get_known_nodes': True,
                       }

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


@app.route('/private/nodes')
@auth
def get_known_nodes():
    return Registry.known_nodes, 200, HEADERS


if __name__ == '__main__':
    app.run()
