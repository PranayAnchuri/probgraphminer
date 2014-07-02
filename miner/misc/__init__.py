__author__ = 'Pranay Anchuri'

# constants that are used throughout the program
EdgePr = "Edge Probability"
NodeLab = "Node Label"

get_label = lambda x, y: x.node[y][NodeLab]
get_prob = lambda gr, src, des: gr.edge[src][des][EdgePr]
Edge = lambda x, y: frozenset([x, y])
