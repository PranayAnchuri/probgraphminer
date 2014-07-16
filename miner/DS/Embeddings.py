from collections import namedtuple
import ipdb as pdb
from recordtype import recordtype
import pprint as pp
from collections import defaultdict
from miner.misc import Edge

__author__ = 'Pranay Anchuri'

# This data structure holds the embeddings and the inverse embeddings
# Inverse embeddings : dict; for each edge it stores the indices in the embeddings and the coverage

Embed = namedtuple('Embeddings', ["Mappings", "Inv_Mappings"])

# Coverage
MinMaxCov = recordtype('MinMaxCoverage', [('MinCov', 0), ('MaxCov', 0)])


# Inverse mappings
Ids = 0
Cov = 1


def nt_str(nt):
    """
    Stringify the Embed namedtuple

    :param nt: namedtuple
    :return: string
    """

    def ed_str(ed):
        src, des = list(ed)
        return "(%d, %d)" % (src, des)

    def cov_str(cov):
        return "{ %.2f, %.2f}" % (cov.MinCov, cov.MaxCov)

    st = "Embeddings %s \n" % pp.pformat(nt.Mappings)
    for ed in nt.Inv_Mappings:
        st += "Edge %s : [%s], Cov : [%s] \n" % (
            ed_str(ed), " ".join("%d" % index for index in nt.Inv_Mappings[ed][Ids]), cov_str(nt.Inv_Mappings[ed][Cov]))
    return st


def emb_edges(pat, embedding):
    return frozenset([Edge(embedding[src], embedding[des]) for src, des in pat.edges()])


def emb_hash(edgeset):
    return hash(edgeset)


def ex_cumsum(li):
    s = 0
    ret = []
    for val in li:
        ret.append(s)
        s += val
    return ret


def remove_duplicate_embeddings(pat, emb):
    """
    Remove the embeddings that has the same set of edges (not the same vertex set)
    :param pat: Pattern
    :param emb: namedtuple - Embed
    :return: None

    Compute the edgesets and a hash for each embedding; for the embeddings that have the same hash check completely
    """
    edgesets = [(emb_edges(pat, emb.Mappings[index]), index) for index, item in enumerate(emb.Mappings)]
    hashes = defaultdict(list)
    # add the embeddings to the hash table
    [hashes[emb_hash(edgeset)].append((edgeset, index)) for edgeset, index in edgesets]
    # get the unique ones in slot
    unique_embeddings = []
    for h, edges in hashes.items():
        unique = []
        for edgelist, index in edges:
            for un in unique:
                # check if they are equal
                if un == edgelist:
                    break
            else:
                unique.append(edgeset)
                unique_embeddings.append(index)
    EmbedList = [emb.Mappings[index] for index in unique_embeddings]
    InvMapping = defaultdict(lambda: [[], MinMaxCov()])
    emb_is_unique = [0] * len(emb.Mappings)
    for idx in unique_embeddings:
        emb_is_unique[idx] = 1
    new_index = dict(zip(range(len(emb.Mappings)), ex_cumsum(emb_is_unique)))
    # remove non unique indices
    for ed, inv in emb.Inv_Mappings.items():
        InvMapping[ed][Ids] = [new_index[index] for index in set(inv[Ids]).intersection(unique_embeddings)]
        InvMapping[ed][Cov] = inv[Cov]
    return Embed(EmbedList, InvMapping)
