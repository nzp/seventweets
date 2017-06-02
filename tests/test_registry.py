from collections import namedtuple
import json

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
            'node1': node1,
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

        test_nodes = json.loads(node_data['known_nodes_json'])

        try:
            result_nodes = json.loads(Registry.known_nodes)
        except json.JSONDecodeError:
            assert False

        # List comparisons consider order of elements.
        try:
            for elem in result_nodes:
                test_nodes.remove(elem)
        except ValueError:
            assert False
        else:
            assert not test_nodes

    def test_delete_node(self, node_data):
        Registry._known_nodes = node_data['known_nodes']
        node = node_data['node1']

        assert node in Registry._known_nodes
        Registry.delete_node('node1')
        assert node not in Registry._known_nodes
