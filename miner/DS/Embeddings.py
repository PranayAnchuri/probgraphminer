from collections import namedtuple
from recordtype import recordtype

__author__ = 'Pranay Anchuri'

# This data structure holds the embeddings and the inverse embeddings
# Inverse embeddings : dict; for each edge it stores the indices in the embeddings and the coverage

Embed = namedtuple('Embeddings', ["Mappings", "Inv_Mappings"])

# Coverage
MinMaxCov = recordtype('MinMaxCoverage', [('MinCov', 0), ('MaxCov', 0)])


# Inverse mappings
Ids = 0
Cov = 1
