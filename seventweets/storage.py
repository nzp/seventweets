import json


NODE_NAME = 'nzp'

class Tweet:
    _tw_id = 0

    def __init__(self, tweet):
        self.id = self.__class__._tw_id
        self.name = NODE_NAME
        self.tweet = tweet

        self.__class__._tw_id += 1

    def __str__(self):
        return self.tweet


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
        return json.dumps(cls._tweets[id].__dict__)

    @classmethod
    def delete_tweet(cls, id):
        del cls._tweets[id]
