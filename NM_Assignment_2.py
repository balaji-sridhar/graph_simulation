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
    #graph_properties = get_graph_properties(G1)
    #log.info("Value of the graph properties: %s ", graph_properties)


def get_graph_properties(G):
    # Print the graph properties, to be used for analysis
    log.info("Analyzing the graph : ")
    outdeg = G.out_degree()
    to_remove_out = [n for n in outdeg if outdeg[n] == 0]
    graph_properties = {"zero_outdegree_nodes": len(to_remove_out)}
    log.debug("Node whose out degree is zero: %s ", to_remove_out)
    in_degree = G.in_degree()
    to_remove_in = [n for n in in_degree if in_degree[n] == 0]
    graph_properties["zero_indegree_nodes"] = len(to_remove_in)
    log.debug("Nodes whose in degree is zero : %s", to_remove_in)
    # Betweenness of the graph
    graph_betweenness = nx.betweenness_centrality(G)
    # Strongly connected component
    graph_scc = nx.number_strongly_connected_components(G)
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
            G2.add_node(i, node_props)
            s = i
            t = random.choice(G2.nodes())
            log.debug("%s , %s",s, t)
            if s == t:
                t = random.choice(G2.nodes())
            # G2.add_edges_from([(s, t)])
            add_citations(G2, s, i)
    log.info("Number of nodes and edges in the graph  --- %s , %s", G2.number_of_nodes(), G2.number_of_edges())

    # Removing self loop in the graph

    log.debug("%s" , G2.edges())
    self_loop_list = G2.selfloop_edges()
    log.info("Found %s Number of self loops in Graph", len(self_loop_list))
    for iter in self_loop_list:
        print(iter[0])
        G2.remove_edge(iter[0], iter[0])
    log.debug("Aft: %s ", G2.edges())
    graph_properties = get_graph_properties(G2)
    log.info("Value of the graph properties: %s ", graph_properties)

    # Writing generated graph to the file in json format
    data = json_graph.node_link_data(G2)
    nx.write_edgelist(G2, "edgelist_graph")
    f = open('node_link_data.json', 'w')
    # f.write(data)
    json.dump(data, f)


def add_citations(G2, paper, n):
    log.debug("Adding node %s to the graph", n )
    for i in range(1, n%12):
        rand_limit = i
        # Limit maximum number of edges per node to 100
        if i > 15:
            rand_limit = 15
        k = random.randint(1, rand_limit)
        # print("Adding ", k, "citations to the paper")
        s = paper
        for j in range(1, k):
            t = random.choice(G2.nodes())
            if s == t | G2.has_edge(s, t) | G2.has_edge(t, s):
                log.debug("No edge will be added as they exist between %s and %s ", s, t)
            else:
                G2.add_edges_from([(s, t)])

            # Making sure the graph is acyclic
            # print(G2.has_edge(s, t), G2.has_edge(t, s) , s,t)
            # Removing cyclic edges
            if (G2.has_edge(s, t)) and (G2.has_edge(t, s)):
                log.debug("%s %s", G2.get_edge_data(s, t, 0), G2.get_edge_data(t, s, 0))
                log.debug("Edge exist both way between %s and %s ", s, t)
                G2.remove_edge(s, t)
            # Removing self loops
            if G2.has_edge(s, s):
                G2.remove_edge(s, t)


def load_node_properties():
    node_props = [dict() for x in range(3)]
    node_props[0] = {"Group": "science", "subgroup": "chemistry", "affinity": 0.1}
    node_props[1] = {"Group": "science", "subgroup": "chemistry", "affinity": 0.2}
    node_props[2] = {"Group": "science", "subgroup": "chemistry", "affinity": 0.3}
    return node_props[0]

if __name__ == "__main__":
    log.basicConfig(level=log.INFO)
    load_standford_graph("NodeConnections.txt")
    create_graph_organically(9450)
