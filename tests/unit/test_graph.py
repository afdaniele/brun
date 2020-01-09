import os
import brun
import unittest
import networkx as nx

from brun.lib import _complete_graph
from brun.exceptions import InvalidConfigurationError

SHOW_GRAPH = False


class TestConfig(unittest.TestCase):
    def _test(self, G):
        _complete_graph(G)
        _render_graph(G)

    def test_empty_graph(self):
        G = nx.Graph()
        self._test(G)

    def test_1node_graph(self):
        G = nx.Graph()
        G.add_node('n1')
        self._test(G)

    def test_2nodes_nogroup_graph(self):
        G = nx.Graph()
        G.add_nodes_from(['n1', 'n2'])
        self._test(G)

    def test_2nodes_1group_graph(self):
        G = nx.Graph()
        G.add_nodes_from(['n1', 'n2'])
        G.add_edge('n1', 'n2', type='zip')
        self._test(G)

    def test_3nodes_2groups_graph(self):
        G = nx.Graph()
        G.add_nodes_from(['n1', 'n2', 'n3'])
        G.add_edge('n1', 'n2', type='zip')
        G.add_edge('n2', 'n3', type='zip')
        self._test(G)

    def test_3nodes_2groups_undirected_graph(self):
        G = nx.Graph()
        G.add_nodes_from(['n1', 'n2', 'n3'])
        G.add_edge('n1', 'n2', type='zip')
        G.add_edge('n1', 'n3', type='zip')
        self._test(G)

    def test_3nodes_loop_graph(self):
        G = nx.Graph()
        G.add_nodes_from(['n1', 'n2', 'n3', 'n4'])
        G.add_edge('n1', 'n2', type='zip')
        G.add_edge('n2', 'n3', type='zip')
        G.add_edge('n3', 'n1', type='zipl')
        try:
            self._test(G)
        except InvalidConfigurationError as e:
            self.assertEqual({'n1', 'n2', 'n3'}, e.data)

    def test_4nodes_2groups_graph(self):
        G = nx.Graph()
        G.add_nodes_from(['n1', 'n2', 'n3', 'n4'])
        G.add_edge('n1', 'n2', type='zip')
        G.add_edge('n3', 'n4', type='zip')
        self._test(G)

    def test_4nodes_fork_graph(self):
        G = nx.Graph()
        G.add_nodes_from(['n1', 'n2', 'n3', 'n4'])
        G.add_edge('n2', 'n1', type='zip')
        G.add_edge('n2', 'n3', type='zip')
        G.add_edge('n2', 'n4', type='zip')
        try:
            self._test(G)
        except InvalidConfigurationError as e:
            self.assertEqual({'n1', 'n2', 'n3', 'n4'}, e.data)

    def test_6nodes_2components_1fork_graph(self):
        G = nx.Graph()
        G.add_nodes_from(['n1', 'n2', 'n3', 'n4', 'n5', 'n6'])
        G.add_edge('n2', 'n3', type='zip')
        G.add_edge('n2', 'n4', type='zip')
        G.add_edge('n2', 'n5', type='zip')
        G.add_edge('n1', 'n6', type='zip')
        try:
            self._test(G)
        except InvalidConfigurationError as e:
            self.assertEqual({'n2', 'n3', 'n4', 'n5'}, e.data)


def _render_graph(G):
    if not SHOW_GRAPH:
        return
    s = ''
    processed = set()
    for u in G.nodes:
        s += ' [{}]->({})'.format(
            u, ','.join([
                '{}:{}'.format(G.get_edge_data(u, v)['type'], v)
                for v in set(G.neighbors(u)).difference(processed)
            ]))
        processed.add(u)
    s = '\nGraph: ' + (s if len(s) else '[]')
    print(s)


if __name__ == '__main__':
    unittest.main()
