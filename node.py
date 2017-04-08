from flask import Flask
from flask import request

from storage import Storage


HEADERS = {'Content-Type': 'application/json; charset=utf=8'}

app = Flask(__name__)

@app.route('/tweets/')
def get_tweets():
    return Storage.get_all(), 200, HEADERS

@app.route('/tweets/<int:id>/')
def get_tweet(id):
    try:
        return Storage.get_tweet(id), 200, HEADERS
    except KeyError:
        return '', 404

@app.route('/tweets/', methods=['POST'])
def save_tweet():
    Storage.save_tweet(str(request.data))
    return 'OK'


if __name__ == '__main__':
    app.run()
