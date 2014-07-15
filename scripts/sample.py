#sample a graph from the complete graph
from collections import deque
import os
import pickle
import sys
import networkx as nx
from db2 import add_node, add_edge
from miner.misc import *
import random
import numpy as np
import ipdb as pdb


def read_mapping(labfile):
    labels = {}
    with open(labfile) as f:
        for line in f:
            line = line.strip()
            sp = line.split("\t")
            labels[int(sp[0])] = sp[2]
    return labels


def read_gr(probfile, labels):
    with open(probfile) as f:
        G = nx.parse_edgelist(f.xreadlines(), nodetype = int, data=(('Edge Probability',float),))
        return G


def forest_fire(gr, numNodes, pf):
    """
    Forest fire algorithm by jure leskovec
    :param gr:
    :param numNodes:
    :param pf: float
    :return:
    """
    sampled = set()
    while len(sampled) < numNodes:
        # pick a node randomly
        seed = random.choice(list(set(gr.nodes()).difference(sampled)))
        sampled.add(seed)
        q = deque([seed])
        while q:
            # pop the top element and explore its neighbors
            tp = q.popleft()
            sampled.add(tp)
            unvisited_nbrs = set(gr.neighbors(tp)).difference(sampled)
            # generate a geometric random number
            rn = np.random.geometric(pf)
            minvisit = min(len(unvisited_nbrs), rn)
            nbrs = random.sample(unvisited_nbrs, minvisit)
            q.extend(nbrs)
            if len(sampled) > numNodes:
                break
    subgr = gr.subgraph(sampled)
    return subgr

def add_labels(gr, labelmap):
    for nd in gr:
        gr.node[nd]['Node Label'] = labelmap[nd]

if __name__ == '__main__':
    labels = read_mapping(sys.argv[1])
    gr = read_gr(sys.argv[2], labels)
    #numnodes = [100, 500, 1000, 2000, 5000, 10000, 20000]
    numnodes = [100, 500, 1000, 2000, 5000, 10000, 20000]
    #numnodes = [100]
    for nn in numnodes:
        print "Generating", nn
        subgr = forest_fire(gr, nn, 0.4)
        # add labels to the graph nodes
        add_labels(subgr, labels)
        pickle.dump(subgr, open("Graph%d.gr" % nn, "w"))
        pdb.set_trace()
    pdb.set_trace()
