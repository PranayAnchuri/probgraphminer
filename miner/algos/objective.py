from miner.DS.Embeddings import Ids
from miner.misc import get_prob, Edge
import networkx as nx
import ipdb as pdb

__author__ = 'Pranay Anchuri'

# value of the objective function


def intersect_prob(e1, e2):
    edges1 = dict((Edge(src, des), pr) for src, des, pr in e1)
    edges2 = dict((Edge(src, des), pr) for src, des, pr in e2)
    common = set(edges1.keys()).intersection(edges2.keys())
    if not common:
        return 0
    return reduce(lambda x, y: x * y, [edges1[ed] for ed in common], 1.0)


def union_prob(edgesets):
    # construct complete graph to compute an upper bound for the union probability
    gr = nx.Graph()
    union_bound = 0.0
    for index, value in enumerate(edgesets):
        embed_prob = reduce(lambda x, y: x * y, [pr for _, _, pr in value], 1)
        union_bound += embed_prob
        gr.add_node(index, weight=embed_prob)
        for index2, value2 in enumerate(edgesets[index + 1:]):
            # compute the intersection probabilites
            prob = intersect_prob(value, value2)
            if not prob:
                gr.add_edge(index, index + index2, weight=-1.0 * prob)
    # compute the weight of minimum spanning tree
    span_edges = list(nx.minimum_spanning_edges(gr))
    return union_bound - sum(-1.0 * attr['weight'] for _, _, attr in span_edges)


def obj_value(pat, db, embeddings):
    """
    Returns the coverage of the pattern in the database
    :param pat: Pattern
    :param db: Graph - input uncertain graph
    :param embeddings: namedtuple -- contains the mappings and the inverse mappings
    :return: Coverage of the pattern
    """
    # get the edges in each embedding
    embeddings_edges = []
    for E in embeddings.Mappings:
        edges = [(E[src], E[des], get_prob(db, E[src], E[des])) for src, des in pat.edges()]
        embeddings_edges.append(edges)
    # compute the coverage of every edge
    total_cov = 0.0
    for ed, vals in embeddings.Inv_Mappings.items():
        this_cov = union_prob([embeddings_edges[index] for index in vals[Ids]])
        pdb.set_trace()
        total_cov += this_cov
    return total_cov

