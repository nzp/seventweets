import json
import itertools
import functools

import pg8000


NODE_NAME = 'nzp'


class Tweet:

    def __init__(self, tweet):
        """Initialize a tweet object from the list returned by pg8000."""

        self.id = tweet[0]
        self.name = tweet[1]
        self.tweet = tweet[2]

    def __str__(self):
        return self.tweet

    def jsoned(self):
        return json.dumps({'id': self.id, 'name': self.name, 'tweet': self.tweet})


#def uses_db(f):
#    @functools.wraps(f)
#    def wrapper(cls, *args, **kwargs):
#        cursor = cls._connection.cursor()
#        res = f(cls, cursor, *args, **kwargs)
#        cursor.close()
#        cls._connection.commit()
#
#        return res
#
#    return wrapper
#
#
#class Storage:
#    _connection = pg8000.connect(user='radionica', password='P4ss')
#
#    @classmethod
#    @uses_db
#    def save_tweet(cls, tweet):
#        t = Tweet(tweet)
#        cls._tweets[t.id] = t
#
#        return json.dumps(t.__dict__)
#
#    @classmethod
#    @uses_db
#    def get_all(cls, cursor):
#        cursor.execute('SELECT id, name, tweet FROM tweets')
#
#        return json.dumps([Tweet(*tweet).jsoned() for tweet in cursor.fetchall()])
#
#    @classmethod
#    def get_tweet(cls, cursor, id):
#        cursor.execute(
#            'SELECT id, name, tweet FROM tweets WHERE id = {id}'.format(id))
#
#        res = cursor.fetchone()
#        if res:
#            return Tweet(*res).jsoned()
#        else:
#            return None
#
#    @classmethod
#    def delete_tweet(cls, id):
#        tweet_id = cls._tweets.pop(id, None)
#
#        if tweet_id or tweet_id == 0:
#            return True
#        else:
#            return False
#
