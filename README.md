# SevenTweets

[![Build Status](https://travis-ci.org/nzp/seventweets.svg?branch=master)](https://travis-ci.org/nzp/seventweets)

SevenTweets is a network of mini services that should resemble twitter.  Each
service that will be part of SevenTweets can have different implementation but
will be built to support a standardised API so that the communication between
services can be possible.  Every node in SevenTweets would:

*  Be a separate service,
*  be able to work with tweets (published message),
*  have its own identificator (username),
*  have its own local storage for tweets originating from that node,
*  have to know addresses of all other nodes,
*  Perform notifications to other nodes when starting/shutting down.


## API endpoints

*  `GET /tweets`

    Returns: `[{"id": 1, "name": "zeljko", "tweet": "this is tweet"}, ...]`  
    Status code: 200

*  `GET /tweets/<id>`

    Returns: `{"id": "...", "name": "...", "tweet": "..."}`  
    Status code : 200

*  `POST /tweets`

    Request body: `{"tweet": "..."}`  
    Returns: `{"id": "...", "name": "...", "tweet": "..."}`  
    Status code: 201

*  `DELETE /tweets/<id>`  
    Status code 204
