import pdb

__author__ = 'Pranay Anchuri'
from miner.preprocess.examples import *
from miner.algos.greedy import greedy

if __name__ == '__main__':
    # gr = triangle()
    gr = traingle_same_labels()
    greedy(gr, 1)
    pdb.set_trace()
