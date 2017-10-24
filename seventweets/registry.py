"""This module implements the registry of known/active nodes in the network.

Classes:

* Registry -- a pseudo-singleton class that represents the registry.

"""

from collections import namedtuple
import json

from seventweets.config import Config


class _classproperty:
    # Decorates a class method to make it behave like a class property.

    def __init__(self, fget):
        self.fget = fget

    def __get__(self, obj, objtype):
        return self.fget(objtype)


class Registry:
    _known_nodes = set()
    _self_node = {'name': Config.NAME, 'address': Config.ADDRESS}

    # For easier access to name and address, we store a node as a named tuple
    # instead of an ordinary tuple.
    _Node = namedtuple('_Node', 'name, address')

    @classmethod
    def register(cls, node):
        """Register a node.

        :param node: Name and address of the node.
        :type node: dict (``{"name": <str>, "address": <str>}``).
        
        """
        if node != cls._self_node:
            cls._known_nodes.add(cls._Node(**node))

    @_classproperty
    def known_nodes(cls):
        """Return a list of all known nodes.

        :rtype: JSON array of node objects of form ``{"name": <str>, "address": <str>}``.

        """
        # Because the list of known nodes is a set of named tuples and needs to
        # be processed into final form of a JSON array of node objects, this
        # method is made into a class property via _classproperty so that we
        # can access it as a simple class attribute.

        node_list = [n._asdict() for n in cls._known_nodes]
        node_list.append(cls._self_node)
        return json.dumps(node_list)

    @classmethod
    def delete_node(cls, node):
        """Delete a node from list of known nodes."""

        for n in cls._known_nodes:
            if n.name == node:  # name is the unique ID in the network.
                cls._known_nodes.remove(n)
                break
