from collections import defaultdict
import operator
import ipdb as pdb
import pprint as pp
from miner.DS.Embeddings import *
from miner.DS.pattern import Pattern
from miner.algos.compare_ext import cmp_ext
from miner.algos.greedy_helper import get_inv_mapping
from miner.algos.objective import obj_value, compute_coverage_scores
from miner.misc import get_label, LabelPair, get_prob, Edge, EdgePr
from miner.misc.logger import get_logger
from miner.tests.test_embeddings import test_valid_embeddings

__author__ = 'Pranay Anchuri'

# Greedy algorithm to construct k patterns that maximizes the value of the objective function

logger = get_logger(__name__)


def get_remaining_coverage(db, all_embeddings):
    """
    Compute the remaining coverage for each edge in the graph; group the edges based on the labels of the end nodes
    :param all_embeddings : Embed - embeddings of all the patterns constructed till now; the coverage of an edge is the cumulative
    coverage by all the patterns that are computed till now
    :return: dict - key is pair of labels and the value is a dict with edges as keys and the cumulative coverage as the value
    """
    rem_cov = defaultdict(lambda: defaultdict(MinMaxCov))
    for src, des, attr in db.edges(data=True):
        prob = attr[EdgePr]
        l1, l2 = get_label(db, src), get_label(db, des)
        if Edge(src, des) in all_embeddings.Inv_Mappings:
            curr_cov = all_embeddings.Inv_Mappings[Edge(src, des)][Cov]
        else:
            curr_cov = MinMaxCov()
        try:
            assert curr_cov.MinCov <= prob
        except AssertionError:
            pdb.set_trace()
        rem_cov[LabelPair(l1, l2)][Edge(src, des)] = MinMaxCov(max(prob - curr_cov.MaxCov, 0), prob - curr_cov.MinCov)
    return rem_cov


def get_best_l1(rem_cov):
    """
    Get the best l1 pattern from the remaining edges
    :param rem_cov: dict
    :return: Pattern, Embedding of l1
    """
    potentials = [(k, sum(cov.MinCov for cov in coverages.values())) for k, coverages in rem_cov.items()]
    ((l1, l2), pot) = max(potentials, key=operator.itemgetter(1))
    pat = Pattern()
    pat.add_single_edge(l1, l2)
    return pat


def create_embeddings(rem_cov, pat, db):
    """
    Create embedding object for the single edge pattern pat
    :param rem_cov:
    :param db:
    :return:
    """
    l1, l2 = [get_label(pat, nd) for nd in pat.nodes()]
    mappings = []
    InvMapping = defaultdict(lambda: [[], MinMaxCov()])
    idx = 0
    for ed, _ in rem_cov[LabelPair(l1, l2)].items():
        src, des = list(ed)
        mappings.append([src, des] if get_label(db, src) == l1 else [des, src])
        prob = get_prob(db, src, des)
        InvMapping[ed][Ids] = [idx]
        InvMapping[ed][Cov] = MinMaxCov(prob, prob)
        idx += 1
    return Embed(mappings, InvMapping)


def get_single_pattern(db, output, all_embeddings):
    rem_cov = get_remaining_coverage(db, all_embeddings)
    pat = get_best_l1(rem_cov)
    # now create embedding object for the pattern "pat"
    emb = create_embeddings(rem_cov, pat, db)
    return pat, emb


def explore_neighborhood(E, pat, db):
    """
    Explore the one neighborhood of E
    :param E: list
    :param pat: Pattern
    :param db: Database Graph
    :return: dict - key is the extension ( a 3 tuple (True, patid1, lab) for
    forward extension, (False, patid1, patid2) for backward extension
    """
    ext = defaultdict(list)
    back_edges = set() # set of back edge extensions added to this extension
    for patv in pat.nodes():
        dbv = E[patv]
        # check the neighbors of dbv
        for nbr in db.neighbors(dbv):
            if nbr not in E:
                # forward extension for sure
                lab = get_label(db, nbr)
                ext[(True, patv, lab)].append(nbr)
            else:
                # make sure that the edge is not in the pattern already
                # TODO : The statement below works only when the pattern
                # vertices are [0, 1, ..., |P| -1]
                pat_des = E.index(nbr)
                if not pat.has_edge(patv, pat_des):
                    if Edge(patv, pat_des) not in back_edges:
                        ext[(False, patv, pat_des)].append((dbv, nbr))
                        back_edges.add(Edge(patv, pat_des))
    return ext


