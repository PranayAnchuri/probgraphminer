from miner.misc import get_prob

__author__ = 'Pranay Anchuri'


def embedding_prob(edges, graph):
    return reduce(lambda x, y: x*y, [get_prob(graph, src, des) for src, des in [list(ed) for ed in edges]], 1)


def union_bound(edge_sets, graph):
    return sum(embedding_prob(edges, graph) for edges in edge_sets)
