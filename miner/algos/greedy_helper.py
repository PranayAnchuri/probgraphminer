from collections import defaultdict
import pdb
from miner.DS.Embeddings import Ids
from miner.misc import Edge

__author__ = 'Pranay Anchuri'


def get_inv_mapping(pat, embeddings):
    print "Embeddings are", embeddings
    print "Pattern is ", pat
    InvMapping = defaultdict(lambda: [[], 0])
    for src, des in pat.edges():
        for index, e in enumerate(embeddings):
            InvMapping[Edge(e[src], e[des])][Ids].append(index)
    return InvMapping
