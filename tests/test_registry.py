from collections import namedtuple
import json
from unittest.mock import patch

import pytest
from pytest_mock import mocker

from seventweets.registry import Registry


@pytest.fixture(scope='function')
def node_data():
    Node = namedtuple('Node', 'name, address')

    node1 = Node(name='node1', address='node1.example.com')
    node2 = Node(name='node2', address='node2.example.com')

    node3 = {'name': 'node3', 'address': 'node3.example.com'}

    known_nodes = {node1, node2}
    self_node = {'name': None, 'address': None}

    known_nodes_json = json.dumps([node1._asdict(), node2._asdict(), self_node])

    return {'node': node3,
            'known_nodes': known_nodes,
            'known_nodes_json': known_nodes_json}



@pytest.mark.usefixture('node_data')
class TestRegistry:

    def test_register(self, node_data):
        Node = namedtuple('Node', 'name, address')

        node = node_data['node']
        known_nodes = node_data['known_nodes']

        Registry._known_nodes = known_nodes.copy()
        Registry.register(node)
        known_nodes.add(Node(**node))

        assert Registry._known_nodes == known_nodes

    def test_known_nodes(self, node_data):
        Registry._known_nodes = node_data['known_nodes']

        assert Registry.known_nodes == node_data['known_nodes_json']