from miner.misc import NodeLab, Edge

__author__ = 'Pranay Anchuri'

import networkx as nx


class Pattern(nx.Graph):
    def __init__(self, data=None, **attr):
        nx.Graph.__init__(self, data=data, **attr)
        # key is an integer denoting the addition of the edge to the pattern and the value is the edge
        if not data:
            self.time_stamps = {}
        else:
            self.time_stamps = dict(data.time_stamps)

    def __str__(self):
        return "Nodes : %s \n Edges: %s" % (self.nodes(data=True), self.edges(data=True))

    def add_label(self, lab=None):
        """
        Add a forward vertex to the pattern
        :param lab: label
        :return: int id of the new vertex        Graph.__init__(self, data=data,name=name,**attr)

        """
        vid = self.number_of_nodes()
        self.add_node(vid)
        self.node[vid][NodeLab] = lab
        return vid

    def add_edge(self, id1, id2):
        nx.Graph.add_edge(self, id1, id2)
        self.time_stamps[len(self.time_stamps)] = Edge(id1, id2)

    def last_edge(self):
        if self.edges():
            return self.time_stamps[max(self.time_stamps.keys())]
        else:
            raise RuntimeError("Cannot get the last edge added to the pattern; No edges in the pattern")

    def add_single_edge(self, l1, l2):
        """
        Make a single edge  from pair of labels, call this method only on empty graph
        :param l1:
        :param l2:
        :return:
        """
        if not self:
            vid1 = self.add_label(l1)
            vid2 = self.add_label(l2)
            self.add_edge(vid1, vid2)
        else:
            raise RuntimeError("Cannot call add_single_edge method on non emtpy graph")

    def add_fwd_edge(self, id1, lab):
        id2 = self.add_label(lab)
        self.add_edge(id1, id2)

    def add_edge_by_type(self, tp):
        if tp[0]: #forward extension
            self.add_fwd_edge(tp[1], tp[2])
        else: # back extension
            self.add_edge(tp[1], tp[2])
