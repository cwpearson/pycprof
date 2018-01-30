import sys
import json
import dag_utils as du
import networkx as nx
import matplotlib.pyplot as plt
import collections
import random

# dictionary with key = node_id and value is a list of attributes
# like color of node, name of node,etc... figure out how the nodes are being colored

# dict format
# { 'node_id' : {'size': '' , 'type': '', 'color': '', 'device': '', 'name': ''}, ... }

# eg: # { '666805237492983' : {'size': '10' , 'type': 'allocation', 'color': 'red', 'device': '0', 'name': ''}, ... }


# generates a test graph
def test_graph():
    DAG = nx.DiGraph()

    graph_data = [(1, 2, 1), (2, 5, 1), (3, 4, 1), (4, 5, 1), (1, 5, 2)]
    DAG.add_weighted_edges_from(graph_data)

    colors = ['red', 'blue', 'green', 'black', 'yellow', 'white']

    pos = nx.layout.circular_layout(DAG)
    nodes = nx.draw_networkx_nodes(
        DAG, pos, node_color=colors, node_size=500)
    edges = nx.draw_networkx_edges(
        DAG, pos, arrowsize=10, arrowstyle='->', width=1)
    labs = nx.draw_networkx_labels(
        DAG, pos, font_color='white')  # labels=node_labels
    # simulate
    ax = plt.gca()
    ax.set_axis_off()
    plt.savefig("/Users/nishantdash/Desktop/research2/dag_test.png")
    plt.clf()


# inputs: takes a file name
# outputs: returns list of json lines from input file
# side effect: none
def get_data(file, amount):
    if file[-6:] != '.cprof':
        print 'Error! Wrong file type!'
        exit()

    data = []
    x = 0
    num_lines = 100

    if amount == 'less':
        num_lines = 500
    elif amount == 'medium':
        num_lines = 10000
    elif amount == 'large':
        num_lines = 500000
    elif amount == 'full':
        with open(file, 'r') as f:
            for i, line in enumerate(f):
                data.append(line)
        return data

    with open(file, 'r') as f:
        for i, line in enumerate(f):
            if x < num_lines:
                data.append(line)
            elif x >= num_lines:
                break
            x += 1

    return data


# inputs: takes a line of json from data
# outputs: json line
#          node_type
# side effect: none
def get_singular_data(j):
    node_type = None
    temp = None

    if "val" in j:
        temp = j["val"]
        node_type = "val"
    elif "allocation" in j:
        temp = j["allocation"]
        node_type = "allocation"
    elif "api" in j:
        temp = j["api"]
        node_type = "api"

    return temp, node_type


# inputs: takes a line of json from data
# outputs: integer that is the node id
# side effect: none
def get_node_id(temp):
    node_id = ""

    if "id" in temp:
        node_id = int(temp["id"])
    elif "tid" in temp:
        node_id = int(temp["tid"])

    return node_id


# inputs: takes a line of json from data
# outputs: string about color of node
# side effect: none
def get_node_type_color(label):
    color = "blue"
    if label == "val":
        color = "green"
    elif label == "allocation":
        color = "red"

    return color


# inputs: list of json having graph data
# outputs: dictionary of node, attribute
# side effect: none
def extract_data(data):
    main_data = {}
    edges = []
    temp = ''
    api_data = []

    for line in data:
        j = json.loads(line)
        node_type = ""
        node_id = ""

        node_data, node_type = get_singular_data(j)
        if node_type == None:
            continue

        # save lines of data that involve api, will use for later
        if node_type == 'api':
            api_data.append(line)

        # first get node id
        # node id acts as the key to each entry in the main_data dictionary
        node_id = get_node_id(node_data)

        # now time to get values and put them all in a dictionary
        # this values_dictionary acts as the values in the main_data dictionary
        temp_data = {}
        if 'size' in node_data:
            temp_data['size'] = int(node_data['size'])
        else:
            temp_data['size'] = -1

        temp_data['type'] = node_type
        temp_data['color'] = get_node_type_color(node_type)

        if 'size' in node_data:
            temp_data['device'] = int(node_data['size'])
        else:
            temp_data['device'] = -1

        # getting name
        n = ""
        s = ""
        if 'name' in node_data:
            n = node_data['name']
            if 'symbolname' in node_data:
                s = node_data['symbolname']
        n = str(n)
        s = str(s)
        if s == "":
            temp_data['name'] = n
        else:
            temp_data['name'] = s

        # create key value, where key is node id and value is node's attributes
        main_data[node_id] = temp_data

    # return the dictionary but sorted in increasing order of node_id
    # main_data_ordered = collections.OrderedDict(sorted(main_data.items()))
    return main_data, api_data


# inputs: dictionary of node,attribute
# outputs: a list of colors for all nodes in the data
# side effect: none
def get_node_coloring_list(info):
    colors = []
    for k, v in info.items():
        colors.append(v['color'])
    return colors


