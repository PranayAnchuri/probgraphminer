from collections import namedtuple

__author__ = 'Pranay Anchuri'

# This data structure holds the embeddings and the inverse embeddings
# Inverse embeddings : dict; for each edge it stores the indices in the embeddings and the coverage

Embed = namedtuple('Embeddings', ["Mappings", "Inv_Mappings"])

# Inverse mappings
Ids = 0
Cov = 1
