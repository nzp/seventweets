"""This module implements storage of tweets.

Classes:
    Tweet: Implements tweet objects.
    Storage: Wrapper for all the database access functions.

"""

import json

from seventweets.config import Config


class Tweet:
    """Implements tweet objects.
    
    Attributes:
        id (int): A unique ID of a tweet.
        name (str): The name of network node to which the tweet belongs.
        tweet (str): Content of tweet.
    
    """

    def __init__(self, tweet):
        """Initialize a tweet object.

        The constructor extracts tweet attributes from the list returned by
        pg8000's ``fetchone()``.

        Args:
            tweet (list): The attributes of a tweet as returned by
                ``fetchone()`` (``[<id>, <name of node>, <tweet body>)]``).

        """
        self.id = tweet[0]
        self.name = tweet[1]
        self.tweet = tweet[2]

    def __str__(self):
        return self.tweet


class Storage:
    """This class encapsulates methods for database access.

    Class methods:
        get_all_tweets: Return all the node's tweets and retweets.
        get_tweet: Return a specific tweet by it's ID.
        save_tweet: Save a tweet to database.
        delete_tweet: Delete a tweet from database.
        search: Search for tweets.
    
    """

    @classmethod
    def get_all_tweets(cls, cursor):
        """Return all tweets and retweets from the database.
        
        Args:
            cursor (:class:`pg8000.Cursor`): Database cursor object.

        Returns:
            str: All tweets and retweets as JSON array of objects
                (``[{"id": <int>, "name": <str>, "tweet": <str>}, ...]``).
        
        """
        cursor.execute('SELECT id, node_name, content FROM tweet')

        return json.dumps([Tweet(tweet).__dict__ for tweet in cursor.fetchall()])

    @classmethod
    def get_tweet(cls, cursor, id):
        """Return a single tweet from the database by it's ID.
        
        Args:
            cursor (:class:`pg8000.Cursor`): Database cursor object.
            id (int): Tweet ID.

        Returns:
            str or None: Tweet as a JSON object (``{"id": <int>, "name": <str>,
                "tweet": <str>}``), or ``None`` if no tweet with ID.
        
        """
        cursor.execute(
            'SELECT id, node_name, content FROM tweet WHERE id = {}'.format(id))

        res = cursor.fetchone()
        if res:
            return json.dumps(Tweet(res).__dict__)
        else:
            return None

    @classmethod
    def save_tweet(cls, cursor, tweet):
        """Save tweet to the database and return it's full JSON representation.

        Args:
            cursor (:class:`pg8000.Cursor`): Database cursor object.
            tweet (str): Content of the tweet.

        Returns:
            str: Saved tweet as a JSON object (``{"id": <int>, "name": <str>,
                "tweet": <str>}``).

        """
        cursor.execute(
            "INSERT INTO tweet (node_name, content) \
            VALUES ('{name}', '{tweet}') RETURNING id, node_name, content".format(
                **{'name': Config.NAME, 'tweet': tweet}))

        res = cursor.fetchone()

        return json.dumps(Tweet(res).__dict__)

    @classmethod
    def delete_tweet(cls, cursor, id):
        """Delete a tweet from the database by ID.

        Args:
            cursor (:class:`pg8000.Cursor`): Database cursor object.
            id (int): ID of the tweet to be deleted.
        
        Returns:
            bool: True on success, False if the tweet ID doesn't exist.
        
        """
        cursor.execute(
            "DELETE FROM tweet WHERE id = {} RETURNING id".format(id))

        result = cursor.fetchone()

        if result:
            return True
        else:
            return False

    @classmethod
    def search(cls, cursor, query):
        """Execute a query on the database and return matching tweets.

        Args:
            cursor (:class:`pg8000.Cursor`): Database cursor object.
            query (str): SQL query to execute.

        Returns:
            str: All tweets as a JSON array of objects (``[{"id": <int>, "name":
                <str>, "tweet": <str>}, ...]``).

        """
        cursor.execute(query)

        return [Tweet(tweet).__dict__ for tweet in cursor.fetchall()]
