from collections import defaultdict
import ipdb as pdb
import networkx as nx
from miner.preprocess.examples import create_lab_node, create_prob_edge
import sys

__author__ = 'Pranay Anchuri'

# create a dataset from the interactions and the mappings


def create_labels(mapfile, Nodes=None):
    """
    Mapping from the protein identifier to the group
    Format :
    ##protein       start_position  end_position    orthologous_group       protein_annotation

    :param Nodes: set -- create mapping only for these set of nodes
    :param mapfile: file that contains the mapping for the organism
    :return:
    """
    f = open(mapfile)
    labels = defaultdict(str)
    while True:
        line = f.readline().strip()
        if not line:
            break
        sp = line.split("\t")
        if not Nodes:
            labels[sp[0]] = sp[3]
        elif sp[0] in Nodes:
            labels[sp[0]] = sp[3]
    return labels


def create_gr(interactions, labels):
    """
    Create a probabilistic graph from the interactions
    :param interactions:
    :return:
    """
    f = open(interactions)
    gr = nx.Graph()
    while True:
        line = f.readline().strip()
        if not line:
            break
        sp = line.split()
        nid1, nid2 = sp[0], sp[1]
        if nid1 not in labels or nid2 not in labels:
            continue
        # add the nodes and the edge
        gr.add_nodes_from([create_lab_node(nid, labels[nid]) for nid in [nid1, nid2]])
        # add the edge
        gr.add_edges_from([create_prob_edge(sp[0], sp[1], float(sp[2])/1000.0)])
    return gr


if __name__ == '__main__':
    labels = create_labels(sys.argv[1])
    gr = create_gr(sys.argv[2], labels)
    pdb.set_trace()
