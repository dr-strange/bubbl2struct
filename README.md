# bubbl2struct

This is a simple Python class that can convert HTML concept maps generated from [bubbl.us](http://bubbl.us) to more structured formats.  At present the class can convert to a JSON object and also an adjacency matrix (Numpy).  In both cases, the meta information such as node names and edge labels are maintained.  The structured concept maps produced are directed graphs which can then be used to perform automatic analysis of the concept maps.

# Example Usage

To use the bubbl2struct class simply give it the path to the saved HTML file then declare what type of structured file you want to produce:

```python
from bubbl2struct import b2s

converter = b2s(<path-to-html-file>)
json = converter.as_json()
adj, node_labels, edge_labels = converter.as_adj()
```

The bubbl.us diagram that produced the example HTML in the diagrams folder can be found [here](https://bubbl.us/v3/?s=6998381#MzQ5OTI3OS82OTk4MzgxL2EyMWRkNDI4OGI2OTcyZmE5ZDJiN2VlYmQ1ZjcxZTZi?X).

# Motivation

This project was created as a means of producing structured representations of the concept maps produced using bubbl.us.  This then enables concept maps to be analysed for detailed structural information and so opens up bubbl.us to be used as a classroom tool.  Future work will look at incorporating automatic analysis tools to score concept maps without user input.

# Installation

To install bubbl2struct, simply clone the repro to your computer or download the `bubbl2struct.py file`.  Easy!

# License

This code is under the MIT license (see LICENSE for more information).