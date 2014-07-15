import pdb

__author__ = 'Pranay Anchuri'
from miner.preprocess.examples import *
from miner.algos.greedy import greedy
import pickle
import sys

if __name__ == '__main__':
    # gr = triangle()
    #gr = traingle_same_labels()
    gr = pickle.load(open(sys.argv[1]))
    out = greedy(gr, 1)
    pdb.set_trace()
