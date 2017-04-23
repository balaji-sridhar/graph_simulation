######
#####
#   @ author: Balaji Subramanian (16203531), Dinesh Kumar (16200107), Lisha Ghosh (16204693)
#   Simulating citation network and analyzing simulation properties
#
#
######

import networkx as nx
import os
import random
import json
import csv
import logging as log
from networkx.readwrite import json_graph
import itertools


def get_graph_properties(G):
    '''
        Compute the graph properties and return dictionary
        :param G:  Graph for which the properties needs to be assessed
        :return: returns a graph properties dictionary
    '''
    # Print the graph properties, to be used for analysis
    log.info("Analyzing the graph : ")
    graph_properties = {}
    graph_scc = nx.number_strongly_connected_components(G)
    graph_properties["scc"] = graph_scc
    log.debug("Graph SCC is: %s", graph_scc)
    graph_wcc = nx.number_weakly_connected_components(G)
    graph_properties["wcc"] = graph_wcc
    log.debug("Graph WCC is: %s", graph_wcc)
    node_count = G.nodes()
    graph_properties["node_count"] = node_count
    log.debug("Graph WCC is: %s", node_count)
    edge_count = G.edges()
    graph_properties["edge_count"] = edge_count
    log.debug("Graph WCC is: %s", edge_count)

    return graph_properties


def load_node_properties():
    '''
    This function returns randomly choses the meta data properties, to be used during node creation
    :return: dictionary of node randomly generated meta data
    '''

    group_values = ["science", "fictional", "comic"]
    sub_group_values = ["neuro", "physics", "chemistry", "maths"]
    popularity_level = ["new", "moderate", "famous", "influential"]
    references = 0  # number of papers it has cited or number of outbound edges
    cited_by = 0  # number of papers which has cited this paper or no:of inbound edges
    first_cited_time = 0  # Represent the number of time step at which the first citation happened
    node_props = {"group": random.choice(group_values), "subgroup": random.choice(sub_group_values),
                  "probability": random.uniform(0, 0.5), "references": references, "cited_by": cited_by,
                  "first_cited_time": first_cited_time, "popularity_level": popularity_level[0]}
    log.debug("Filtering criteria is %s ", node_props)
    return node_props


def get_nodes_from_graph(G, attr_name, attr_value):
    '''
        Wrapper function to return the list of matching nodes based on fitering criteriaa
    :param G: Graph on which the filtering needs to be applied
    :param attr_name: Name of the attribute to be filtered
    :param attr_value: value of the attribute to be matched
    :return: list of matching nodes
    '''
    return dict((n, d) for n, d in G.node.items() if (attr_name in d and d[attr_name] == attr_value))


def get_nodes_from_nodeset(nodeset, attr_name, attr_value, cond="equals"):
    '''
        Applies filtering on attributes in the nodeset. TO be used for multiple filtering on nodesets repeatedly
    :param nodeset: nodeset on which the filtering needs to be applied
    :param attr_name: Name of the attribute to be filtered
    :param attr_value: value of the attribute to be matched
    :param cond: define the comparison criteria say less than, greater than or equal
    :return: list of matching nodes
    
    '''
    filtered_nodes = {}
    if cond == "less_than":
        filtered_nodes = dict((n, d) for n, d in nodeset.items() if (attr_name in d and d[attr_name] < attr_value))
    elif cond == "greater_than":
        filtered_nodes = dict((n, d) for n, d in nodeset.items() if (attr_name in d and d[attr_name] > attr_value))
    else:
        filtered_nodes = dict((n, d) for n, d in nodeset.items() if (attr_name in d and d[attr_name] == attr_value))

    return filtered_nodes


def get_random_nodes(G, no_of_nodes, filter):
    '''
    Picks requested number of nodes randomly from the graph based on tge filtering criteria
    :param G: Graph from which nodes have to be chosen
    :param no_of_nodes: number of nodes to be returned
    :param filter: seed for seleccting the nodes from the graph
    :return: returns the list of nodes
    '''
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


