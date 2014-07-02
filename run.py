import pdb

__author__ = 'Pranay Anchuri'
from miner.preprocess.examples import triangle
from miner.algos.greedy_extension import *

if __name__ == '__main__':
    gr = triangle()
    pat = triangle()
    pat.remove_edge(1, 3)
    embed = [{1: 1, 2:2, 3:3}]
    ext = extend_embeddings(pat, embed, gr)
    pdb.set_trace()
