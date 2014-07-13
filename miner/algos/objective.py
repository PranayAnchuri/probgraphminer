from miner.DS.Embeddings import Ids, MinMaxCov
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


def lower_bound(gr):
    """
    return the lower bound for the intersection of the probabilities
    :param gr: Graph -- networkx graph with intersection probabilities on the edges
    :return: float -- lower bound on the probability of the union event
    """
    node_wts = sum(attr['weight'] for _, attr in gr.nodes(data=True))
    edge_wts = sum(attr['weight'] for _, _, attr in gr.edges(data=True))
    return node_wts - edge_wts


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
            if prob:
                gr.add_edge(index, index + index2 + 1, weight=-1.0 * prob)
    # compute the weight of minimum spanning tree
    span_edges = list(nx.minimum_spanning_edges(gr))
    lbnd = lower_bound(gr)
    return MinMaxCov(lbnd, union_bound - sum(-1.0 * attr['weight'] for _, _, attr in span_edges))


def mappings_to_edges(db, E, pat):
    edges = [(E[src], E[des], get_prob(db, E[src], E[des])) for src, des in pat.edges()]
    return edges


def obj_value(pat, db, embeddings, edges=None):
    """
    Returns the coverage of the pattern in the database
    :param edges: list -- edges that should be considered for computing the coverage; if None all the edges in inv_mapping
    are considered in the computation
    :param pat: Pattern
    :param db: Graph - input uncertain graph
    :param embeddings: namedtuple -- contains the mappings and the inverse mappings
    :return: Coverage of the pattern
    """
    # get the edges in each embedding
    embeddings_edges = []
    for E in embeddings.Mappings:
        #edges = [(E[src], E[des], get_prob(db, E[src], E[des])) for src, des in pat.edges()]
        embeddings_edges.append(mappings_to_edges(db, E, pat))
    # compute the coverage of every edge
    total_cov = MinMaxCov()
    for ed, vals in embeddings.Inv_Mappings.items():
        if not edges or ed in edges:
            this_cov = union_prob([embeddings_edges[index] for index in vals[Ids]])
            total_cov.MinCov += this_cov.MinCov
            total_cov.MaxCov += this_cov.MaxCov
    return total_cov

