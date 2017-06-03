# SevenTweets

[![Build Status](https://travis-ci.org/nzp/seventweets.svg?branch=master)](https://travis-ci.org/nzp/seventweets)
[![codecov](https://codecov.io/gh/nzp/seventweets/branch/master/graph/badge.svg)](https://codecov.io/gh/nzp/seventweets)

SevenTweets is a network of mini services with a REST API that should resemble
twitter (short messages, ability to “retweet” etc.).  Every SevenTweets node

*  is a separate service,
*  is able to work with tweets (published message),
*  has its own identifier (username),
*  has its own local storage for tweets originating from that node,
*  knows addresses of all other nodes,
*  performs notifications to other nodes when starting/shutting down.


## API endpoints

*  `GET /tweets`

    Retrieve all tweets from a node.

    Returns: `[{"id": 1, "name": "zeljko", "tweet": "this is tweet"}, ...]`  
    Status code: 200

*  `GET /tweets/<id>`

    Retrieve a tweet with id.

    Returns: `{"id": "...", "name": "...", "tweet": "..."}`  
    Status code: 200

*  `POST /tweets`

    Post a tweet to own service.

    Request body: `{"tweet": "..."}`  
    Returns: `{"id": "...", "name": "...", "tweet": "..."}`  
    Status code: 201

*  `DELETE /tweets/<id>`

    Delete own tweet (or retweet).

    Status code: 204

*   `POST /tweets/retweet`

    Retweet a tweet from a different node.

    Request body: `{'name': '...', 'id': '...'}` (name of node, and id of tweet)  
    Status code: 200

*  `POST /registry` 

    Announce self to another node.  Receive list of all known nodes.
    
    Request body: `{"name": "...", "address:": "..."}`  
    Returns: `[{"name": "...", "address:": "..."}, ...]`  
    Status code: 200

*  `DELETE /registry/<name>`

    Delete node with `<name>` from known nodes.  Used to announce own shutdown.  
    Status code: 204

*  `GET /search`

    Search locally or across the network depending on the `all` parameter.

    Query string parameters: `content`, `created_from`, `created_to`, `all`  
    Returns: `[{"id": 1, "name": "zeljko", "tweet": "this is tweet"}, ...]`  
    Status code: 200

*  `POST /join_network`

    Initiate joining the network if not already in.

    Request body: `{"name": "...", "address:": "..."}`  
