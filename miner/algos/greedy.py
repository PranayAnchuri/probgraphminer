from collections import defaultdict
import operator
import ipdb as pdb
import pprint as pp
from miner.DS.Embeddings import *
from miner.DS.pattern import Pattern
from miner.algos.compare_ext import cmp_ext
from miner.algos.greedy_helper import get_inv_mapping
from miner.algos.objective import obj_value, compute_coverage_scores
from miner.misc import get_label, LabelPair, get_prob, Edge
from miner.misc.logger import get_logger

__author__ = 'Pranay Anchuri'

# Greedy algorithm to construct k patterns that maximizes the value of the objective function

logger = get_logger(__name__)


def get_single_pattern(db, output):
    # return single edge pattern that has maximum remaining coverage
    # key is edge type (pair of labels), value is dict with db edge as the key and value is the remaining coverage
    edge_types = defaultdict(lambda: defaultdict(float))
    for src, des in db.edges():
        l1, l2 = get_label(db, src), get_label(db, des)
        edge_types[LabelPair(l1, l2)][Edge(src, des)] = get_prob(db, src, des)
    # subtract the coverages by previously computed patterns
    rem_coverages = dict([(k, sum(ed.values())) for k, ed in edge_types.items()])
    # construct the pattern from the type with maximum value
    best_type = max(rem_coverages.items(), key=operator.itemgetter(1))[0]
    l1, l2 = list(best_type)
    pat = Pattern()
    pat.add_single_edge(l1, l2)
    # compute the embeddings for the single edge pattern
    EmbedList = []
    InvMapping = defaultdict(lambda: [[], MinMaxCov()])
    for ed in edge_types[LabelPair(l1, l2)]:
        src, des = list(ed)
        prob = get_prob(db, src, des)
        if l1 == get_label(db, src):
            emb = [src, des]
        else:
            emb = [des, src]
        InvMapping[ed][Ids].append(len(EmbedList))
        InvMapping[ed][Cov] = MinMaxCov(prob, prob)
        EmbedList.append(emb)
    emb = Embed(EmbedList, InvMapping)
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


def get_best_extension(pat, emb, output, db):
    extensions = get_extensions(pat, emb, output, db)
    if not extensions:
        return False, pat, emb, MinMaxCov()
    logger.info("Possible extensions of the pattern are %s " % pp.pformat(extensions.keys()))
    best_ext, best_emb, best_cov = cmp_ext(pat, db, emb, output, extensions)
    logger.info("The best extension is %s " % pp.pformat(best_ext))
    #next_pat, next_emb = extensions.items()[0]
    #return True, next_pat[0], next_emb
    # return an extension only if the minimum change in the coverage is positive
    status = False
    if best_cov.MinCov > 0:
        status = True
    else:
        best_ext = pat
        best_emb = emb
    total_cov = compute_coverage_scores(best_ext, db, best_emb)
    return status, best_ext, best_emb, total_cov


def get_next_pattern(db, output):
    pat, emb = get_single_pattern(db, output)
    logger.info("Iteration starts with single edge pattern %s" % pat.__str__())
    logger.debug(nt_str(emb))
    while True:
        status, next_pat, next_emb, cov = get_best_extension(pat, emb, output, db)
        if status:
            logger.info("Extension of the pattern is %s " % pat.__str__())
            logger.debug(nt_str(emb))
            logger.debug("Total coverage %s" % pp.pformat(cov))
            pat = next_pat
            emb = next_emb
        else:
            logger.info("Pattern cannot be extended anymore")
            break
    logger.info("Pattern constructed in this iteration is %s" % pat.__str__())
    logger.debug(nt_str(emb))
    return pat, emb


def greedy(db, k):
    """
   Returns k patterns that maximizes the value of the objective function
   :param db: networkx graph with probabilities on the edges
   :param k: Number of patterns required
   :return: list of patterns
   """
    output = []
    for i in range(k):
        logger.info("Iteration %d of the greedy algorithm" % i)
        pat, embeddings = get_next_pattern(db, output)
        uniq_embeds = remove_duplicate_embeddings(pat, embeddings)
        pdb.set_trace()
        output.append((pat, embeddings))
    return output