# inputs: dictionary of node,attribute and list of json lines that include api
# outputs: a list of directed weighted edges of the graph
# side effect: none
def get_edges(info, api_data):

    edges = []

    for line in api_data:
        j = json.loads(line)
        temp = j['api']

        # getting node id first
        node_id = int(temp['id'])

        # getting edges
        list_of_in = []
        list_of_op = []
        if 'inputs' in temp and 'outputs' in temp:
            list_of_in = temp['inputs']
            list_of_op = temp['outputs']

        # print 'inputs ', list_of_in, ' node ', node_id, ' outputs ', list_of_op

        # now extract edges one by one
        # all inputs go into node_id and node_id has edges to all outputs
        for ii in list_of_in:
            n = int(ii)
            u = n
            v = node_id
            w = int(info[n]['size'])
            if w == -1:
                continue
            uv = (u, v, w)
            edges.append(uv)

        for ii in list_of_op:
            u = node_id
            v = int(ii)
            uv = (u, v, 1)
            edges.append(uv)

    return edges


# inputs: list of edges and dictionary of node,attribute
# outputs: list of colors each node in the graph is supposed to have
# side effect: none
def get_colors_from_edge_info(info, edges):
    colors = []
    nodes = {}
    for ii in edges:
        u = ii[0]
        v = ii[1]
        if u not in nodes:
            nodes[u] = info[u]['color']
        if v not in nodes:
            nodes[v] = info[v]['color']

    nodes_ordered = collections.OrderedDict(sorted(nodes.items()))

    for k, v in nodes_ordered.items():
        colors.append(v)

    return colors, nodes


def get_node_positions(nodes, division_factor):
    positions = {}
    total = len(nodes)
    lim = 100
    x_range = [0, lim]
    y_range = [0, lim]
    modulo_factor = total // division_factor

    ii = 0
    # scaling_factor = 0
    offset_factor = -1
    for k, v in nodes.items():
        if ii % modulo_factor == 0:
            offset_factor += lim * 100

        x = offset_factor + random.randint(x_range[0], x_range[-1])
        y = random.randint(y_range[0], y_range[-1])

        positions[k] = [x, y]
        ii += 1

    # print positions
    return positions


# inputs: list of edges and list of color nodes
# outputs: a DAG
# side effect: none
def generate_graph(edges):
    DAG = nx.DiGraph()
    DAG.add_weighted_edges_from(edges)
    return DAG


# inputs: DAG
# outputs: none
# side effect: visualizes the DAG and saves it
def simulate_graph(DAG, colors, pos):
    # pos = nx.layout.random_layout(DAG)
    # pos = dictionary with nodes as keys and positions as values
    nodes = nx.draw_networkx_nodes(
        DAG, pos, node_color=colors, node_size=100)
    edges = nx.draw_networkx_edges(
        DAG, pos, arrowsize=10, arrowstyle='->')
    # labs = nx.draw_networkx_labels(
    # DAG, pos, font_color='white')  # labels=node_labels

    # simulate and save figure
    ax = plt.gca()
    ax.set_axis_off()
    plt.savefig(
        "/Users/nishantdash/Desktop/research2/dag_trace.png", dpi=1000)
    plt.clf()


# inputs: DAG, path
# outputs: none
# side effect: visualizes the DAG with the path highlighted and saves it
def simulate_DAG_with_path(G, path):
    node_colors_dict = {}
    node_colors = []

    for i in G.nodes:
        node_colors_dict[str(i)] = 'blue'
    for i in path:
        node_colors_dict[str(i)] = 'yellow'
    for cur_node in G.nodes:
        node_colors.append(node_colors_dict[str(cur_node)])

    pos = nx.layout.spring_layout(G)
    nodes = nx.draw_networkx_nodes(
        G, pos, node_color=node_colors, node_size=100)
    edges = nx.draw_networkx_edges(
        G, pos, arrowsize=1, arrowstyle='->', width=1)
    # labs = nx.draw_networkx_labels(
    #   G, pos, font_color='white')  # labels=node_labels
    # edge_labs = nx.draw_networkx_edge_labels(G, pos)

    ax = plt.gca()
    ax.set_axis_off()
    plt.savefig(
        "/Users/nishantdash/Desktop/research2/dag_trace_with_longest_path.png")
    plt.clf()


def longest_path_DAG(G, weight='weight', default_weight=1):
    return nx.dag_longest_path(G, weight='weight', default_weight=0)


def find_cycle_DAG(G):
    return nx.find_cycle(G, orientation='original')


# def main_old():
#     file = sys.argv[1]
#     data = get_data(file)

#     nodes, names, edges, de = get_nodes_old(data)
#     # have list of node,node_type and list of names
#     generate_dummy_graph(nodes, de, names)


# inputs: list of edges and list of color nodes
# outputs: none
# side effect: generates a DAG and saves it as a figure
def main():
    file = sys.argv[1]
    data = get_data(file, 'less')

    # first extract data from json
    info, api_data = extract_data(data)

    # get edge from data
    edges = get_edges(info, api_data)
    # get colors for the nodes to be added in the graph
    colors, nodes_to_draw = get_colors_from_edge_info(info, edges)

    # generate a DAG
    G = generate_graph(edges)

    # cycles = find_cycle_DAG(G)
    # print cycles

    # get node positions based on edges
    positions = get_node_positions(nodes_to_draw, 7)

    # simulate DAG
    simulate_graph(G, colors, positions)

    # get longest path in DAG
    longest_path = longest_path_DAG(G)
    # simulate the DAG with it's longest path
    simulate_DAG_with_path(G, longest_path)

# to do
# improve visualizing scheme by building graph left to right using the
# inherent chronological ordering of the data


main()
