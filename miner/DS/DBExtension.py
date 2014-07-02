__author__ = 'Pranay Anchuri'

# one neighbor extension of an embedding in the graph
from ..misc import Edge


class DbExt:

    def __init__(self, extclass, src, desOrLabel):
        self.extclass = extclass
        self.src = src
        self.desOrLabel = desOrLabel

    def __eq__(self, other):
        if not self.extclass:
            # back extension is the same if it is between the same vertices in the extension
            return not other.extclass and set([self.src, self.desOrLabel]) == set([other.src, other.desOrLabel])
        else:
            # forward extension is the same if the extension is from the same vertex with the same label
            return other.extclass and self.src == other.src and self.desOrLabel == other.desOrLabel

    def __hash__(self):
        return hash(self.extclass)

    def get_ext_type(self):
        pass

