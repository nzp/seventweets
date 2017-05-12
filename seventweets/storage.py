import json


NODE_NAME = 'nzp'


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
        cursor.execute('SELECT id, name, tweet FROM tweets')

        return json.dumps([Tweet(tweet).__dict__ for tweet in cursor.fetchall()])

    @classmethod
    def get_tweet(cls, cursor, id):
        cursor.execute(
            'SELECT id, name, tweet FROM tweets WHERE id = {}'.format(id))

        res = cursor.fetchone()
        if res:
            return json.dumps(Tweet(res).__dict__)
        else:
            return json.dumps({})

    @classmethod
    def save_tweet(cls, cursor, tweet):
        cursor.execute(
            "INSERT INTO tweets (name, tweet) \
            VALUES ('nzp', '{}') RETURNING id, name, tweet".format(tweet))

        res = cursor.fetchone()

        return json.dumps(Tweet(res).__dict__)

    @classmethod
    def delete_tweet(cls, cursor, id):
        cursor.execute(
            "DELETE FROM tweets WHERE id = {} RETURNING id".format(id))

        result = cursor.fetchone()

        if result:
            return True
        else:
            return False
