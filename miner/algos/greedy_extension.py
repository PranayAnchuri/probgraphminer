from collections import defaultdict
import pdb
from miner.DS.DBExtension import DbExt
from miner.DS.typedefs import EmbedEdges
from miner.misc import Edge, get_label

__author__ = 'Pranay Anchuri'

# extend the current pattern with an edge that maximizes the change in the objective function


def embedding_neighborhood(pat, embed, graph):
    rev_map = dict(zip(embed.values(), embed.keys()))
    extensions = set()
    for pv, dv in embed.items():
        for nbr in graph.neighbors(dv):
            if nbr not in rev_map:
                # a forward extension
                extensions.add(DbExt(True, pv, nbr))
            else:
                # a back extension
                # make sure that the edge is not present in the embedding already
                rev_v = rev_map[nbr]
                if not pat.has_edge(pv, rev_v):
                    extensions.add(DbExt(False, pv, rev_v))
    return extensions


def extend_embeddings(pat, embeddings, graph):
    embedding_edges = defaultdict(set)
    # what are the mappings for new edge in the extension
    new_mapped_edges = defaultdict(set)
    for embed in embeddings:
        extensions = embedding_neighborhood(pat, embed, graph)
        for ext in extensions:
            new_edge = Edge(embed[ext.src], ext.desOrLabel) if ext.extclass else Edge(embed[ext.src], embed[ext.desOrLabel])
            edges = frozenset([Edge(embed[src], embed[des]) for src, des in pat.edges()] + [new_edge])
            ext_type = (ext.extclass, ext.src, get_label(graph, ext.desOrLabel)) if ext.extclass else (
                ext.extclass, ext.src, ext.desOrLabel)
            embedding_edges[ext_type].add(edges)
            new_mapped_edges[ext_type].add(new_edge)
    return embedding_edges, new_mapped_edges
