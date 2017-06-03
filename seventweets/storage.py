import json

from seventweets.config import Config


class Tweet:

    def __init__(self, tweet):
        """Initialize a tweet object from the list returned by pg8000."""

        self.id = tweet[0]
        self.name = tweet[1]
        self.tweet = tweet[2]

    def __str__(self):
        return self.tweet


class Storage:

    @classmethod
    def get_all_tweets(cls, cursor):
        cursor.execute('SELECT id, node_name, content FROM tweet')

        return json.dumps([Tweet(tweet).__dict__ for tweet in cursor.fetchall()])

    @classmethod
    def get_tweet(cls, cursor, id):
        cursor.execute(
            'SELECT id, node_name, content FROM tweet WHERE id = {}'.format(id))

        res = cursor.fetchone()
        if res:
            return json.dumps(Tweet(res).__dict__)
        else:
            return False

    @classmethod
    def save_tweet(cls, cursor, tweet):
        cursor.execute(
            "INSERT INTO tweet (node_name, content) \
            VALUES ('{name}', '{tweet}') RETURNING id, node_name, content".format(
                **{'name': Config.NAME, 'tweet': tweet}))

        res = cursor.fetchone()

        return json.dumps(Tweet(res).__dict__)

    @classmethod
    def delete_tweet(cls, cursor, id):
        cursor.execute(
            "DELETE FROM tweet WHERE id = {} RETURNING id".format(id))

        result = cursor.fetchone()

        if result:
            return True
        else:
            return False

    @classmethod
    def search(cls, cursor, query):
        cursor.execute(query)

        return [Tweet(tweet).__dict__ for tweet in cursor.fetchall()]
