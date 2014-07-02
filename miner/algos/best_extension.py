from miner.algos.prob_bounds import union_bound

__author__ = 'Pranay Anchuri'

# from all possible extensions of the current pattern find the extension that leads to maximum
# increase in the value of the objective function


def get_min_score_change(curr_embedding_edges, edge_sets, new_mapped_edges):
    return 0


def get_max_score_change(curr_embedding_edges, edge_sets, new_mapped_edges, graph):
    """
    Maximum improvement in the obj func score for the extension corresponding to new edge sets
    :param curr_embedding_edges:
    :param edge_sets:
    :param new_mapped_edges:
    :return:
    """
    inc = 0
    for ed in new_mapped_edges:
        # get the embeddings that contain this edge
        incident_embeddings = filter(lambda x: ed in x, edge_sets)
        # compute an upper bound of the probability that at least one of the embedding is realized
        inc += union_bound(incident_embeddings, graph)
    return inc


def choose_extension(pat, graph, curr_embedding_edges, next_embedding_edges, new_mapped_edges):
    """
    Finds the extension of the pattern that leads to maxium increase in the value of the objective function.
    Given the embeddings of the pattern as a list of edge sets and the edge sets corresponding to various extensions
    of the pattern, it estimates the change in obj function for each extension.

    Note that the objective function can only increase for the new_mapped_edges.

    Algo : Order extensions by the improvement they can bring.
        1) Estimate a lower bound and upper bound of the change in obj function for each extension.
        2) Prune some extensions based on the bounds.
        3) Tighten the bounds and repeat

    :param pat:
    :param graph:
    :param curr_embedding_edges: set of embeddings
    :param next_embedding_edges: dict; key is the type and value is a set of embeddings
    :param new_mapped_edges: dict - map of new edges for each type
    :return:
    """

    MIN, MAX = 0, 1
    scores = dict((ext_type, [None, ()]) for ext_type in next_embedding_edges.keys())
    for ext_type, edge_sets in next_embedding_edges:
        scores[ext_type][MIN] = get_min_score_change(curr_embedding_edges, edge_sets, new_mapped_edges)
        scores[ext_type][MAX] = get_max_score_change(curr_embedding_edges, edge_sets, new_mapped_edges)

