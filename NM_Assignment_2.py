######
#####
#   @ author: Balaji Sridhar Subramanian, Dinesh , Lisha
#   Simulating citation network and analyzing the characteristics of graph
#
#
######

import networkx as nx
import random
import json
import logging as log
from networkx.readwrite import json_graph


def load_standford_graph(dataFile):
    log.info("This function is to load the standford graph dataset and analyze it")
    G1 = nx.DiGraph()
    # Read the file and create the nodes
    with open(dataFile) as f:
        lines = f.readlines()

    # Creating the edge
    for line in lines:
        # Split the line and get the nodes
        nodeset = line.split()
        log.debug("%s , %s", nodeset[0], nodeset[1])
        # Verify if the nodes exist in the graph, if not add it
        if not G1.has_node(nodeset[0]):
            G1.add_node(nodeset[0])
        if not G1.has_node(nodeset[1]):
            G1.add_node(nodeset[1])

        # Create the edge from node[0] to node[1]
        G1.add_edge(nodeset[0], nodeset[1])
    log.info("Number of nodes and edges in the graph are : %s , %s", G1.number_of_nodes(), G1.number_of_edges())
    return G1


def get_graph_properties(G):
    # TODO - to verify how SCC an WCC are calculated. At the moment all the nodes are considered as SCC
    # Print the graph properties, to be used for analysis
    log.info("Analyzing the graph : ")
    graph_properties = {}
    graph_scc = nx.number_strongly_connected_components(G)
    '''
        print("Stongly connected components are ")
        for i in nx.strongly_connected_components(G):
            print(i)
    
        print("Weakly connected components are ")
        for i in nx.weakly_connected_components(G):
            print(i)
    '''
    graph_properties["scc"] = graph_scc
    log.debug("Graph SCC is: %s", graph_scc)
    graph_wcc = nx.number_weakly_connected_components(G)
    graph_properties["wcc"] = graph_wcc
    log.debug("Graph WCC is: %s", graph_wcc)
    # print("Value of the graph properties: ", graph_properties)
    return graph_properties


def create_graph_organically(no_of_nodes):
    G2 = nx.DiGraph()
    # Minimum size of the graph should be 10 - an arbitary value
    if no_of_nodes < 10:
        no_of_nodes = 10
    for i in range(1, no_of_nodes):
        node_props = load_node_properties()
        if i < 5:
            G2.add_node(i, node_props)
        else:
            add_nodes_in_timestep(G2, 1)
    log.info("Number of nodes and edges in the graph  --- %s , %s", G2.number_of_nodes(), G2.number_of_edges())

    # Removing self loop in the graph

    log.debug("%s", G2.edges())
    self_loop_list = G2.selfloop_edges()
    log.info("Found %s Number of self loops in Graph", len(self_loop_list))
    for iter in self_loop_list:
        print(iter[0])
        G2.remove_edge(iter[0], iter[0])
    log.debug("Aft: %s ", G2.edges())
    # Writing graph in edgelist format with no node
    nx.write_edgelist(G2, 'test.edgelist', data=False)
    write_graph_in_json(G2)  # To be enabled only for small graph <10000 nodes
    graph_properties = get_graph_properties(G2)
    log.info("Value of the graph properties: %s ", graph_properties)
    return G2


def add_nodes_in_timestep(G, no_of_time_steps):
    node_counter = G.number_of_nodes() + 1
    for i in range(node_counter, node_counter + no_of_time_steps):
        node_props = load_node_properties()
        G.add_node(i, node_props)
        s = i
        add_citations_with_filter(G, s, i)


def write_graph_in_json(G):
    # Writing generated graph to the file in json format
    data = json_graph.node_link_data(G)
    nx.write_edgelist(G, "edgelist_graph")
    f = open('node_link_data.json', 'w')
    # f.write(data)
    json.dump(data, f)


def get_random_nodes(G, no_of_nodes, filter):
    group = 'science'  # setting the default value to be science
    if 'group' in filter.keys():
        group = filter["group"]["value"]
        del filter['group']  # Removing the group filtering key value pair
    random_nodes = []
    filtered_node_set = get_nodes_from_graph(G, 'group', group)
    log.debug(filtered_node_set)
    for key, value in filter.items():
        filtered_node_set = get_nodes_from_nodeset(filtered_node_set, key, value["value"], value["comp"])
        log.debug(filtered_node_set)
    filtered_node_len = len(filtered_node_set)
    if no_of_nodes >= filtered_node_len:
        no_of_nodes = filtered_node_len
    # No select random node from subset of nodes
    if len(filtered_node_set) >= no_of_nodes:
        random_nodes = random.sample(filtered_node_set.keys(), no_of_nodes)
    return random_nodes


