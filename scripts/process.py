import networkx as nx
from networkx.readwrite import json_graph

import csv
import json


class RaoJGraph:
    def __init__(self, G=None):
        if G is None:
            G = nx.DiGraph()
        self.G = G

    @classmethod
    def from_tsv(cls, passages='passages.tsv', choices='choices.tsv'):
        G = nx.DiGraph()
        RaoJGraph.add_passages_from_tsv(G, passages)
        RaoJGraph.add_choices_from_tsv(G, choices)
        return cls(G)

    @staticmethod
    def add_passages_from_tsv(G, passages_file='passages.tsv'):
        with open(passages_file) as passage:
            reader = csv.DictReader(passage,
                                    quoting=csv.QUOTE_NONE,
                                    delimiter='\t')
            for row in reader:
                passage = row.pop('passage')
                description = row.pop('passage_description')
                pov = row.pop('pov')
                is_ending = row.pop('is_ending') == 'Y'
                tags = row.pop('tags').split(';')
                G.add_node(passage,
                        description=description,
                        pov=pov,
                        is_ending=is_ending,
                        tags=tags)

    @staticmethod
    def add_choices_from_tsv(G, choices_file='choices.tsv'):
        with open(choices_file) as choices:
            reader = csv.DictReader(choices,
                                    quoting=csv.QUOTE_NONE,
                                    delimiter='\t')
            for row in reader:
                from_passage = row.pop('from_passage')
                to_passage = row.pop('to_passage')
                description = row.pop('choice_description')
                bard_choice = row.pop('bard_choice') == 'Y'
                weight = RaoJGraph.diff(from_passage, to_passage)
                has_edge = G.has_edge(from_passage, to_passage)
                if not has_edge or (has_edge and \
                    not G[from_passage][to_passage]['bard_choice']):
                    G.add_edge(from_passage, to_passage,
                                description=description,
                                bard_choice=bard_choice,
                                weight=weight)

    @staticmethod
    def diff(a, b):
        try:
            return abs(int(a) - int(b))
        except:
            return 1

    @staticmethod
    def turned(path):
        total = 0
        for curr, prev in zip(path[1:], path[:-1]):
            total += diff(curr, prev)
        return total

    def add_bard_layout(self, layout, fixed_node=3, start='Cover',
                        end='THE END FOR REAL THIS TIME'):
        e, length = start, 0
        fixed = {e: True}
        x, y = {e: layout.x(length)}, {e: layout.y(length)}
        while e != end:
            for v in self.G[e]:
                if self.G[e][v]['bard_choice']:
                    length = length + 1
                    if not length % fixed_node:
                        fixed[v] = True
                        x[v] = layout.x(length)
                        y[v] = layout.y(length)

                    # set next node in bard path
                    e = v
                    break
            else:
                print("No bard choice found for: {}".format(e))
                break
        nx.set_node_attributes(self.G, 'fixed', fixed)
        nx.set_node_attributes(self.G, 'x', x)
        nx.set_node_attributes(self.G, 'y', y)

    def add_bard_path(self, start='Cover',
                        end='THE END FOR REAL THIS TIME'):
        e, length = start, 0
        path = [e]
        len_result = {e: length}
        path_result = {e: path.copy()}
        while e != end:
            for v in self.G[e]:
                if self.G[e][v]['bard_choice']:
                    length = length + 1
                    path.append(v)
                    len_result[v] = length
                    path_result[v] = path.copy()

                    # set next node in bard path
                    e = v
                    break
            else:
                print("No bard choice found for: {}".format(e))
                break
        nx.set_node_attributes(self.G, 'bard_length', len_result)
        nx.set_node_attributes(self.G, 'bard_path', path_result)

    def add_shortest_path(self, start='Cover'):
        # calculate min_depth from shortest path from 'Cover'
        spl = nx.shortest_path_length(self.G, start)
        nx.set_node_attributes(self.G, 'from_{}_length'.format(start.lower()), spl)

        sp = nx.shortest_path(self.G, start)
        nx.set_node_attributes(self.G, 'from_{}_path'.format(start.lower()), sp)

    def get_laziest_path(self, start='Cover', \
                         end='THE END FOR REAL THIS TIME'):
        # calculated the shortest number of passages
        # turned through from starting passage
        spl = nx.dijkstra_path(self.G, start, end)
        # nx.set_node_attributes(self.G, 'lazy_{}_length'.format(start.lower()), spl)

        sp = nx.dijkstra_path(self.G, 'Cover', end)
        # nx.set_node_attributes(self.G, 'lazy_{}_path'.format(start.lower()), sp)

        return spl, sp

    def export_json(self, json_file='../json/RaoJ.json'):
        self.G.remove_node('THE END')

        d = json_graph.node_link_data(self.G)
        json.dump(d, open(json_file, 'w'))


import math


class ArchSpiralLayout:

    def __init__(self, width, height, a=0, b=7.5, num_spiral=2, elements=40):
        self.width = width
        self.height = height
        self.a = a
        self.b = b / num_spiral
        self.c = 2 * math.pi / (elements / num_spiral)

    def x(self, n):
        return self.b * n * math.cos(self.c * n + self.a) + self.width / 2

    def y(self, n):
        return self.b * n * math.sin(self.c * n + self.a) + self.height / 2

    def xy(self, n):
        return self.x(n), self.y(n)


class CircleLayout:

    PADDING = 150

    def __init__(self, width, height, radius=None, elements=100):
        self.width = width
        self.height = height
        if radius is None:
            radius = (min([width, height]) - CircleLayout.PADDING) / 2
        self.r = radius
        self.c = 2 * math.pi / elements

    def x(self, n):
        return self.r * math.cos(self.c * n) + self.width / 2

    def y(self, n):
        return self.r * math.sin(self.c * n) + self.height / 2

    def xy(self, n):
        return self.x(n), self.y(n)


class LinearLayout:

    PADDING = 50

    def __init__(self, width, height, slope=(1,1), padding=None, elements=100):
        self.width = width
        self.height = height
        self.mx, self.my = slope
        if padding is None:
            padding = LinearLayout.PADDING
        self.b = padding
        self.c = (min([width, height]) - padding * 2) / (elements)

    def x(self, n):
        return self.c * n + self.b

    def y(self, n):
        return self.c * n + self.b

    def xy(self, n):
        return self.x(n), self.y(n)


if __name__ == '__main__':
    raoj = RaoJGraph.from_tsv('passages.tsv', 'choices.tsv')
    # raoj.add_bard_layout(ArchSpiralLayout(750, 750, b=7.5, num_spiral=2, elements=80))
    raoj.add_bard_layout(CircleLayout(750, 750, radius=300, elements=100))
    # raoj.add_bard_layout(LinearLayout(750, 750, padding=50, elements=85))
    raoj.export_json('RaoJ.json')
