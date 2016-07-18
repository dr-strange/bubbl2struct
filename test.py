from pprint import pprint
from bubbl2struct import b2s

# Load the simple diagram from the diagras folder
converter = b2s('diagrams/simple_diagram.html')

# Load as JSON
json = converter.as_json()

print 'Converted to json format: '

pprint(json)

# Load as adjacency
adj, nodes, edges = converter.as_adj()

print 'Converted to adjacency matrix: '

pprint(str(adj))

print 'Node information: '

for (node, id) in zip(nodes, range(0, len(nodes))):
    print str(id) + ': ' + node

print 'Edge information: '

pprint(edges)


print str(adj.shape)