def get_nodes_from_graph(G, attr_name, attr_value):
    return dict((n, d) for n, d in G.node.items() if (attr_name in d and d[attr_name] == attr_value))


def get_nodes_from_nodeset(nodeset, attr_name, attr_value, cond="equals"):
    filtered_nodes = {}
    if cond == "less_than":
        filtered_nodes = dict((n, d) for n, d in nodeset.items() if (attr_name in d and d[attr_name] < attr_value))
    elif cond == "greater_than":
        filtered_nodes = dict((n, d) for n, d in nodeset.items() if (attr_name in d and d[attr_name] > attr_value))
    else:
        filtered_nodes = dict((n, d) for n, d in nodeset.items() if (attr_name in d and d[attr_name] == attr_value))

    return filtered_nodes


# Note this method doesnt not guarantee the addition of n edges. Rather it adds a maximum of n edges
def add_citations_with_filter(G2, paper, no_of_nodes):
    log.debug("Adding node %s to the graph", no_of_nodes)

    group_values = ["science", "fictional", "comic"]
    sub_group_values = ["neuro", "physics", "chemistry", "maths"]

    filter = {"group": {"value": random.choice(group_values), "comp": "equals"},
              "subgroup": {"value": random.choice(sub_group_values), "comp": "equals"},
              "probability": {"value": random.uniform(0, 0.5), "comp": "greater_than"}}

    # Limiting the number of edges to x% of the graph
    graph_size = G2.number_of_nodes()
    no_of_nodes = int(graph_size * 0.001)
    no_of_nodes = no_of_nodes + 1  # One or more edges are requested
    log.debug("Max number of edges to be created is : %s ", no_of_nodes)
    k = random.randint(1, no_of_nodes)
    random_nodes = get_random_nodes(G2, k, filter)
    for reference in random_nodes:
        if paper == reference | G2.has_edge(paper, reference) | G2.has_edge(reference, paper):
            log.debug("No edge will be added as they exist between %s and %s ", paper, reference)
        else:
            G2.add_edges_from([(paper, reference)])
            # Now update the meta data of the nodes
            G2.node[paper]['references'] = G2.node[paper]['references'] + 1
            G2.node[reference]['referenced_by'] = G2.node[reference]['referenced_by'] + 1
            if G2.node[reference]['first_cited_time'] == 0:
                G2.node[reference]['first_cited_time'] = paper
        # Making sure the graph is acyclic
        # Removing cyclic edges
        if (G2.has_edge(paper, reference)) and (G2.has_edge(reference, paper)):
            log.debug("%s %s", G2.get_edge_data(paper, reference, 0), G2.get_edge_data(reference, paper, 0))
            log.debug("Edge exist both way between %s and %s ", paper, reference)
            G2.remove_edge(paper, reference)
        # Removing self loops
        if G2.has_edge(paper, paper):
            G2.remove_edge(paper, reference)


def load_node_properties():
    group_values = ["science", "fictional", "comic"]
    sub_group_values = ["neuro", "physics", "chemistry", "maths"]
    references = 0  # number of papers it has cited or number of outbound edges
    referenced_by = 0  # number of papers which has cited this paper or no:of inbound edges
    first_cited_time = 0  # Represent the number of time step at which the first citation happened
    node_props = {"group": random.choice(group_values), "subgroup": random.choice(sub_group_values),
                  "probability": random.uniform(0, 0.5), "references": references, "referenced_by": referenced_by,
                  "first_cited_time": first_cited_time}
    log.debug("Filtering criteria is %s ", node_props)
    return node_props


if __name__ == "__main__":
    log.basicConfig(level=log.INFO)

    G = create_graph_organically(35)
    # Update the timestep parameter to scale the number of nodes to be processed
    add_nodes_in_timestep(G, 10)
    graph_properties = get_graph_properties(G)
    log.info("Value of the home grown graph properties: %s ", graph_properties)

    G1 = load_standford_graph("Cit-HepPh.txt")
    stanford_graph_properties = get_graph_properties(G1)
    log.info("Value of the stanford graph properties: %s ", stanford_graph_properties)

    G2 = nx.gnm_random_graph(100, 250, directed=True)
    gnm_graph_properties = get_graph_properties(G)
    log.info("Value of the GNM  graph properties: %s ", gnm_graph_properties)
