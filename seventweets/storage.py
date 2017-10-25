"""This module implements storage of tweets.

Classes:

* Tweet -- Implements tweet objects;
* Storage -- Just a wrapper for all the database access functions.

"""

import json

from seventweets.config import Config


class Tweet:
    """Implements tweet objects.
    
    Instance variables:

    * id -- A unique ID of a tweet;
    * name -- The name of network node to which the tweet belongs (str);
    * tweet -- Content of tweet (str).
    
    """

    def __init__(self, tweet):
        """Initialize a tweet object.

        The constructor extracts tweet attributes from the list returned by
        pg8000's ``fetchone()``.

        :param tweet: The attributes of a tweet as returned from the database.
        :type tweet: List -- ``(<id>, <name of node>, <tweet body>)``.

        """
        self.id = tweet[0]
        self.name = tweet[1]
        self.tweet = tweet[2]

    def __str__(self):
        """Represent a tweet as string by it's body."""
        return self.tweet


class Storage:
    """Collects methods for database access.

    Class methods:

    * ``get_all_tweets`` -- Return all the node's tweets and retweets;
    * ``get_tweet`` -- Return a specific tweet by it's ID;
    * ``save_tweet`` -- Save a tweet to database;
    * ``delete_tweet`` -- Delete a tweet from database;
    * ``search`` -- Search for tweets.
    
    """

    @classmethod
    def get_all_tweets(cls, cursor):
        """Return all tweets and retweets from the database.
        
        :param cursor: A database cursor.
        :type cursor: pg8000 cursor object.

        :return: All tweets and retweets as JSON array of objects:
        ``[{"id": <int>, "name": <str>, "tweet": <str>}, ...]``.
        :rtype: str
        
        """
        cursor.execute('SELECT id, node_name, content FROM tweet')

        return json.dumps([Tweet(tweet).__dict__ for tweet in cursor.fetchall()])

    @classmethod
    def get_tweet(cls, cursor, id):
        """Return a single tweet from the database by it's ID.
        
        :param cursor: Database cursor.
        :type cursor: pg8000.Cursor
        :param id: Tweet ID.
        :type id: int.

        :returns: Tweet as a JSON object
        (``{"id": <int>, "name": <str>, "tweet": <str>}``), or None if no tweet.
        :rtype: str or None
        
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

        :param cursor: Database cursor.
        :type cursor: pg8000.Cursor
        :param tweet: Tweet body.
        :type tweet: str

        :returns: Tweet as a JSON object
        (``{"id": <int>, "name": <str>, "tweet": <str>}``).
        :rtype: str

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
        
        :param cursor: Database cursor.
        :type cursor: pg8000.Cursor
        :param id: ID of the tweet to be deleted.
        :type id: int

        :returns: True on success, False if the tweet ID doesn't exist.
        :rtype: bool
        
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

        :param cursor: Database cursor.
        :type cursor: pg8000.Cursor
        :param query: SQL query to execute.
        :type query: str

        :return: All tweets as a JSON array of objects:
        ``[{"id": <int>, "name": <str>, "tweet": <str>}, ...]``.
        :rtype: str

        """
        cursor.execute(query)

        return [Tweet(tweet).__dict__ for tweet in cursor.fetchall()]