def get_extensions(pat, emb, output, db):
    """
    Explore the neighborhood of current embeddings and compute the best extension
    :param pat: Pattern- Current pattern
    :param emb: Embed - namedtuple that contains the embeddings and the inverse mappings
    :param output: list - of patterns constructed till now
    :param db: Graph - Input Graph
    :return: Status, Pattern, Embed
    """
    mappings = defaultdict(list) # key is the extension type and value is the embeddings of the pattern
    for E in emb.Mappings:
        # explore the neighborhood of E
        this_ext = explore_neighborhood(E, pat, db)
        for tp, ext in this_ext.items():
            if tp[0]: # forward extension
                # add the embeddings
                for dbvid in ext:
                    mappings[tp].append(E + [dbvid])
            else: # the extension is backward
                mappings[tp].append(E)
    # get the inverse mapping of the embeddings
    extensions = {}
    for tp, emb in mappings.items():
        patprime = Pattern(pat)
        patprime.add_edge_by_type(tp)
        try:
            inv_mappings = get_inv_mapping(patprime, emb)
        except TypeError:
            pdb.set_trace()
        extensions[patprime] = Embed(emb, inv_mappings)
    return extensions


def get_best_extension(pat, emb, output, db, all_embeddings):
    """

    :param pat:
    :param emb:
    :param output:
    :param db:
    :param all_embeddings: Embed - embeddings of all the patterns till now
    :return:
    """
    extensions = get_extensions(pat, emb, output, db)
    if not extensions:
        return False, pat, emb, MinMaxCov()
    logger.info("Possible extensions of the pattern are %s " % pp.pformat(extensions.keys()))
    best_ext, best_emb, best_cov = cmp_ext(pat, db, emb, output, extensions, all_embeddings)
    logger.info("The best extension is %s " % pp.pformat(best_ext))
    status = False
    if best_cov.MaxCov > 0:
        status = True
    else:
        best_ext = pat
        best_emb = emb
    pdb.set_trace()
    total_cov = compute_coverage_scores(best_ext, db, best_emb)
    return status, best_ext, best_emb, total_cov


def get_next_pattern(db, output, all_embeddings):
    pat, emb = get_single_pattern(db, output, all_embeddings)
    logger.info("Iteration starts with single edge pattern %s" % pat.__str__())
    logger.debug(nt_str(emb))
    while True:
        status, next_pat, next_emb, cov = get_best_extension(pat, emb, output, db, all_embeddings)
        if status:
            logger.info("Extension of the pattern is %s " % pat.__str__())
            logger.debug(nt_str(emb))
            logger.debug("Total coverage %s" % pp.pformat(cov))
            pat = next_pat
            emb = next_emb
        else:
            logger.info("Pattern cannot be extended anymore")
            break
        emb = remove_duplicate_embeddings(pat, emb)
    logger.info("Pattern constructed in this iteration is %s" % pat.__str__())
    logger.debug(nt_str(emb))
    return pat, emb


def union_coverage(prev_cov, next_cov):
    """
    Total coverage of the pattern by merging both the coverages
    See http://imgur.com/fJokqsU
    :param prev_cov:
    :param next_cov:
    :return:
    """
    new_min = prev_cov.MinCov + next_cov.MinCov - min(prev_cov.MaxCov, next_cov.MaxCov)
    new_max = prev_cov.MaxCov + next_cov.MaxCov - prev_cov.MinCov * next_cov.MinCov
    return new_min, new_max


def post_pat_const(pat, embeddings, output, all_embeddings):
    """
    Append the pattern and update all_embeddings

    :param pat: Pattern - pattern that is a result of greedy construction algorithm
    :param embeddings: Embed - Embeddings of the pattern
    :param output: list - set of patterns that are constructed till now
    :param all_embeddings: Embed - embeddings of all the patterns till now
    :return: None

    """
    output.append(pat)
    # add the embeddings
    offset = len(all_embeddings.Mappings)
    all_embeddings.Mappings.extend(embeddings.Mappings)
    for ed, invmap in embeddings.Inv_Mappings.items():
        all_embeddings.Inv_Mappings[ed][Ids].extend(index + offset for index in invmap[Ids])
        # get the new coverage of the edge
        new_min, new_max = union_coverage(invmap[Cov], all_embeddings.Inv_Mappings[ed][Cov])
        all_embeddings.Inv_Mappings[ed][Cov].MinCov = new_min
        all_embeddings.Inv_Mappings[ed][Cov].MaxCov = new_max
    offset = len(all_embeddings.Mappings)
    all_embeddings.Mappings.append([-1])
    all_embeddings.Inv_Mappings[Edge(-1, -1)][Ids].append(offset)


def greedy(db, k):
    """
   Returns k patterns that maximizes the value of the objective function
   :param db: networkx graph with probabilities on the edges
   :param k: Number of patterns required
   :return: list of patterns
   """
    output = []  # contains the patterns constructed
    # contains all the embeddings of all the patterns that are constructed till now
    # embeddings of different patterns are seperated by a [-1]
    all_embeddings = Embed([], defaultdict(lambda: [[], MinMaxCov()]))
    for i in range(k):
        logger.info("Iteration %d of the greedy algorithm" % i)
        pat, embeddings = get_next_pattern(db, output, all_embeddings)
        assert test_valid_embeddings(pat, db, embeddings)
        post_pat_const(pat, embeddings, output, all_embeddings)
        output.append(pat)
    return output
