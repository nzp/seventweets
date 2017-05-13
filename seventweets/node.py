from contextlib import contextmanager
import json

from flask import Flask
from flask import request
import pg8000

from seventweets.storage import Storage
from seventweets.config import Config


HEADERS = {'Content-Type': 'application/json; charset=utf=8'}

app = Flask(__name__)


@contextmanager
def get_db_cursor():
    _connection = pg8000.connect(**Config.DB_CONFIG)
    cursor = _connection.cursor()

    yield cursor

    cursor.close()
    _connection.commit()
    _connection.close()


@app.route('/tweets')
def get_tweets():

    with get_db_cursor() as cursor:
        tweets = Storage.get_all_tweets(cursor)

    return tweets, 200, HEADERS


@app.route('/tweets/<int:id>')
def get_tweet(id):

    with get_db_cursor() as cursor:
        tweet = Storage.get_tweet(cursor, id)

    if tweet:
        return tweet, 200, HEADERS
    else:
        return '{}', 404, HEADERS


@app.route('/tweets', methods=['POST'])
def save_tweet():
    tweet = json.loads(request.get_data(as_text=True))

    with get_db_cursor() as cursor:
        result = Storage.save_tweet(cursor, tweet['tweet'])

    return result, 201, HEADERS


@app.route('/tweets/<int:id>', methods=['DELETE'])
def delete_tweet(id):

    with get_db_cursor() as cursor:
        result = Storage.delete_tweet(cursor, id)

    if result:
        return '{}', 204, HEADERS
    else:
        return '{}', 404, HEADERS


if __name__ == '__main__':
    app.run()
