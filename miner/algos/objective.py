import math
from miner.DS.Embeddings import Ids, MinMaxCov, Cov
from miner.misc import get_prob, Edge
import networkx as nx
import ipdb as pdb

__author__ = 'Pranay Anchuri'

# value of the objective function
# TODO : obtain better bounds for the union probability using multicherry construction


def intersect_prob(e1, e2):
    """
    Compute the probability that both the embeddings occur in a possible world
    :param e1: list - of three tuples (src, des, prob) in the first embedding
    :param e2: list - of three tuples (src, des, prob) in the second embedding
    :return: float - <= 1 and >0
    """
    mul = lambda x, y: x * y
    pr1 = reduce(mul, [pr for _, _, pr in e1], 1.0)
    pr2 = reduce(mul, [pr for _, _, pr in e2], 1.0)
    prmap = dict([(Edge(src, des), pr) for src, des, pr in e1])
    common = set([Edge(src, des) for src, des, _ in e1]).intersection([Edge(src, des) for src, des, _ in e2])
    pr3 = reduce(mul, [prmap[ed] for ed in common], 1.0)
    assert pr3 >= 0
    return (pr1 * pr2) / float(pr3)


def lower_bound(gr):
    """
    return the lower bound for the intersection of the probabilities
    :param gr: Graph -- networkx graph with intersection probabilities on the edges
    :return: float -- lower bound on the probability of the union event
    """
    node_wts = sum(attr['weight'] for _, attr in gr.nodes(data=True))
    edge_wts = sum(attr['weight'] for _, _, attr in gr.edges(data=True))
    # the two quantities have to added because the edge weights are negative already
    try:
        assert node_wts + edge_wts >= 0.0
    except AssertionError:
        pdb.set_trace()
    return node_wts + edge_wts


def lower_bound_caen(gr):
    """
    See the article "A lower bound on the probability of a union" by Caen
    :param gr: Graph where each node correspond to an embedding
    :return: lower bound on the prob of union of embeddings
    """
    lb = 0.0
    for ev1, attr1 in gr.nodes(data=True):
        non_zero_nbrs = [(nbr, -1.0 * gr.edge[ev1][nbr]['weight']) for nbr in gr.neighbors(ev1) if
                         -1.0 * gr.edge[ev1][nbr]['weight'] > 0]
        selfwt = attr1['weight']
        if non_zero_nbrs:
            lb += (selfwt ** 2) / float(sum(wt for _, wt in non_zero_nbrs))
    try:
        assert lb >= 0
    except AssertionError:
        pdb.set_trace()
    return lb


def lower_bound_caen2(gr):
    """
    See http://imgur.com/fvq4FLZ
    :param gr:
    :return:
    """
    if not gr:
        return 0.0
    s1 = sum(attr['weight'] for _, attr in gr.nodes(data=True))
    s2 = sum(-1.0 * attr['weight'] for _, _, attr in gr.edges(data=True))
    try:
        frac = float(2 * s2) / float(s1)
    except ZeroDivisionError:
        pdb.set_trace()
    theta = frac - math.floor(frac)
    return theta * s1 * s1 / float((2 - theta) * s1 + 2 * s2) + (
        (1 - theta) * s1 * s1 / float((1 - theta) * s1 + 2 * s2))


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
    lbnd = lower_bound_caen2(gr)
    upperbound = union_bound - sum(-1.0 * attr['weight'] for _, _, attr in span_edges)
    try:
        assert (upperbound - lbnd) >= -1.0 * math.pow(10, -4)
    except AssertionError:
        pdb.set_trace()
    return MinMaxCov(lbnd, upperbound)


def mappings_to_edges(db, E, pat):
    edges = [(E[src], E[des], get_prob(db, E[src], E[des])) for src, des in pat.edges()]
    return edges


def obj_value(pat, db, embeddings, edges=None, update_cov=False):
    """
    Returns the coverage of the pattern in the database
    :param update_cov: boolean -- if true coverage of the edges are updated
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
        # edges = [(E[src], E[des], get_prob(db, E[src], E[des])) for src, des in pat.edges()]
        embeddings_edges.append(mappings_to_edges(db, E, pat))
    # compute the coverage of every edge
    total_cov = MinMaxCov()
    for ed, vals in embeddings.Inv_Mappings.items():
        if not edges or ed in edges:
            this_cov = union_prob([embeddings_edges[index] for index in vals[Ids]])
            if update_cov:
                embeddings.Inv_Mappings[ed][Cov] = this_cov
            total_cov.MinCov += this_cov.MinCov
            total_cov.MaxCov += this_cov.MaxCov
    return total_cov


def compute_coverage_scores(pat, db, emb):
    """
    Update the coverage scores of the edges in the pattern and return the value of the objective function
    :param pat: Pattern -
    :param emb: namedtuple - of the type Embed
    :return: namedtuple - of the type MinMax Coverage
    """
    return obj_value(pat, db, emb, update_cov=True)
