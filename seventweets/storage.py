import json
import itertools

NODE_NAME = 'nzp'


class Tweet:
    _id_counter = None

    @classmethod
    def reset_counter(cls):
        cls._id_counter = itertools.count()

    def __init__(self, tweet):
        self.id = next(self._id_counter)
        self.name = NODE_NAME
        self.tweet = tweet

    def __str__(self):
        return self.tweet


Tweet.reset_counter()


class Storage:
    # Id indexed dictionary of tweets (see save_tweet method).  Maybe overkill,
    # but a lot faster in general than searching a list of Tweet objects for
    # the wanted id.
    _tweets = {}

    @classmethod
    def save_tweet(cls, tweet):
        t = Tweet(tweet)
        cls._tweets[t.id] = t

        return json.dumps(t.__dict__)

    @classmethod
    def get_all(cls):
        return json.dumps([t.__dict__ for t in cls._tweets.values()])

    @classmethod
    def get_tweet(cls, id):
        try:
            tweet = json.dumps(cls._tweets[id].__dict__)
        except KeyError:
            tweet = None

        return tweet

    @classmethod
    def delete_tweet(cls, id):
        tweet_id = cls._tweets.pop(id, None)

        if tweet_id or tweet_id == 0:
            return True
        else:
            return False

