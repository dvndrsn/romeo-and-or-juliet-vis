import networkx as nx
import csv

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
        G.add_edge(from_passage, to_passage,
                   description=description,
                   bard_choice=bard_choice)

G.remove_node('THE END')

import json
from networkx.readwrite import json_graph

d = json_graph.node_link_data(G)
json.dump(d, open('RaoJ.json', 'w'))
