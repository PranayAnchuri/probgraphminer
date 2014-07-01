import pdb
from miner.misc import get_label

__author__ = 'Pranay Anchuri'

# extend the current pattern with an edge that maximizes the change in the objective function

def one_neighbor(embed, pat, gr):
    """
    get all the one extensions of the embedding in a given graph
    :param pat: pattern that is being extended
    :param embed: Embedding
    :param gr: uncertain graph
    :return: list of list of extended embeddings and the extension of the type
    """
    extensions = set()
    covered_vertices = set()
    induced_embedding = dict(zip(embed.values(), embed.keys()))
    for src, des in pat.edges():
        for v in filter(lambda x: x not in covered_vertices, [src, des]):
            # get the mapping of the vertex in the embedding
            vp = embed[v]
            # explore the neighbors of vp in the uncertain graph
            for nbr in gr.neighbors(vp):
                ext = ()
                if nbr in induced_embedding:
                    # potentially a back edge
                    rev_map = induced_embedding[nbr]
                    if not pat.has_edge(v, rev_map):
                        # a back edge in the pattern
                        ext = (False, frozenset(v, rev_map))
                else:
                    # definitely a forward extension of the
                    ext = (True, v, get_label(gr, nbr))
                if ext:
                    extensions.add(ext)
            covered_vertices.add(v)
    pdb.set_trace()
    return extensions


def extension(pats, embeddings, graph):
    """

    :param pats: list -- list of the patterns that are computed till now -- including the current one
    :param embeddings: list of embeddings, embeddings for each pattern till now in the corresponding components of the graph
    :param graph: graph component in which extension is being performed
    :return: Boolean -- (True, (new values)) if the pattern is extended and (False, 0) otherwise
    """
    curr_pat = pats[-1]
    curr_embed = embeddings[-1]
    # explore the neighborhood of the current embeddings
