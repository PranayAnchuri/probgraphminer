from collections import defaultdict
from miner.DS.Embeddings import MinMaxCov, Cov, Ids
from miner.algos.objective import obj_value
from miner.misc import Edge

__author__ = 'Pranay Anchuri'

# compare the extensions of pattern in terms of the change in the value of the objective function
# Let P be a pattern and P' be one of its extension
# edges in the uncertain graph can be classified into the following 4 groups :
# 1) Edges that are not covered by both P and P'
# 2) Edges that are only covered by P
# 3) Edges that are covered by both P and P'
# 4) Edges that are only covered by P'
# --> We can safely ignore Group 1 for they don't contribute towards change in objective function
# --> Coverage of group 2 can be subtracted directly
# --> Coverage of group 4 contributes towards inc in objective function
# --> We can further classify the edges that are covered by both P and P'
# --> 3.1 : edges that are mappings of the new edge added to the pattern P to make it P'
# --> 3.2 : edges that are mappings of the existing edges in P
# --> the coverage decreases for 3.2 because of the extra edge and increases for 3.1
# because the subembedding is not present in P


def contains_sublist(lst, sublst):
    n = len(sublst)
    return any((sublst == lst[i:i+n]) for i in xrange(len(lst)-n+1))


def cov_diff_bounds(emb, embprime, emb_new_edge, rem, pat_extended_ids, pat_nextended_ids):
    """
    See the image  https://imgur.com/AqaCw1M for the classification of edges
    :param emb:
    :param embprime:
    :param emb_new_edge:
    :param rem:
    :param pat_extended_ids:
    :param pat_nextended_ids:
    :return:
    """
    pass


def common_edges_cov_difference(ed, pat, emb, patprime, embprime, output):
    """
    See the image  https://imgur.com/AqaCw1M for the classification of edges
    :param ed:
    :param pat:
    :param emb:
    :param patprime:
    :param embprime:
    :param output:
    :return:
    """
    # embeddings that map ed to the last edge added to the pattern
    src, des = list(patprime.last_edge())
    emb_new_edge = filter(
        lambda embindex: Edge(embprime.Mappings[embindex][src], embprime.Mappings[embindex][des]) == ed,
        embprime.Inv_Mappings[Ids])
    rem = list(set(embprime.Inv_Mappings[Ids].difference(set(emb_new_edge))))
    pat_extended_ids = []
    pat_nextended_ids = []
    for index in emb.Inv_Mappings[Ids]:
        # check if this embedding shares a prefix with one of the remaining embeddings of pat prime
        for rem_id in rem:
            if contains_sublist(embprime.Mappings[rem_id], emb.Mappings[index]):
                pat_extended_ids.append(index)
                break
        else:
            pat_nextended_ids.append(index)


def approx1(pat, emb, patprime, embprime, output, db):
    """
    Return MinMax change in the objective function
    :param pat:
    :param emb:
    :param patprime:
    :param embprime:
    :param output:
    :param db:
    :return:
    """
    prev_edges = set(emb.Inv_Mappings.keys())
    next_edges = set(embprime.Inv_Mappings.keys())
    # see above for the desc of the groups
    grp2 = prev_edges.difference(next_edges)
    grp3 = prev_edges.intersection(next_edges)
    grp4 = next_edges.difference(prev_edges)
    change = MinMaxCov()
    for ed in grp2:
        change.MinCov += -1.0 * emb.Inv_Mappings[ed][Cov].MaxCov
        change.MaxCov += -1.0 * emb.Inv_Mappings[ed][Cov].MinCov
    if grp4:
        inc = obj_value(patprime, db, embprime[patprime], grp3)
        change.MinCov += inc.MinCov
        change.MaxCov += inc.MaxCov
    for ed in grp3:
        # edges that are covered by both P and P'
        diff = common_edges_cov_difference(pat, emb, patprime, embprime, output)
        change.MinCov += diff.MinCov
        change.MaxCov += diff.MaxCov
    return change


def cmp_cov_item(item):
    return item[1].MaxCov


def cmp_ext(pat, db, emb, output, extensions):
    """
    Compares and returns the best extension out of all possible extensions.
    It computes min and max coverage for each extension and compares them.
    :param pat:
    :param db:
    :param emb:
    :param output:
    :param extensions:
    :return:
    """
    approx = [approx1]  # functions that approximate the min and max coverage
    rem_pats = set(extensions.keys())
    for mth in approx:
        changes = defaultdict(lambda: MinMaxCov())
        for patprime in rem_pats:
            changes[pat] = mth(pat, emb, patprime, extensions[patprime], output, db)
        # sort the items are remove some of them
        itms = changes.items()
        max_cov_itm = max(itms, key=cmp_cov_item)
        # remove all the patters whose max coverage is less than the min cov of max item
        rem_pats = filter(lambda itm: itm[1].MinCov >= max_cov_itm.MaxCov, itms)
