from collections import namedtuple
import json

from seventweets.config import Config


class classproperty:
    def __init__(self, fget):
        self.fget = fget

    def __get__(self, obj, objtype):
        return self.fget(objtype)


class Registry:
    _known_nodes = set()
    _self_node = {'name': Config.NAME, 'address': Config.ADDRESS}
    _Node = namedtuple('_Node', 'name, address')

    @classmethod
    def register(cls, node):
        cls._known_nodes.add(cls._Node(**node))


    @classproperty
    def known_nodes(cls):
        node_list = [n._asdict() for n in cls._known_nodes]
        node_list.append(cls._self_node)
        return json.dumps(node_list)

