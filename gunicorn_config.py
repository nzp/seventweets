bind = "0.0.0.0:8000"
worker_class = "gthread"
threads = 10


def on_exit(server):
    import requests

    from seventweets.registry import Registry
    from seventweets.config import Config

    for node in Registry._known_nodes:
        endpoint = 'http://{address}/registry/{name}'.format(address=node.address,
                                                             name=Config.NAME)
        r = requests.delete(endpoint)
