import networkx as nx
import random
import matplotlib.pyplot as plt

################################################################################
#                             Algorithm methods
################################################################################

def topological_sort(DAG):
    return list(nx.topological_sort(DAG))

def longest_path_DAG(G, weight='weight', default_weight=1):
    return nx.dag_longest_path(G, weight='weight', default_weight=0)

def longest_path_length_DAG(DAG):
    return nx.dag_longest_path_length(DAG)

def longest_path_min_weight_DAG(DAG, edge_widths, weights, sources):
    global_w = 1000000000
    n,e = genrate_DAG_info(DAG)
    ret = []

    for i in sources:
        root = i
        dist = bfs(root, e)
        paths = get_longest_paths(root, e, dist)
        final_path, final_w = get_lightest_path_and_weight(DAG, root, paths, weights)

        if final_w < global_w:
            global_w = final_w
            ret = final_path

    return ret

def dfs(root, edges, level, distance, paths):
    if root == None:
        return
    if level == distance:
        paths.append(root)
        return True

    to_go = edges[root] # we get a list of neighbors to visit
    # recursively visit each neighbor
    flag = False
    for ii in to_go:
        if dfs(ii, edges, level+1, distance, paths) == True:
            paths.append(root)
            flag = True

    return flag

def bfs(root, edges):
    # we have a dictionary of edges
    # now time to perform BFS starting from root and visiting each edge

    # start with root node
    queue = []
    queue.append(root)
    level = 0
    ctr = 1
    while len(queue) != 0:
        cur_nodes = []
        for ii in range(ctr):
            cur_nodes.append(queue.pop(0))

        ctr = 0
        for cur_node in cur_nodes:
            for node in edges[cur_node]:
                queue.append(node)            # enqueue all neighbors
                ctr += 1

        level += 1

    #print edges
    return level-1

def get_longest_paths(root, edges, distance):
    temp = []
    paths = []
    dfs(root, edges, 0, distance, temp)
    temp.reverse()
    offset = 0
    for ii in range(len(temp)):
        if temp[ii] == root:
            paths.append(temp[offset:ii])
            offset += ii
    paths.append(temp[offset:])

    return paths[1:]

def get_lightest_path_and_weight(DAG, root, paths, weights):
    total_weight = 10000000000
    final_idx = 0

    for ii in range(len(paths)):
        path = paths[ii]
        # path holds the path for consideration
        # so now we need to extract edges from the path
        edges = []
        for x in range(0, len(path)-1):
            tup =(path[x], path[x+1])
            edges.append(tup)

        # now calculate total weight of path, i.e sum of all edge weights
        temp = 0
        for edge in edges:
            #get weight of edges
            temp += weights[edge]

        # compare current calculated wight with global one
        if temp < total_weight:
            total_weight = temp
            final_idx = ii      # save index

    return paths[final_idx], total_weight


################################################################################
#                             Generation methods
################################################################################

def generate_small_DAG():
    # DAG = nx.gn_graph(10)  # the GN graph
    DAG = nx.DiGraph()
    DAG_alt = nx.DiGraph()

    f = open('sample_graph.txt', 'r')
    data = f.read()
    f.close()

    graph_data = []
    graph_data_alt = []
    weights = {}
    edge_widths = []

    for i in range(len(data)//6):
        x = 6*i
        u = int(data[x])
        v = int(data[x+2])
        w = int(data[x+4])

        tup1 = (u,v,w)
        tup1_alt = (u,v,1)
        tup2 = (u,v)

        graph_data.append(tup1)
        graph_data_alt.append(tup1_alt)
        weights[tup2] = w
        edge_widths.append(w)

    DAG.add_weighted_edges_from(graph_data)
    DAG_alt.add_weighted_edges_from(graph_data_alt)

    sources = []
    for node in DAG.nodes():
        if DAG.in_degree(node) == 0:
            sources.append(node)

    return DAG, DAG_alt, edge_widths, weights, sources

def genrate_DAG_info(DAG):
    nodes = DAG.nodes()
    edges_temp = DAG.edges()
    edges = {}

    for u in nodes:
        edges[u] = []
    for u,v in edges_temp:
        edges[u] += [v]

    return nodes, edges

################################################################################
#                             Simulation methods
################################################################################

# Draws a directed acyclic graph
def simulate_DAG(G, edge_widths):
    pos = nx.layout.spring_layout(G)
    nodes = nx.draw_networkx_nodes(G, pos, node_color='blue', node_size=500)
    edges = nx.draw_networkx_edges(
        G, pos, arrowsize=1, arrowstyle='->', width=edge_widths)
    labs = nx.draw_networkx_labels(
        G, pos, font_color='white')  # labels=node_labels
    #edge_labs = nx.draw_networkx_edge_labels(G, pos)

    ax = plt.gca()
    ax.set_axis_off()
    plt.savefig("/Users/nishantdash/Desktop/research2/dag.png")
    plt.clf()

# Draws a directed acyclic graph with a given path highlighted a different color
def simulate_DAG_with_path(G, path, edge_widths):
    node_colors_dict = {}
    node_colors = []

    for i in G.nodes:
        node_colors_dict[str(i)] = 'blue'
    for i in path:
        node_colors_dict[str(i)] = 'red'
    for cur_node in G.nodes:
        node_colors.append(node_colors_dict[str(cur_node)])

    pos = nx.layout.spring_layout(G)
    nodes = nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=500)
    edges = nx.draw_networkx_edges(
        G, pos, arrowsize=1, arrowstyle='->', width=edge_widths)
    labs = nx.draw_networkx_labels(
        G, pos, font_color='white')  # labels=node_labels
    #edge_labs = nx.draw_networkx_edge_labels(G, pos)

    ax = plt.gca()
    ax.set_axis_off()
    plt.savefig("/Users/nishantdash/Desktop/research2/dag_with_longest_path.png")
    plt.clf()

################################################################################
#                               Sample run
################################################################################
# sample analysis
def sample():
    DAG, DAG2, e_w, w, sources = generate_small_DAG()
    ts_DAG = topological_sort(DAG)

    simulate_DAG(DAG, e_w)

    ts_DAG2 = topological_sort(DAG2)

    path = longest_path_min_weight_DAG(DAG2, e_w, w, sources)
    #path = longest_path_DAG(DAG, weight='weight', default_weight=1)
    simulate_DAG_with_path(DAG, path, e_w)


#sample()
