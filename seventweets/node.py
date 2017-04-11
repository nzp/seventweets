import json

from flask import Flask
from flask import request

from seventweets.storage import Storage


HEADERS = {'Content-Type': 'application/json; charset=utf=8'}

app = Flask(__name__)

@app.route('/tweets')
def get_tweets():
    return Storage.get_all(), 200, HEADERS

@app.route('/tweets/<int:id>')
def get_tweet(id):
    tweet = Storage.get_tweet(id)

    if tweet:
        return tweet, 200, HEADERS
    else:
        return '{}', 404, HEADERS

@app.route('/tweets', methods=['POST'])
def save_tweet():
    tweet = json.loads(request.data)

    return Storage.save_tweet(tweet['tweet']), 201, HEADERS

@app.route('/tweets/<int:id>', methods=['DELETE'])
def delete_tweet(id):
    if Storage.delete_tweet(id):
        return '{}', 204, HEADERS
    else:
        return '{}', 404, HEADERS


if __name__ == '__main__':
    app.run()
