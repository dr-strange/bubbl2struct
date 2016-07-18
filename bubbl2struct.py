'''
bubbl2struct.py - Class to convert a bubbl.us HTML concept map to more structured representations.

Author: Harry Strange
E-mail: h.strange@ucl.ac.uk
Affiliation: University College London
'''
import json
import numpy as np
import pprint 

from bs4 import BeautifulSoup

class b2s:
    '''Converts a bubbl.us HTML format concept map to other formats.

    This is a simple utility class that converts an HTML file generated from bubbl.us to a 
    more structured format (i.e. adjacency matrix, json).  At the moment, it can convert to a 
    json file or to an adjacency matrix.  In both cases, the meta information related to the 
    concept map is retained (i.e. node and edge labels).

    Example:

        >> from bubbl2struct import b2s
        >> converter = b2s('test.html')
        >> json = converter.as_json()

    Attributes:
        data: The raw data from the bubbl.us HTML file 
        parsed_html: A parsed version of the HTML using BeautifulSoup 
        lut: The mapping look up table to convert the id numberings
    '''
    data = ''
    parsed_html = None
    lut = None

    def __init__(self, file):
        ''' Loads and parses the specified HTML file. 

        The HTML file specified by the only input argument should contain an HTML file downloaded from the
        bubbl.us website.  BeautifulSoup is then used as the main parser for this file. 

        Arguments:
            file: The path to the bubbl.us HTML file containing the concept map to be parsed.
        '''
        with open(file, 'r') as f:
            data = f.read().replace('\n', '')

        # Create the beautiful soup object
        parsed_html = BeautifulSoup(data, 'html.parser')

        self.data = data
        self.parsed_html = parsed_html


    def create_edge(self, connector, node_src, incoming=True):
        ''' Creates and returns an edge from the given information.

            Creates an edge from the information in the given connector and the node_src.  The
            incoming flag indicates whether it is a directional edge or not.

            Arguments:
                connector: The beautiful soup object contianing the edge information.
                node_src: The id of the source node.
                incoming: Flag to indiciate if it is an incoming (directed) edge or not.

            Returns:
                edge: The edge information in dictionary format.
        '''

        node_target = self.lut.get(connector['href'].replace("#", ""))
        description = ''

        title = connector['title']
        text = connector.text

        # Remove non-ascii characters from the text (those pesky arrows)
        title = ''.join([i if ord(i) < 128 else ' ' for i in title]).strip()
        text = ''.join([i if ord(i) < 128 else ' ' for i in text]).strip()

        # This needs a little explaining!  In the html files produced by bubbl.us, all links have a description;
        # however, this does not necessarily match with what is on the diagram.  If the description is the 
        # same as the node name, then we can ignore it, otherwise it is actually the correct description.
        if title != text:
            description = text

        edge = {}

        # Swap source and target nodes depending on whether it is an incoming or outgoing edge
        if incoming:
            edge['from'] = node_target
            edge['to'] = node_src
        else:
            edge['from'] = node_src
            edge['to'] = node_target

        edge['description'] = description

        return edge


    def as_json(self):
        ''' Converts to json format. 

            Converts the concept map to json format.  The json file will contian two arrays, one of nodes
            and one of edges.  The nodes contian an id and a description, the edges contain the start and end
            nodes (from and to) as well as an optional edge description.

            Returns:
                output: The json representation of the concept map represented by this class. 
        '''

        parsed_html = self.parsed_html

        # Find all of the entities (concepts) within this HTML file.  They can be found by searching for any
        # div element that has the class 'bubble root pinned'
        entities = parsed_html.find_all('div', attrs={'class': 'bubble root pinned'})

        node_array = []
        edge_array = []

        # We need to create a lookup table to convert from the ids in the HTML file to a monotonically increasing
        # function of values.  This is because in bubbl.us, if you delete a node that id is not re-used, so we can
        # end up with an array of ids like this: [0, 1, 4, 7, 8].  If we want to use the ids as keys for indexing 
        # then this numbering obviously won't work.  Therefore, we create a lookup table where the key is the id
        # value from bubbl.us and the value is the newly re-ordered ids that we can use for referencing.
        # NOTE: The ids used in the outputs are *not* those used in the bubbl.us HTML file, they are the new 
        #       re-ordered version.
        self.lut = {}

        for (entity, id) in zip(entities, range(0, len(entities))):
            self.lut[entity['id']] = id

        # Loop over the concepts and create a node for the given concept and create edges for hierarchies or
        # links between the concepts.
        for entity in entities:
            node_src = self.lut.get(entity['id'])

            # Create the node for this concept
            node = {}
            node['id'] = node_src
            node['description'] = entity.find('div', attrs={'class': 'bubble-text'}).text.strip()
            node_array.append(node)

            # Examine the incoming and outgoing edges of this concept.  These determine the directionality of any
            # connection to or from this concept.
            connectors_incoming = entity.find('div', attrs={'class': 'lines-incoming'}).find_all('a', attrs={'class': 'line'})
            connectors_outgoing = entity.find('div', attrs={'class': 'lines-outgoing'}).find_all('a', attrs={'class': 'line'})

            # Find incoming (directed) edges
            for connector in connectors_incoming:
                edge_array.append(self.create_edge(connector, node_src, True))

            # Find outgoing edges
            for connector in connectors_outgoing:
                edge_array.append(self.create_edge(connector, node_src, False))

        # Remove any duplicate edges that might have appeared
        edge_array = [dict(tupleized) for tupleized in set(tuple(item.items()) for item in edge_array)]

        # Produce the final output dictionary
        output = {}
        output['nodes'] = node_array
        output['edges'] = edge_array

        # Convert the dictionary to json format
        return json.dumps(output)


    def as_adj(self):
        ''' Return an adjacency matrix representation of the concept map. 

            Returns an adjacency matrix as a numpy array representing the connectivity of the concept map. 
            This adjacency matrix is a directed graph and the node details are returned as a separate 
            list of strings.

            Indexing the adjacency matrix proceeds as follows:

                adj[i, j] -> infers that there is a link from node i to node j.  Note that the reverse is 
                             not necessarily true!

            Returns:
                adj: The adjacency matrix of the concept map as a numpy array.
                node_names: The names of the nodes
                edges_names: A 2-dimensional array of edge descriptions (edge_names[0, 1], gives the edge 
                             description for the edge from node 0 to node 1).
        '''
        rep = json.loads(self.as_json())

        nodes = rep['nodes']
        edges = rep['edges']

        # Create an empty array of strings, this makes indexing the correct nodes/edges far easier
        node_names = [''  for x in xrange(len(nodes))]

        # Add the node names
        for node in nodes:
            node_names[node['id']] = node['description']

        adj = np.zeros((len(nodes), len(nodes)))

        # Initialise the edge descriptions array
        edge_names = np.zeros((len(nodes), len(nodes)), dtype = object)

        # Construct the edge information
        for edge in edges:
            adj[edge['from'], edge['to']] = 1

            edge_names[edge['from'], edge['to']] = edge['description']

        return adj, node_names, edges