__author__ = 'Pranay Anchuri'

# functions that return sample probabilistic graphs
import networkx as nx
from ..misc import NodeLab, EdgePr
import pdb


def create_lab_node(id, lab):
    return id, {"%s" % NodeLab: lab}


def create_prob_edge(id1, id2, prob):
    return id1, id2, {"%s" % EdgePr: prob}


def triangle():
    gr = nx.Graph()
    gr.add_nodes_from(create_lab_node(id, lab) for id, lab in [(1, 'A'), (2, 'B'), (3, 'C')])
    gr.add_edges_from(create_prob_edge(id1, id2, prob) for id1, id2, prob in [(1, 2, 0.8), (2, 3, 0.9), (1, 3, 0.6)])
    return gr
