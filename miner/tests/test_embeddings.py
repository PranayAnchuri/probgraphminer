from miner.misc import get_label, is_edge
import ipdb as pdb

__author__ = 'Pranay Anchuri'

# tests about the embeddings of a pattern


def test_isomorphism(pat, db, vmappings):
    """
    Return true if the isomorphism that maps pattern vertices to vmappings is a valid isomorphism of the pattern
    :param pat:
    :param db:
    :param vmappings:
    :return:
    """
    injective = len(pat) == len(set(vmappings))
    lab = all(get_label(pat, nd) == get_label(db, vmappings[nd]) for nd in pat.nodes())
    adj = all(is_edge(db, vmappings[src], vmappings[des]) for src, des in pat.edges())
    return injective and lab and adj


def test_valid_embeddings(pat, db, emb):
    """
    Return true if and only all the embeddings induce a valid isomorphism of the pattern in the database
    :param pat: Pattern
    :param emb: Embed - namedtuple that contains the mappings and inverse mappings of the pattern
    :return:
    """
    return all(test_isomorphism(pat, db, vmappings) for vmappings in emb.Mappings)