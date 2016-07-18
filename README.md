# bubbl2struct

This is a simple Python class that can convert HTML concept maps generated from [bubbl.us](http://bubbl.us) to more structured formats.  At present the class can convert to a JSON object and also an adjacency matrix (Numpy).  In both cases, the meta information such as node names and edge labels are maintained.  The structured concept maps produced are directed graphs which can then be used to perform automatic analysis of the concept maps.

# Example Usage

To use the bubbl2struct class simply give it the path to the saved HTML file then declare what type of structured file you want to produce:

'''python
from bubbl2struct import b2s

converter = b2s(<path-to-html-file>)
json = converter.as_json()
adj, node_labels, edge_labels = converter.as_adj()
'''