# Note this method doesnt not guarantee the addition of n edges. Rather it adds a maximum of n edges
def add_citations_with_filter(G2, paper, no_of_edges):
    '''
    Add random edges based on the cusotom built seeding logic and adds a maximum of :no_of_edges originating from :paper node
    :param G2: Graph on which the edges are added
    :param paper: Node from which the edges originates
    :param no_of_edges:  Max number of edges to be added from the node
    
    '''
    log.debug("Adding node %s to the graph", no_of_edges)

    group_values = ["science", "fictional", "comic"]
    sub_group_values = ["neuro", "physics", "chemistry", "maths"]

    filter = {"group": {"value": random.choice(group_values), "comp": "equals"},
              "subgroup": {"value": random.choice(sub_group_values), "comp": "equals"},
              "probability": {"value": random.uniform(0, 0.5), "comp": "greater_than"}}

    # Limiting the number of edges to x% of the graph
    graph_size = G2.number_of_nodes()
    no_of_edges = int(graph_size * 0.001)
    no_of_edges = no_of_edges + 1  # One or more edges are requested
    log.debug("Max number of edges to be created is : %s ", no_of_edges)
    k = random.randint(1, no_of_edges)
    random_nodes = get_random_nodes(G2, k, filter)
    for reference in random_nodes:
        if paper == reference or G2.has_edge(paper, reference) or G2.has_edge(reference, paper):
            log.debug("No edge will be added as they exist between %s and %s ", paper, reference)
        else:
            G2.add_edges_from([(paper, reference)])
            # Now update the meta data of the nodes
            G2.node[paper]['references'] = G2.node[paper]['references'] + 1
            G2.node[reference]['cited_by'] = G2.node[reference]['cited_by'] + 1
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


def initialize_csv_file(output_file_name):
    '''
    Initialize the csv file with output headers, to track the metrics
    :param output_file_name: Name of the metrics file to which the data has to be written
    :return: Nothing
    '''
    # Create the file if exist, else clear down
    output_file = open(output_file_name, 'w+', newline='')
    writer = csv.writer(output_file)
    # Writing header to the csv file
    writer.writerow(['total_no_of_nodes', 'nodes_in_new_state', 'nodes_in_moderate_state', 'nodes_in_famous_state',
                     'nodes_in_influential_state'])


def study_simulation_properties(G, time_steps, no_of_cycles, metrics_filename):
    '''
    Runs simulation metrics for :no_of_cycle and writes the metrics after each :time_step to a csv file. 
    This helps to track how the graph properties affect the simulation properties
    :param G: Graph on which the simulation needs to be carried out 
    :param time_steps: number of nodes to be added per atomic unit of computation, number of nodes to be added
    :param no_of_cycles: number of cycles or number of atomic unit operations to be repeated 
    :param metrics_filename: name of metric file to which analysis report needs to be written to
    :return: Nothing
    '''
    if time_steps < 50:
        time_steps = 50
    for i in range(0, no_of_cycles):
        # Atomic unit of analysis, adds 50 nodes to the graph and recomputes the metrics
        add_nodes_in_timestep(G, time_steps, 1, 1, metrics_filename)


def print_simulation_metrics(G, filename):
    '''
    Helper function to print the metrics to the csv files
    :param G: Graph for which metrics to be printed
    :param filename: file name to which the metrics to be printed to 
    :return: 
    '''
    # Print the simulation properties to csv file
    # no:of nodes in graph, no:of nodes in new state, no:of nodes in moderate state, no:of nodes in famouos state , no:of nodes in influential state
    total_no_of_nodes = G.number_of_nodes()
    nodes_in_new_state = len(get_nodes_from_graph(G, 'popularity_level', 'new'))
    nodes_in_moderate_state = len(get_nodes_from_graph(G, 'popularity_level', 'moderate'))
    nodes_in_famous_state = len(get_nodes_from_graph(G, 'popularity_level', 'famous'))
    nodes_in_influential_state = len(get_nodes_from_graph(G, 'popularity_level', 'influential'))
    if filename != "":
        # Assume the file exist
        output_file = open(filename, 'a', newline='')
        writer = csv.writer(output_file)
        writer.writerow([total_no_of_nodes, nodes_in_new_state, nodes_in_moderate_state, nodes_in_famous_state,
                         nodes_in_influential_state])
        output_file.close()


