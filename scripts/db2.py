from collections import defaultdict
import ipdb as pdb
import sys
import pickle

__author__ = 'Pranay Anchuri'

import os
import networkx as nx
from miner.misc import *

# create a dataset for each species


def read_labels(fname):
    labels = {}
    with open(fname) as f:
        for line in f:
            try:
                protein, group = line.strip().split("\t")
            except ValueError:
                pdb.set_trace()
            labels[protein] = group
    return labels

def get_protein(ax):
    return ax.split(".")[1]


def add_node(gr, nid, lab):
    gr.add_node(nid)
    gr.node[nid][NodeLab] = lab


def add_edge(gr, nid1, nid2, prob):
    gr.add_edge(nid1, nid2)
    gr.edge[nid1][nid2][EdgePr] = prob


def create_graph(interactions, labels, minprob=0.45):
    gr = nx.Graph()
    with open(interactions) as f:
        for line in f:
            if line.startswith("protein") or len(line.split()) <3:
                continue
            line = line.strip()
            try:
                n1, n2, prob = line.split()
            except ValueError:
                pdb.set_trace()
            p1, p2 = [get_protein(n) for n in [n1, n2]]
            prob = float(prob)/1000.0
            if p1 in labels and p2 in labels and prob >= minprob:
                # add nodes to the graph
                add_node(gr, p1, labels[p1])
                add_node(gr, p2, labels[p2])
                # add edge to the graph
                add_edge(gr, p1, p2, prob)
    return gr


def read_dir(dirpath):
    files = os.listdir(dirpath)
    prefixes = defaultdict(list)
    [prefixes[x.split(".", 1)[0]].append(x) for x in files]
    for pref, fnames in prefixes.items():
        lab, inter = (os.path.join(dirpath, fnames[0]), os.path.join(dirpath, fnames[1])) if "map" in fnames[0] else (os.path.join(dirpath, fnames[1]), os.path.join(dirpath, fnames[0]))
        assert "map" in lab
        labels = read_labels(lab)
        gr = create_graph(inter, labels)
        pickle.dump(gr, open(os.path.join(dirpath, "%s.gr" % pref), "w"))


if __name__ == '__main__':
    read_dir(sys.argv[1])
