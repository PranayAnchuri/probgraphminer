from collections import namedtuple
from recordtype import recordtype
import pprint as pp

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