def add_nodes_in_timestep(G, no_of_time_steps, with_edges, with_metrics, filename=""):
    '''
    
    :param G: Graph to which the nodes needs to added 
    :param no_of_time_steps: Number of nodes to be added to the graph
    :param with_edges: determines whether to add only the nodes or add random edges for the nodes. 1 implies enabled, else disabled.
    :param with_metrics: determines whether metrics needs to be computed at the end of the node addition. 1 implies enabled, else disabled. 
    :param filename: Name of the filename to which the metrics to be written
    :return: 
    '''
    if G.number_of_nodes() > 0:
        node_counter = G.number_of_nodes() + 1
    else:
        node_counter = 0
    for i in range(node_counter, node_counter + no_of_time_steps):
        node_props = load_node_properties()
        G.add_node(i, node_props)
        s = i
        if with_edges == 1:
            add_citations_with_filter(G, s, i)

    if with_metrics == 1:
        # Iterate over all the nodes and update the node state
        indegree_centralities = nx.in_degree_centrality(G)
        # Normalizing the distribution
        max_indegree_centrality = max([i for i in indegree_centralities.values()])
        log.debug("Maximum value of indegree centrality : %s", max_indegree_centrality)

        for n, c in indegree_centralities.items():
            normalized_node_centrality = c / max_indegree_centrality
            log.debug("Actual centrality is %s Normalized centrality is %s", c, normalized_node_centrality)
            # Check the centrality range and update the popularity state
            if normalized_node_centrality > 0 and normalized_node_centrality <= 0.15:
                G.node[n]["popularity_level"] = "moderate"
            elif normalized_node_centrality > 0.15 and normalized_node_centrality <= 0.30:
                G.node[n]["popularity_level"] = "famous"
            elif normalized_node_centrality > 0.30:
                G.node[n]["popularity_level"] = "influential"
        print_simulation_metrics(G, filename)


def write_graph_in_json(G, filename):
    '''
    Helper function to write graph in node_link format. AKA in json format
    :param G: Graph which needs to written to the file
    :param filename: name of the file graph needs to written to
    :return: 
    '''
    # Writing generated graph to the file in json format
    data = json_graph.node_link_data(G)
    # nx.write_edgelist(G, "edgelist_graph")
    f = open(filename, 'w+')
    # f.write(data)
    json.dump(data, f)


def create_graph_organically(no_of_nodes):
    '''
    Creates graph organically, where nodes and edges are added to empty graph. Nodes are created with meta data inducted 
    to it and values are chosen randomly from pre-defined data set.
    Addition of the edges to the nodes are based custom build function where graph meta data is taken into consideration.
    :param no_of_nodes: Number of nodes to be added.
    :return: Returns an graph object
    '''
    G2 = nx.DiGraph()
    # Minimum size of the graph should be 10 - an arbitary value
    if no_of_nodes < 10:
        no_of_nodes = 10
    for i in range(1, no_of_nodes):
        node_props = load_node_properties()
        if i < 5:
            G2.add_node(i, node_props)
        else:
            add_nodes_in_timestep(G2, 1, 1, 0)
    log.info("Number of nodes and edges in the home brewed graph are :%s , %s", G2.number_of_nodes(),
             G2.number_of_edges())

    # Removing self loop in the graph

    log.debug("%s", G2.edges())
    self_loop_list = G2.selfloop_edges()
    log.info("Found %s Number of self loops in Graph", len(self_loop_list))
    for iter in self_loop_list:
        print(iter[0])
        G2.remove_edge(iter[0], iter[0])
    log.debug("Aft: %s ", G2.edges())
    if G2.number_of_nodes() < 1000:
        write_graph_in_json(G2, 'node_link_data.json')
    return G2


