import networkx as nx
import csv

DEFAULT_PASSAGES_FILE = 'passages.tsv'
DEFAULT_CHOICES_FILE = 'choices.tsv'

G = nx.DiGraph()

with open('passages.tsv') as passage:
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

with open('choices.tsv') as choices:
    reader = csv.DictReader(choices,
                            quoting=csv.QUOTE_NONE,
                            delimiter='\t')
    for row in reader:
        from_passage = row.pop('from_passage')
        to_passage = row.pop('to_passage')
        description = row.pop('choice_description')
        bard_choice = row.pop('bard_choice') == 'Y'
        try:
            weight = abs(int(from_passage) - int(to_passage))
        except:
            weight = 1
        has_edge = G.has_edge(from_passage, to_passage)
        print(from_passage, ',', to_passage, ':', has_edge)
        if not has_edge or (has_edge and \
            not G[from_passage][to_passage]['bard_choice']):
            G.add_edge(from_passage, to_passage,
                        description=description,
                        bard_choice=bard_choice,
                        weight=weight)

import math

width, height = 750, 750

# def layout_x(n):
#     a = 0
#     b = 7.5 / 2
#     c = 2 * math.pi / 40
#     return b * n * math.cos(c * n + a) + width / 2

# def layout_y(n):
#     a = 0
#     b = 7.5 / 2
#     c = 2 * math.pi / 40
#     return b * n * math.sin(c * n + a) + height / 2

def layout_x(n):
    r = 300
    c = 2 * math.pi / 100
    return r * math.cos(c * n) + width / 2

def layout_y(n):
    r = 300
    c = 2 * math.pi / 100
    return r * math.sin(c * n) + height / 2

# calculate bard_depth from number of choices from 'Cover'
# bard depth would be used to fix the bard passagesx
e, end = 'Cover', 'THE END FOR REAL THIS TIME'
path, length = [e], 0
fixed = {e: True}
x, y = {e: layout_x(length)}, {e: layout_y(length)}
len_result = {e: length}
path_result = {e: path.copy()}
while e != end:
    print("Current node: {}".format(e))
    for v in G[e]:
        if G[e][v]['bard_choice']:
            print("Bard choice: {}".format(v))
            length = length + 1
            path.append(v)
            len_result[v] = length
            path_result[v] = path.copy()
            if not length % 3:
                fixed[v] = True
            x[v] = layout_x(length)
            y[v] = layout_y(length)

            e = v
            break
    else:
        print("No bard choice found for: {}".format(e))
        break
nx.set_node_attributes(G, 'fixed', fixed)
nx.set_node_attributes(G, 'x', x)
nx.set_node_attributes(G, 'y', y)

nx.set_node_attributes(G, 'bard_length', len_result)
# nx.set_node_attributes(G, 'bard_path', path_result)


# calculate min_depth from shortest path from 'Cover'
# spl = nx.shortest_path_length(G, 'Cover')
# nx.set_node_attributes(G, 'from_cover_length', spl)

# sp = nx.shortest_path(G, 'Cover')
# nx.set_node_attributes(G, 'from_cover_path', sp)


G.remove_node('THE END')

import json
from networkx.readwrite import json_graph

d = json_graph.node_link_data(G)
json.dump(d, open('RaoJ.json', 'w'))
