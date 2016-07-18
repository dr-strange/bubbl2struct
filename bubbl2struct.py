import json
import pprint
import numpy as np

from bs4 import BeautifulSoup

class b2s:
    '''
        b2s
        ---
        This is a simple utility class that converts an HTML file generated from bubbl.us to a 
        more structured format (i.e. adjacency matrix, json).

        Example:

            >> from bubbl2struct import b2s
            >> converter = b2s('test.html')
            >> json = converter.as_json()

    '''
    data = ''
    parsed_html = None

    def __init__(self, file):
        '''
            Starts
        '''
        with open(file, 'r') as f:
            data = f.read().replace('\n', '')

        # Create the beautiful soup object
        parsed_html = BeautifulSoup(data, 'html.parser')

        self.data = data
        self.parsed_html = parsed_html

    def create_edge(self, connector, node_src, incoming=True):
        '''
            Creates an edge from the information in the given connector and the node_src.  The
            incoming flag indicates whether it is a directional edge or not.

        '''
        node_target = int(connector['href'].replace("#", ""))
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

        if incoming:
            edge['from'] = node_target
            edge['to'] = node_src
        else:
            edge['from'] = node_src
            edge['to'] = node_target

        edge['description'] = description

        return edge

    def as_json(self):
        '''
            Converts the concept map to json format.  The json file will contian two arrays, one of nodes
            and one of edges.  The nodes contian an id and a description, the edges contain the start and end
            nodes (from and to) as well as an optional edge description.

        '''
        parsed_html = self.parsed_html

        entities = parsed_html.find_all('div', attrs={'class': 'bubble root pinned'})

        node_array = []
        edge_array = []

        for entity in entities:
            node_src = int(entity['id'])

            node = {}
            node['id'] = node_src
            node['description'] = entity.find('div', attrs={'class': 'bubble-text'}).text.strip()
            node_array.append(node)

            connectors_incoming = entity.find('div', attrs={'class': 'lines-incoming'}).find_all('a', attrs={'class': 'line'})
            connectors_outgoing = entity.find('div', attrs={'class': 'lines-outgoing'}).find_all('a', attrs={'class': 'line'})

            for connector in connectors_incoming:
                edge_array.append(self.create_edge(connector, node_src, True))

            for connector in connectors_outgoing:
                edge_array.append(self.create_edge(connector, node_src, False))

        pprint.pprint(edge_array)

        # Remove any duplicate edges that might have appeared
        edge_array = [dict(tupleized) for tupleized in set(tuple(item.items()) for item in edge_array)]

        output = {}
        output['nodes'] = node_array
        output['edges'] = edge_array

        return json.dumps(output)

    def as_adj(self):
        '''
            Returns an adjacency matrix as a numpy array representing the connectivity of the concept map. 
            This adjacency matrix is a directed graph and the node details are returned as a separate 
            list of strings.

            Indexing the adjacency matrix proceeds as follows:

                adj[i, j] -> infers that there is a link from node i to node j.  Note that the reverse is 
                             not necessarily true!
        '''
        rep = json.loads(self.as_json())

        nodes = rep['nodes']
        edges = rep['edges']

        # Create an empty array of strings, this makes indexing the correct nodes far easier
        node_names = [''  for x in xrange(len(nodes))]

        for node in nodes:
            node_names[node['id'] - 1] = node['description']

        adj = np.zeros((len(nodes), len(nodes)))

        for edge in edges:
            adj[edge['from']-1, edge['to']-1] = 1

        return adj, node_names