def load_standford_graph(dataFile):
    '''
    This function loads the edge list connectivity from the stanford dataset. File is read line by line, each line
    represent the edges(from and to nodes). If the nodes doesnt exist in the graph, they are added and edges are created
    If not just edges are created.
    https://snap.stanford.edu/data/cit-HepPh.html
    :param dataFile: Name of the stanford data file to be loaded
    :return: Returns the graph object
    '''
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
            node_props = load_node_properties()
            G1.add_node(nodeset[0], node_props)

        if not G1.has_node(nodeset[1]):
            node_props = load_node_properties()
            G1.add_node(nodeset[1], node_props)

        # Create the edge from node[0] to node[1]
        G1.add_edge(nodeset[0], nodeset[1])
        # Updating the node properties
        G1.node[nodeset[0]]['references'] = G1.node[nodeset[0]]['references'] + 1
        G1.node[nodeset[1]]['cited_by'] = G1.node[nodeset[1]]['cited_by'] + 1

    log.info("Number of nodes and edges in stanford graph are : %s , %s", G1.number_of_nodes(), G1.number_of_edges())
    # To restrict the performance impact in writing huge file to disk
    if G1.number_of_nodes() < 1000:
        write_graph_in_json(G1, 'stanford_dataset.json')
    return G1


def generate_erdos_renyi_graph(n, p, seed=None):
    """
        This function generates graph of node n with random number of edges, with probability p

        NOTE:This function implementation is inspired from networkx implementaiton nx.gnp_random_graph()and being modified 
        to cater the needs of this simulation. We are overriding the function, so meta data can be updated.

    """
    G = nx.DiGraph()
    # Replace this function with node addition
    add_nodes_in_timestep(G, n, 0, 0)

    G.name = "gnp_random_graph(%s,%s)" % (n, p)

    if p <= 0:
        return G

    if not seed is None:
        random.seed(seed)

    if G.is_directed():
        edges = itertools.permutations(range(n), 2)
    else:
        edges = itertools.combinations(range(n), 2)

    if p >= 1:
        G.add_edges_from(edges)
        return G

    for e in edges:
        if random.random() < p:
            # print(e[0],e[1], e)
            # Updating the meta data, to keep count of number of in bound and outbound edges
            add_citations_with_filter(G, e[0], e[1])
    if G.number_of_nodes() < 1000:
        write_graph_in_json(G, 'erdos_renyi.json')
    log.info("Number of nodes and edges in the  erdos renyi graph are :%s , %s", G.number_of_nodes(),
             G.number_of_edges())

    return G


if __name__ == "__main__":
    # Setting the default log level to INFO
    log.basicConfig(level=log.INFO)

    # Brewing the graph with 35000 edges
    # using custom logic for edges addition and analyzing the simulation properties
    G = create_graph_organically(35000)
    graph_properties = get_graph_properties(G)
    brewed_graph_metrics_file = 'brewed_sim_metrics.csv'
    initialize_csv_file(brewed_graph_metrics_file)
    study_simulation_properties(G, 50, 30, brewed_graph_metrics_file)

    # To be used if a subset of stanford dataset to be used
    # stanford_data_set = "test.edgelist"
    stanford_data_set = "Cit-HepPh.txt"

    # Loading the real time data set and
    # analyzing the simulation properties
    stanford_metrics_file = 'stanford_sim_metrics.csv'
    G1 = load_standford_graph(stanford_data_set)
    stanford_graph_properties = get_graph_properties(G1)
    initialize_csv_file(stanford_metrics_file)
    study_simulation_properties(G1, 50, 30, stanford_metrics_file)

    # Create a scalable graph model with 35000 nodes
    # analyzing the simulation properties
    # Setting the probability for erdos graph
    erdos_probability = 0.3
    G2 = generate_erdos_renyi_graph(350, erdos_probability)
    erdos_renyi_graph_properties = get_graph_properties(G2)
    erdos_metrics_file = 'erdos_renyi_sim_metrics.csv'
    initialize_csv_file(erdos_metrics_file)
    study_simulation_properties(G2, 50, 30, erdos_metrics_file)
