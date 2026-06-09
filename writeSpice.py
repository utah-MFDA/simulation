# fmt:off
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import re
import csv
import ast

import SimulationXyce

import os
import sys
import json
import regex
import mmap
import copy
import logging

from pprint import pp

# moved add_probes to add_probe.py

def convert_dict_to_probes(probes):
    pass


def generate_source_list(spice_config_class, has_chem=False, has_temp=False):

    dev_lines = {}

    for key, dev in spice_config_class.getDeviceList().items():
        dev_lines[dev.getNode()] = [
            dev.getType(),
            f'{dev.getNode()}_dev',
            f'{dev.getNode()}_in']
        # adds chem port
        if has_chem:
            dev_lines[dev.getNode()].append(f"{dev.getNode()}_in_chem")
        if has_temp:
            dev_lines[dev.getNode()].append(f"{dev.getNode()}_in_heat")
        # adds arguments
        if isinstance(dev.getArgs(), dict):
            for key, val in dev.getArgs().items():
                dev_lines[dev.getNode()].append(f"{key}={val}")
        elif isinstance(dev.getArgs(), list):
            for a in dev.getArgs():
                dev_lines[dev.getNode()].append(a)
        elif isinstance(dev.getArgs(), str):
            dev_lines[dev.getNode()].append(dev.getArgs())

    chem_args = {}
    # print(spice_config_class.getInputChemList())
    if has_chem:
        for key, chem in spice_config_class.getInputChemList().items():
            if isinstance(chem, SimulationXyce.SimulationXyce.ChemInput):
                chem_args[key] = {chem.getNode(): chem.getInValue()}
            if isinstance(chem, list):
                chem_args[key] = {}
                for c in chem:
                    chem_args[key][c.getNode()] = chem.getInValue()

    return dev_lines, chem_args


def generate_time_lines(spice_config_class):
    # returns a list

    out_lines = []
    if "transient" in spice_config_class.getSimulationTimes():
        for t in spice_config_class.getSimulationTimes()["transient"]:
            out_lines.append([".tran"] + t[1:])
    if "static" in spice_config_class.getSimulationTimes():
        for t in spice_config_class.getSimulationTimes()["static"]:
            out_lines.append([".dc"] + t[1:])

    return out_lines


"""
This function inserts the channel graph into the verilog graph
"""
def merge_wl_net(
    in_g,
    wl_g,
    node,
    wl_file=None,
    sim_type="chem",
    debug_node = False,
    debug_edge = False,
    debug_draw=False
):

    import matplotlib.pyplot as plt

    mapping = {}

    for common_node in [n for n in wl_g.nodes if n in in_g.nodes]:
        for prop in in_g.nodes[common_node].items():
            print("   Transfer prop -", prop[0], ':', prop[1])
            wl_g.nodes[common_node][prop[0]] = in_g.nodes[common_node][prop[0]]

    if wl_file is not None:
        node_wl_dict = wl_file[node]

    for n in list(wl_g.nodes):
        if re.match(r'br_\d_\d', str(n)) is not None:
            br_pt = True
            mapping[n] = f"{node}_{n}"
            wl_g.nodes[n]['virt_node'] = ''
        else:
            br_pt = False

        if n not in node_wl_dict and not br_pt and n not in in_g.nodes:
            print("Removing node:", n)
            wl_g.remove_node(n)
            continue

        if len(str(n)) > 0 and \
                (str(n)[0] in [str(i) for i in range(0,10)] and not br_pt):
            wl_g.nodes[n]['route'] = None
            wl_g.nodes[n]['node_type'] = 'wire'
            wl_g.nodes[n]['chan_len'] = node_wl_dict[n]
            for con_n in wl_g[n]:
                #if re.match(r'br_\d_\d', str(n)) is not None:
                wl_g.edges[(n, con_n)]['fl_net'] = f"{node}_{con_n}"
                if sim_type == 'chem' or sim_type == 'heat':
                    wl_g.edges[(n, con_n)]['ch_net'] = f"{node}_{con_n}_chem"
                if sim_type == 'heat':
                    wl_g.edges[(n, con_n)]['ht_net'] = f"{node}_{con_n}_heat"

            mapping[n] = f"{node}_{n}"
    wl_g = nx.relabel_nodes(wl_g, mapping)

    # validate
    # nx.draw(in_g, with_labels = True)
    # plt.show()

    # if re.match(f'soln\d+', str(node)) is not None:
    #     return in_g

    if in_g.nodes[node]['node_type'] in ['input', 'output']:

        # if len(in_g[node]) == 1:
        if len(wl_g.nodes) == 1:
            conn_node = list(wl_g[node])[0]
            print("New input/output node:", conn_node)
            # the regex if different now
            # Checks name if break point
            if re.match(r'[\w_]+_br_\d_\d', str(conn_node)) is not None:
                for conn_node2 in list(wl_g[conn_node]):
                    # print(conn_node2)
                    wl_g.nodes[conn_node2]['node_type'] = wl_g.nodes[node]['node_type']
                    wl_g.nodes[conn_node2]['input_node'] = node
                wl_g.nodes[node]['virt_node'] = ''
            else:
                wl_g.nodes[conn_node]['node_type'] = wl_g.nodes[node]['node_type']
                if wl_g.nodes[node]['node_type'] == 'input':
                    wl_g.nodes[conn_node]['input_node'] = node
                wl_g.nodes[node]['virt_node'] = ''
        else:
            pass
            #raise Exception(f"Too many nodes connected to {node}; nodes {in_g[node]}")

    in_g.remove_node(node)
    in_g = nx.compose(in_g, wl_g)

    # write nodes and edges to terminal

    if node == 'soln2':
        debug_node = False
        debug_edge = False
    # debug_draw = True
    if debug_node:
        print("Wirelength nodes: ")
        for n in wl_g.nodes:
            print(n)
            print(wl_g.nodes[n])
        print("Result nodes: ")
        for n in in_g.nodes:
            print(n)
            print(in_g.nodes[n])
    if debug_edge:
        print("Wirelength edges: ")
        for e in wl_g.edges:
            print(e)
            print(wl_g.get_edge_data(e[0], e[1]))
        print("Result edges: ")
    if debug_draw:
        import matplotlib.pyplot as plt
        nx.draw_spring(wl_g, with_labels=True)
        plt.show()
        nx.draw_spring(in_g, with_labels=True)
        plt.show()

    return in_g

"""
    Used as nx.node_link_graph() was having issues in this code
"""

def build_graph(dict_gph):
    G_out = nx.Graph()
    for nd in dict_gph['nodes']:
        G_out.add_node(nd['id'])
        for nd_k, nd_val in nd.items():
            if nd_k is not 'id':
                G_out.nodes[nd['id']][nd_k] = nd_val

    if 'edges' in dict_gph:
        for edg in dict_gph['edges']:
            G_out.add_edge(edg['source'], edg['target'])
    if 'links' in dict_gph:
        for edg in dict_gph['links']:
            G_out.add_edge(edg['source'], edg['target'])

    return G_out


"""


"""

def generate_spice_nets(
    in_netlist,
    length_list=None,
    add_prn_to_list=False,
    pcell_file=None,
    wl_graph=None,
    simulation_type="chem"
):

    WIRE = ['wire', 'input', 'output']
    PROBE = ['flow_probe', 'pressure_probe', 'concentration_probe']
    FL_PROBE = ['flow_probe', 'pressure_probe']
    C_PROBE = ['chem_probe', 'concentration_probe']
    T_PROBE = ['temp_probe', 'temperature_probe']

    if length_list is None:
        no_lengths = True
    else:
        no_lengths = False
        len_df = get_length_list(length_list)

        # check default path for route_nets
    if 'XYCE_WL_GRAPH' in os.environ or \
            os.path.exists(length_list.replace('_length.csv', '_route_nets.json')):
        from networkx.readwrite import json_graph
        wl_graph_f = ''
        if wl_graph is None:
            if length_list[-4:] == '.csv':
                wl_graph_f = length_list.replace('_length.csv', '_route_nets.json')
            if length_list[-5:] == '.xlsx':
                wl_graph_f = length_list.replace('_length.xslx', '_route_nets.json')
        wl_graph = {}
        print("Reading: ", wl_graph_f)
        with open(wl_graph_f, 'r') as js_f:
            json_f = json.load(js_f)
        for r in json_f.keys():
            # print(f'r: "{r}"')
            # print('VAL:')
            # pp(json_f[r])
            new_graph = build_graph(json_f[r])
            if len(new_graph.nodes) > 1:
                wl_graph[r] = new_graph
                #for wl_n in wl_graph.items():
                #    merge_wl_net(in_netlist, wl_n[1], wl[0])
        print("Loading graph:", wl_graph_f)
        # unset variable
        # os.environ.pop('XYCE_WL_GRAPH')


    # start internal net functions ####

    def add_fl_net_2_edge(g, edge, net_name):
        if 'fl_net' in g.edges[edge]:
            if net_name == g.edges[edge]['fl_net']:
                print(f"  Net {net_name} already added to {edge}")
            else:
                raise Exception(f"Conflicting net names adding {net_name}, already {g.edges[edge]['fl_net']}")
        else:
            g.edges[edge]['fl_net'] = net_name

    def add_ch_net_2_edge(g, edge, net_name):
        #print(f"Prop: {g.edges[edge]}")
        if "has_flow_probe" in g.edges[edge]:
            print("EDGE IN FLOW NODE", edge)

        if 'ch_net' in g.edges[edge]:
            if net_name == g.edges[edge]['ch_net']:
                print(f"  Net {net_name} already added to {edge}")
            else:
                raise Exception(f"Conflicting net names adding {net_name}, already {g.edges[edge]['ch_net']}")
        else:
            g.edges[edge]['ch_net'] = net_name

    def add_ht_net_2_edge(g, edge, net_name):
        #print(f"Prop: {g.edges[edge]}")
        if "has_flow_probe" in g.edges[edge]:
            print("EDGE IN FLOW NODE", edge)

        if 'ht_net' in g.edges[edge]:
            if net_name == g.edges[edge]['ht_net']:
                print(f"  Net {net_name} already added to {edge}")
            else:
                raise Exception(f"Conflicting net names adding {net_name}, already {g.edges[edge]['ht_net']}")
        else:
            g.edges[edge]['ht_net'] = net_name


    def add_net_defs_to_graph(g, node, comp_node):
        if g.nodes[comp_node]['node_type'] in PROBE:
            print(f"  Skipping probe node {comp_node}")
            return
        print("comp node :", comp_node, "wire node: ", node)

        # check for flow probe
        net_edge = (comp_node, node)
        if any([(fl_pr in g.edges[net_edge]) for fl_pr in FL_PROBE]):
            print(f"fluid probe at edge {net_edge}")
            g.edges[net_edge]['fl_net'] = {
                "comp_net": f"{node}_{comp_node}_comp",
                "channel_net": f"{node}_{comp_node}_net"
            }
            print(g.edges[net_edge]['fl_net'])
        else:
            chan_fluid_net = f"{node}_{comp_node}"
            add_fl_net_2_edge(g, (comp_node, node), chan_fluid_net)

        # check for chemical probe
        if any([(fl_pr in g.edges[net_edge]) for fl_pr in C_PROBE]):
            print(f"chemical probe at edge {net_edge}")
            g.edges[net_edge]['ch_net'] = {
                "comp_net": f"{node}_{comp_node}_comp_chem",
                "channel_net": f"{node}_{comp_node}_net_chem"
            }
        else:
            chan_chem_net  = f"{node}_{comp_node}_chem"
            print("add edge:", chan_chem_net)
            add_ch_net_2_edge(g, (comp_node, node), chan_chem_net)

        # check for temperature probe
        if any([(fl_pr in g.edges[net_edge]) for fl_pr in T_PROBE]):
            print(f"temperature probe at edge {net_edge}")
            g.edges[net_edge]['ht_net'] = {
                "comp_net": f"{node}_{comp_node}_comp_heat",
                "channel_net": f"{node}_{comp_node}_net_heat"
            }
        else:
            chan_heat_net  = f"{node}_{comp_node}_heat"
            print("add edge:", chan_heat_net)
            add_ht_net_2_edge(g, (comp_node, node), chan_heat_net)

    # end internal net functions ####

    for node in list(in_netlist.nodes):

        #nx.draw(in_netlist, with_labels=True)
        #plt.show()

        ############# IF INPUT #############

        if in_netlist.nodes[node]['node_type'] == 'input':
            # and (not no_lengths):
            #in_netlist.nodes[node]['node_color']='tab:blue'
            #nx.draw(in_netlist, with_labels=True)
            #plt.show()
            #nx.draw(wl_graph[node], with_labels=True)
            #plt.show()

            #  add a place holder
            # TODO make direct connections to components
            if no_lengths:
                wl = 0.01
            elif isinstance(len_df, pd.DataFrame):
                wl = len_df.loc[node]["length (mm)"]

            elif isinstance(len_df, dict):
                wl = len_df[node] #["length (mm)"]

            if isinstance(wl, float):
                in_netlist.nodes[node]['chan_len'] = wl
                node_edges = list(in_netlist.edges(node))

                if len(node_edges) == 1:
                    comp_node = list(in_netlist[node])[0]
                    add_net_defs_to_graph(in_netlist, node, comp_node)

                else:
                    raise Exception(f"Too many nodes in input, {node_edges}. This will be handled by a net parser, the length file is invalid")

            elif isinstance(wl, dict):
                print(f"connecting net {node}")
                if wl_graph is None:
                    print(f"failed to connect graph, {('XYCE_WL_GRAPH' in os.environ)}")
                # print(wl_graph)
                in_netlist = merge_wl_net(
                    in_netlist,
                    wl_graph[node],
                    node, 
                    wl_file=len_df,
                    sim_type=simulation_type
                )
            else:
                pass

        ############# IF OUTPUT #############

        elif in_netlist.nodes[node]['node_type'] == 'output':
            # TODO check if output as dev
            #print(len_df)

            # get wire length
            if no_lengths:
                wl = 0.01
            elif isinstance(len_df, pd.DataFrame):
                try:
                    wl = len_df.loc[node]["length (mm)"]
                except KeyError:
                    raise KeyError(f"Not able to find node {node} in lenght file {os.path.abspath(wl_graph_f)}")
            elif isinstance(len_df, dict):
                wl = len_df[node] #["length (mm)"]

            if isinstance(wl, float):
                in_netlist.nodes[node]['chan_len'] = wl
                node_edges = list(in_netlist.edges(node))

                if len(node_edges) == 1:
                    comp_node = list(in_netlist[node])[0]
                    add_net_defs_to_graph(in_netlist, node, comp_node)

                else:
                    raise Exception(f"Too many nodes in input, {node_edges}. This will be handled by a net parser, the length file is invalid")
            elif isinstance(wl, dict):
                try:
                    in_netlist = merge_wl_net(
                        in_netlist,
                        wl_graph[node],
                        node,
                        wl_file=len_df,
                        sim_type=simulation_type
                    )
                except TypeError:
                    raise ValueError("Missing XYCE_WL_GRAPH in environment, usually (design)_route_nets.json in results dir")
            else:
                pass

        ############# IF WIRE #############

        elif in_netlist.nodes[node]['node_type'] == 'wire':
            # and (not no_lengths):
            if no_lengths:
                wl = 0.01
            elif isinstance(len_df, pd.DataFrame):
                wl = len_df.loc[node]["length (mm)"]
            elif isinstance(len_df, dict):
                # print(len_df)
                wl = len_df[node] #["length (mm)"]

            if isinstance(wl, float):
                in_netlist.nodes[node]['chan_len'] = wl
                node_edges = list(in_netlist.edges(node))

                if len(node_edges) == 2:
                    for comp_node in in_netlist[node]:
                        add_net_defs_to_graph(in_netlist, node, comp_node)

                else:
                    raise Exception(f"Too many nodes in input, {node_edges}. This will be handled by a net parser, the length file is invalid")
            elif isinstance(wl, dict):
                in_netlist = merge_wl_net(
                    in_netlist,
                    wl_graph[node],
                    node,
                    wl_file=len_df,
                    sim_type=simulation_type
                )
            else:
                pass

        # since only nets are added the components are implicitly added
        elif in_netlist.nodes[node]['node_type'] in ['flow_probe', 'pressure_probe']:
            node_edges = list(in_netlist.edges(node))
            if len(node_edges) == 2:
                a_pr_ns = list(in_netlist[node])
                a_pr_nt = [
                    in_netlist.nodes[a_pr_ns[0]]['node_type'],
                    in_netlist.nodes[a_pr_ns[1]]['node_type']
                ]

                if a_pr_nt[0] in WIRE and a_pr_nt[1] not in WIRE:
                    chan_chem_net  = f"{a_pr_ns[0]}_{a_pr_ns[1]}_chem"
                elif a_pr_nt[0] not in WIRE and a_pr_nt[1] in WIRE:
                    chan_chem_net  = f"{a_pr_ns[1]}_{a_pr_ns[0]}_chem"
                elif a_pr_nt[0] not in WIRE and a_pr_nt[1] not in WIRE:
                    print(f"Connecting two components {a_pr_ns}")
                    chan_chem_net  = f"{a_pr_ns[0]}_{a_pr_ns[1]}_chem"
                else:
                    raise Exception("Nodes are both nodes wires for probe")

                if simulation_type == "heat":
                    if a_pr_nt[0] in WIRE and a_pr_nt[1] not in WIRE:
                        chan_heat_net  = f"{a_pr_ns[0]}_{a_pr_ns[1]}_heat"
                    elif a_pr_nt[0] not in WIRE and a_pr_nt[1] in WIRE:
                        chan_heat_net  = f"{a_pr_ns[1]}_{a_pr_ns[0]}_heat"
                    elif a_pr_nt[0] not in WIRE and a_pr_nt[1] not in WIRE:
                        print(f"Connecting two components {a_pr_ns}")
                        chan_heat_net  = f"{a_pr_ns[0]}_{a_pr_ns[1]}_heat"
                    else:
                        raise Exception("Nodes are both nodes wires for probe")


                for att_node in in_netlist[node]:
                    chan_fluid_net = f"{node}_{att_node}"
                    print("attached node :", att_node, "probe node: ", node,'\nNet:', chan_fluid_net)
                    add_fl_net_2_edge(
                        in_netlist,
                        (att_node, node),
                        chan_fluid_net
                    )
                    add_ch_net_2_edge(
                        in_netlist,
                        (att_node, node),
                        chan_chem_net
                    )
                    if simulation_type == "heat":
                        add_ht_net_2_edge(
                            in_netlist,
                            (att_node, node),
                            chan_heat_net
                        )
            else:
                raise Exception(f"Too many nodes in input, {node_edges}. This will be handled by a net parser, the length file is invalid")
        else:
            print(f"Node {node} is of type {in_netlist.nodes[node]['node_type']} (no action)")

    # iterate through nodes only looking at component nets

    return in_netlist


def read_pcell_file(pc_file):

    if '.' not in os.path.basename(pc_file):
        reader = csv.DictReader(open(pc_file, 'r'))
        pcomp_dict = {}
        for row in reader:
            pcomp_dict[row['lef']] = {'base cell': row['cell_name'], 'parameters':row['parameters']}
        print(pcomp_dict)
        return pcomp_dict
    elif pc_file[-4] == '.csv':
        reader = csv.DictReader(open(pc_file, 'r'))
        pcomp_dict = {}
        for row in reader:
            pcomp_dict[row['lef']] = {'base cell': row['cell_name'], 'parameters':row['parameters']}
        print(pcomp_dict)
        return reader
    else:
        print("Pcell file type not supported yet,", pc_file)

"""
    Writes the netlist file from the generated graph
"""

def write_components_from_graph(
    in_g,
    of,
    probe_list=[],
    pcell_file=None,
    simulation_type="chem",
    channel_dev=None,
):
    #nx.draw_spring(in_g, with_labels=True)
    #plt.show()

    if simulation_type == "chem":
        CHEM_SIM = True
        HEAT_SIM = False
    elif simulation_type == "heat":
        CHEM_SIM = True
        HEAT_SIM = True
    else:
        CHEM_SIM = False
        HEAT_SIM = False

    if isinstance(of, str):
        of = open(of, 'w+')

    if pcell_file is not None:
        pcells = read_pcell_file(pcell_file)
    else:
        pcells = {}

    in_nodes = []
    out_nodes = []
    wire_nodes = []
    probe_nodes= []
    oth_nodes = []

    new_probes = []
    probe_2_write = []

    if channel_dev is not None:
        chan_comp = 'Y' + channel_dev
    elif simulation_type == "flow":
        chan_comp = 'Ychannel_flow'
    elif simulation_type == "chem":
        chan_comp = 'Ychannel'
    elif simulation_type == "heat":
        chan_comp = 'Ychannel_ht'

    for n in in_g.nodes:
        # these are handled by the graph wires
        if 'virt_node' in in_g.nodes[n]:
            continue
        if in_g.nodes[n]['node_type'] == 'input':
            in_nodes.append(n)
        elif in_g.nodes[n]['node_type'] == 'output':
            out_nodes.append(n)
        elif in_g.nodes[n]['node_type'] == 'wire':
            wire_nodes.append(n)
        elif in_g.nodes[n]['node_type'] in ['flow_probe', 'pressure_probe']:
            probe_nodes.append(n)
        else:
            oth_nodes.append(n)

    print(
        "IN nodes:", in_nodes,
        '\nOUT nodes:', out_nodes,
        '\nCHANNEL nodes:', wire_nodes,
        '\nCOMPONENT nodes:', oth_nodes
    )
    print(f"""
    SIM TYPE:{simulation_type}
    """)
    # write nodes
    for i_n in in_nodes:
        # temp fix
        if 'chan_len' not in in_g.nodes[i_n]:
            in_g.nodes[i_n]['chan_len'] = '0.1m'
            e_in = list(nx.all_neighbors(in_g, i_n))[0]
            if 'fl_net' not in in_g[i_n][e_in] or 'fl_net' not in in_g[e_in]:
                in_g.edges[(i_n, e_in)]['fl_net'] = e_in
                in_g.edges[(i_n, e_in)]['ch_net'] = e_in + "_chem"
                if HEAT_SIM:
                    in_g.edges[(i_n, e_in)]['ht_net'] = e_in + "_heat"
        try:
            e = list(in_g.edges(i_n))[0]
            e_fl = in_g[e[0]][e[1]]['fl_net']
            if CHEM_SIM:
                e_ch = in_g[e[0]][e[1]]['ch_net']
            if HEAT_SIM:
                e_ht = in_g[e[0]][e[1]]['ht_net']
        except KeyError:
            raise KeyError(f"Net node properly made for edge {e}, node {i_n}")

        wl = in_g.nodes[i_n]['chan_len']
        if isinstance(e_fl, dict):
            e_fl = e_fl["channel_net"]
        if CHEM_SIM and isinstance(e_ch, dict):
            e_ch = e_ch["channel_net"]
        if HEAT_SIM and isinstance(e_ht, dict):
            e_ht = e_ht["channel_net"]
        if 'input_node' in in_g.nodes[i_n]:
            inst_n = i_n  # instance captured so it is unique
            i_n = in_g.nodes[i_n]['input_node']  # syncs up with pump nodes

            # write to file

            #of.write(f"{chan_comp} {inst_n} {i_n}_in {e_fl} {i_n}_in_chem {e_ch} length={wl}m\n")
            of.write(f"{chan_comp} {inst_n} {i_n}_in {e_fl}")
            # add chemical probes
            if CHEM_SIM:
                of.write(f" {i_n}_in_chem {e_ch}")
            if HEAT_SIM:
                of.write(f" {i_n}_in_heat {e_ht}")
            # write params
            of.write(f" length={wl}m\n")
        else:
            # write to file

            #of.write(f"{chan_comp} {i_n} {i_n}_in {e_fl} {i_n}_in_chem {e_ch} length={wl}m\n")
            of.write(f"{chan_comp} {i_n} {i_n}_in {e_fl}")
            # add chemical probes
            if CHEM_SIM:
                of.write(f" {i_n}_in_chem {e_ch}")
            if HEAT_SIM:
                of.write(f" {i_n}_in_heat {e_ht}")
            # write params
            of.write(f" length={wl}m\n")

    of.write('\n\n')

    for w_n in wire_nodes:
        e = list(in_g.edges(w_n))
        print(f"edges of node {w_n}: {e}")
        if len(e) != 2:
            continue
        e_fl1 = in_g[e[0][0]][e[0][1]]['fl_net']
        e_fl2 = in_g[e[1][0]][e[1][1]]['fl_net']

        # TODO seperate chem or heat
        if CHEM_SIM:
            e_ch1 = in_g[e[0][0]][e[0][1]]['ch_net']
            e_ch2 = in_g[e[1][0]][e[1][1]]['ch_net']

        if HEAT_SIM:
            if 'ht_net' in in_g[e[0][0]][e[0][1]]:
                e_ht1 = in_g[e[0][0]][e[0][1]]['ht_net']
                e_ht2 = in_g[e[1][0]][e[1][1]]['ht_net']
            else:
                e_ht1 = in_g[e[0][0]][e[0][1]]['ch_net'].replace('_chem', '_heat')
                e_ht2 = in_g[e[1][0]][e[1][1]]['ch_net'].replace('_chem', '_heat')

        # need to fix addition of sets
        # if isinstance(e_fl1, set):
        #     e_fl1 = list(e_fl1)[0]
        # if isinstance(e_fl2, set):
        #     e_fl2 = list(e_fl2)[0]
        # if isinstance(e_ch1, set):
        #     e_ch1 = list(e_ch1)[0]
        # if isinstance(e_ch2, set):
        #     e_ch2 = list(e_ch2)[0]
        if isinstance(e_fl1, dict):
            e_fl1 = e_fl1["channel_net"]
        if isinstance(e_fl2, dict):
            e_fl2 = e_fl2["channel_net"]

        if CHEM_SIM and isinstance(e_ch1, dict):
            e_ch1 = e_ch1["channel_net"]
        if CHEM_SIM and isinstance(e_ch2, dict):
            e_ch2 = e_ch2["channel_net"]

        if HEAT_SIM and isinstance(e_ht1, dict):
            e_ht1 = e_ht1["channel_net"]
        if HEAT_SIM and isinstance(e_ht2, dict):
            e_ht2 = e_ht2["channel_net"]


        wl = in_g.nodes[w_n]['chan_len']

        # write init flow devs
        of.write(f"{chan_comp} {w_n} {e_fl1} {e_fl2}")
        if CHEM_SIM:
            of.write(f" {e_ch1} {e_ch2}")
        if HEAT_SIM:
            of.write(f" {e_ht1} {e_ht2}")
        # write params
        of.write(f" length={wl}m\n")


    of.write('\n\n')

    for o_n in out_nodes:
        if 'chan_len' not in in_g.nodes[o_n]:
            e_out = list(in_g[o_n])[0]
            #print(o_n, e_out)
            in_g.edges[(o_n, e_out)]['fl_net'] = e_out
            if CHEM_SIM:
                in_g.edges[(o_n, e_out)]['ch_net'] = e_out + "_chem"
            if HEAT_SIM:
                in_g.edges[(o_n, e_out)]['ht_net'] = e_out + "_heat"
            in_g.nodes[o_n]['chan_len'] = '0.1m'
        try:
            e = list(in_g.edges(o_n))[0]
            e_fl = in_g[e[0]][e[1]]['fl_net']
            if CHEM_SIM:
                e_ch = in_g[e[0]][e[1]]['ch_net']
            if HEAT_SIM:
                e_ht = in_g[e[0]][e[1]]['ht_net']
        except KeyError:
            raise KeyError(f"Net node properly made for edge {e}, node {o_n}")
        # if isinstance(e_fl, set):
        #     e_fl = list(e_fl)[0]
        # if isinstance(e_ch, set):
        #     e_ch = list(e_ch)[0]
        # change for probe
        if isinstance(e_fl, dict):
            e_fl = e_fl["channel_net"]
        if CHEM_SIM and isinstance(e_ch, dict):
            e_ch = e_ch["channel_net"]
        if HEAT_SIM and isinstance(e_ht, dict):
            e_ht = e_ht["channel_net"]
        wl = in_g.nodes[o_n]['chan_len']

        # of.write(f"{chan_comp} {o_n} {e_fl} 0 {e_ch} {o_n}_out_chem length={wl}m\n")
        of.write(f"{chan_comp} {o_n} {e_fl} 0")
        if CHEM_SIM:
            of.write(f" {e_ch} {o_n}_out_chem")
        if HEAT_SIM:
            of.write(f" {e_ht} {o_n}_out_heat")
        of.write(f" length={wl}m\n")

    of.write('\n\n')

    for oth_n in oth_nodes:
        n_type = in_g.nodes[oth_n]['node_type']

        def check_port(c_nd, c_port):
            if in_g.nodes[c_nd][c_port] in in_g[c_nd]:
                return in_g.nodes[c_nd][c_port]
            else:
                port_reg = in_g.nodes[c_nd][c_port] + r'\w+;'
                nets = re.findall(port_reg, '; '.join(list(in_g[c_nd]))+';')
                if len(nets) == 1:
                    return nets[0][:-1]  # remove ';'
                elif len(nets) > 1:
                    raise ValueError("Port naming collision, "+str(nets))
                else:
                    raise Exception("No ports found matching "+str(port_reg))


        port_n = []
        print(f"node: {oth_n}, connected nodes {in_g[oth_n]}")
        # currently assume in-out and a-b-out
        # TODO need to identify node names from library
        if len(in_g[oth_n]) == 2:
            port_n.append(check_port(oth_n, 'in_fluid'))
            port_n.append(check_port(oth_n, 'out_fluid'))
        if len(in_g[oth_n]) == 3:
            port_n.append(check_port(oth_n, 'a_fluid'))
            port_n.append(check_port(oth_n, 'b_fluid'))
            port_n.append(check_port(oth_n, 'out_fluid'))

        #  TODO move to edge writing
        # overwrites previous probe nodes
        fl_wr_new = []
        ch_wr_new = []
        ht_wr_new = []
        try:
            for pn in port_n:
                if isinstance(in_g.edges[(oth_n, pn)]['fl_net'], dict):
                    fl_wr_new.append(in_g.edges[(oth_n, pn)]['fl_net']["comp_net"])
                else:
                    # if isinstance(in_g.edges[(oth_n, pn)]['fl_net'], set):
                    #     fl_wr_new.append(list(in_g.edges[(oth_n, pn)]['fl_net'])[0])
                    # else:
                    fl_wr_new.append(in_g.edges[(oth_n, pn)]['fl_net'])

                if CHEM_SIM and isinstance(in_g.edges[(oth_n, pn)]['ch_net'], dict):
                    ch_wr_new.append(in_g.edges[(oth_n, pn)]['ch_net']["comp_net"])
                elif CHEM_SIM:
                    # if isinstance(in_g.edges[(oth_n, pn)]['ch_net'], set):
                    #     ch_wr_new.append(list(in_g.edges[(oth_n, pn)]['ch_net'])[0])
                    # else:
                    ch_wr_new.append(in_g.edges[(oth_n, pn)]['ch_net'])
                else:
                    pass

                if HEAT_SIM and 'ht_net' not in in_g.edges[(oth_n, pn)]:
                    in_g[oth_n][pn]['ht_net'] = in_g[oth_n][pn]['ch_net'].replace('_chem', '_heat')

                if HEAT_SIM and isinstance(in_g.edges[(oth_n, pn)]['ht_net'], dict):
                    ht_wr_new.append(in_g.edges[(oth_n, pn)]['ht_net']["comp_net"])
                elif HEAT_SIM:
                    # if isinstance(in_g.edges[(oth_n, pn)]['ch_net'], set):
                    #     ch_wr_new.append(list(in_g.edges[(oth_n, pn)]['ch_net'])[0])
                    # else:
                    ht_wr_new.append(in_g.edges[(oth_n, pn)]['ht_net'])
                else:
                    pass
        except KeyError:
            raise KeyError(f"{pn} not in nets of component {oth_n}, nets: {in_g[oth_n]}")

        fl_wr = ' '.join(fl_wr_new)
        if CHEM_SIM:
            ch_wr = ' '.join(ch_wr_new) + ' '
        if HEAT_SIM:
            ht_wr = ' '.join(ht_wr_new) + ' '

        if pcell_file is not None and \
                pcells is not None and \
                n_type in pcells:
            #of.write(f"Y{pcells[n_type]['base cell']} {oth_n} {fl_wr} {ch_wr} {pcells[n_type]['parameters']}\n")
            of.write(f"Y{pcells[n_type]['base cell']} {oth_n} {fl_wr}")
            if CHEM_SIM:
                of.write(f" {ch_wr}")
            if HEAT_SIM:
                of.write(f" {ht_wr}")
            of.write(f" {pcells[n_type]['parameters']}\n")
        else:
            of.write(f"Y{in_g.nodes[oth_n]['node_type']} {oth_n} {fl_wr}")
            if CHEM_SIM:
                of.write(f" {ch_wr}")
            if HEAT_SIM:
                of.write(f" {ht_wr}")
            of.write("\n")


    of.write("\n\n")
    for pr_n in probe_list:
        if 'edge' not in pr_n:
            continue
        #try:
        e = in_g.edges[pr_n['edge']]['fl_net']
        if not isinstance(e, dict):
            raise ValueError(f"Net not properly made for probe {pr_n}, {e}")
        e_fl1 = e['comp_net']
        e_fl2 = e['channel_net']

        if pr_n["probe"] == "chem_probe":
            of.write(f"{pr_n['name']} {e_fl1}_chem {e_fl2}_chem 0V\n")
        else:
            of.write(f"{pr_n['name']} {e_fl1} {e_fl2} 0V\n")

    of.write('\n\n')
    for pr in probe_2_write:
        of.write(re.sub(r'[ ]+', ' ', ' '.join(pr)+'\n'))

    of.write('\n\n')

    return new_probes


def write_time_lines(spice_config_class):
    pass


def check_nets(in_graph, simulation_type='flow'):

    for net_edge in in_graph.edges:
        edge_props = in_graph[net_edge[0]][net_edge[1]]
        if 'fl_net' not in edge_props:
            raise Exception(f"Flow net not in {net_edge}; {in_graph[net_edge[0]][net_edge[1]]}")
        if (simulation_type == 'chem' or simulation_type == 'heat') and \
                'ch_net' not in edge_props:
            raise Exception(f"Chem net not in {net_edge}; {in_graph[net_edge[0]][net_edge[1]]}")
        if (simulation_type == 'heat') and 'ht_net' not in edge_props:
            raise Exception(f"Heat net not in {net_edge}; {in_graph[net_edge[0]][net_edge[1]]}")



def write_spice_file(
    in_netlist,
    probes_list,
    source_lines,
    sims_time_lines=None,
    sim_type=None,
    length_list=None,
    chem_list=None,
    out_file=None,
    add_prn_to_list=False,
    basename_only=False,
    pcell_file=None,
    wl_graph=None,
    simulation_type="chem",
    channel_dev=None
):

    dev = "dev"

    conn_channel = {
        'flow': 'Ychannel',
        'chem': 'Ychannel',
        'heat': 'Ychannel'
    }

    if out_file is None:
        out_file = 'out_spice'
    if out_file.split('.')[-1] == 'cir':
        out_file = '.'.join(out_file.split('.')[:-1])

    if chem_list is None or len(chem_list)==0:
        chem_list = {'':''}
        no_chems  = True
    else:
        no_chems = False

    if 'XYCE_WL_GRAPH' in os.environ or wl_graph is not None:
        if wl_graph is None:
            wl_graph = length_list.replace('_length.csv', '_route_nets.json')

    pc_dict = {}
    if isinstance(pcell_file, str):
        has_pcells = True
        with open(pcell_file, "r+") as pc_if:
            import csv

            pc_reader = csv.reader(pc_if)
            for i, row in enumerate(pc_reader):
                if i == 0:
                    continue
                else:
                    pc_dict[row[0]] = {"pcell": row[1], "params": row[2]}
    else:
        has_pcells = False

    output_file_list = []

    # for each chemical create a netlist file

    for chem, chem_node_dict in chem_list.items():

        chem_out_file = f'{out_file}_{chem}.cir.str'
        print("Writing string file:\n\t", chem_out_file)

        if basename_only:
            output_file_entry = {
                'Chemical': chem,
                'spice_str_file': chem_out_file,
                'spice_file': os.path.basename(chem_out_file)[:-4]}
            if add_prn_to_list:
                output_file_entry["OutputFile"] = (
                    os.path.basename(chem_out_file)[:-4] + ".prn"
                )
        else:
            output_file_entry = {
                "Chemical": chem,
                "spice_str_file": chem_out_file,
                "spice_file": chem_out_file[:-4],
            }
            if add_prn_to_list:
                a, b = os.path.split(chem_out_file)
                # output_file_entry['OutputFile'] = a + "/results/" + b[:-4]+'.prn'
                output_file_entry['OutputFile'] = a + "/" + b[:-4]+'.prn'


        output_file_list.append(output_file_entry)

        if not os.path.isdir(os.path.dirname(chem_out_file)) and \
                os.path.dirname(chem_out_file) != '':
            os.mkdir(os.path.dirname(chem_out_file))

        with open(chem_out_file, 'w+') as c_of:

            c_of.write(f"* Simulation of device {dev}; chem: {chem}\n")

            chem_source_list = copy.deepcopy(source_lines)
            if isinstance(chem_node_dict, dict):
                for node, val in chem_node_dict.items():
                    chem_source_list[node].append(f"chemConcentration={val}")

            # write inputs and connections
            for node, line in chem_source_list.items():
                line[0] = "Y"+line[0]
                new_line = line+['\n']
                new_line = ' '.join(new_line)

                c_of.write(new_line)

            wire_connections = {}
            probe_wires = [[], []]
            node_dict = {}

            in_netlist_temp = copy.deepcopy(in_netlist)
            in_netlist_ch = generate_spice_nets(in_netlist_temp, length_list)

            # check_nets(in_netlist_ch, simulation_type=simulation_type)

            new_probes = write_components_from_graph(
                in_g=in_netlist_ch,
                of=c_of,
                probe_list=probes_list,
                pcell_file=pcell_file,
                simulation_type=simulation_type,
                channel_dev=channel_dev,
            )

            # add transient lines
            c_of.write("\n\n")

            for t in sims_time_lines:
                print(t)
                c_of.write(' '.join(t)+'\n')

            # add probes
            if sim_type is not None:
                if isinstance(sim_type, str):
                    sim_type = [sim_type]

                for st in sim_type:
                    if st == "transient":
                        nl = re.sub(r'[ ]+', r' ', '.print tran '+' '.join([pr["print"] for pr in probes_list])+' '.join(new_probes))
                        c_of.write(nl+'\n')
                    elif st == "static":
                        nl = re.sub(r'[ ]+', r' ', '.print dc '+' '.join([pr["print"] for pr in probes_list])+' '.join(new_probes))
                        c_of.write(nl+'\n')
                    else:
                        raise ValueError("sim_type must be transient or static")
            c_of.write('\n.end')

    if 'XYCE_WL_GRAPH' in os.environ:
        os.environ.pop('XYCE_WL_GRAPH')

    o_csv_col = ['Chemical', 'spice_str_file', 'spice_file']
    if add_prn_to_list:
        o_csv_col.append("OutputFile")
    o_csv = pd.DataFrame(output_file_list, columns=o_csv_col)

    return o_csv


def get_length_list(len_file):

    if len_file.split(".")[-1] == "csv":
        len_df = pd.read_csv(len_file, index_col=0)
    elif len_file.split('.')[-1] == 'xlsx':
        len_df = pd.read_excel(len_file, index_col=0)

    if len_df.shape[0] == 1:
        len_df = len_df.T
    elif len_df.shape[1] == 2:
        len_df = pd.read_csv(len_file, index_col=1)
        len_df = {}
        reader = csv.DictReader(open(len_file, 'r'))
        for r in reader:
            r['length (mm)'] = ast.literal_eval(r['length (mm)'])
            # print(r)
            # print(len(r))
            if len(r['length (mm)']) > 1:
                # possibly unsafe
                len_df[r['wire']] =r['length (mm)']
            else:
                len_df[r['wire']] = r['length (mm)']['']
    elif len_df.shape[1] == 3:
        len_df = pd.read_csv(len_file, index_col=2)

    if isinstance(len_df, pd.DataFrame):
        # print(len_df.shape[0], len_df.shape[1])
        pass
    # print(len_df)

    return len_df

"""
    converts the str node file to num nodes
"""

def convert_nodes_2_numbers_xyce(SPfile, cir_out=False):
    if os.path.isfile(SPfile) and \
            (SPfile[-4:] == ".cir" or SPfile[-8:] == ".cir.str"):
        SPfile = [SPfile]
    else:
        # if directory is given
        SPfile = [
            '/'.join([SPfile, f])
            for f in os.listdir(SPfile)
                if os.path.isfile(os.path.join(SPfile, f)) and f[-4:] == ".cir"]

    for f in SPfile:
        SPfile_o = open(f, "r")

        if cir_out:
            if len(f) > 8 and f[-8:] == ".cir.str":
                new_file = f[:-8] + ".cir"
            elif f[-4:] != ".cir":
                new_file = f + ".cir"
        else:
            new_file = f + ".num"

        with open(new_file, "w") as SPfile_n:

            nodeList = {}

            for line in SPfile_o:
                # remove leading WS
                line = line.rstrip()

                # remove comments
                line = line.split('*')[0]
                line_comment = re.search(r'\*.*$', line)
                if line_comment is None:
                    line_comment = ""

                if re.match(line, r"\s*"):  # == "" or line == "\n":
                    SPfile_n.write(line + line_comment + "\n")
                else:
                    #line_vars = line.replace("  ", " ").split(" ")
                    line_vars = line.split()
                    if len(line_vars) > 1:
                        arg1 = line_vars[0]
                        end_line_str = []
                        line_nodes = []
                        # xyce command start with .
                        if re.match(r'\.[a-zA-Z0-9_]+', line_vars[0]):  # == ".":
                            if line_vars[0][1:] == 'print':
                                for ind, param in enumerate(line_vars[1:]):
                                    for n in nodeList.keys():
                                        if n in param:
                                            n_num = str(nodeList[n])
                                            # rplace_str = "(" + n + ")"
                                            # newParam = param.replace(
                                            #     "(" + n + ")", "(" + n_num + ")"
                                            # )
                                            newParam = re.sub(
                                                r"([VvIi])\(" + n + "\)",
                                                r"\1(" + n_num + r")",
                                                param
                                            )
                                            line_vars[ind + 1] = newParam
                                new_sp_line = " ".join(line_vars) + "\n"
                            else:
                                new_sp_line = " ".join(line_vars) + "\n"
                        # xyce voltage probes start with v
                        elif arg1[0] == "v":
                            for ind, param in enumerate(line_vars[1:]):
                                if ind < 2:
                                    if "=" in param:
                                        end_line_str += [param]
                                    elif param == "0":
                                        line_nodes.append(0)
                                    else:
                                        if param not in nodeList.keys():
                                            # we do not want 0
                                            nodeList[param] = len(nodeList) + 1
                                        line_node = nodeList[param]
                                        line_nodes.append(line_node)
                                if ind >= 2:
                                    end_line_str += [param]
                            # append all
                            # print(arg1)
                            new_sp_line = ' '.join(
                                [arg1] +
                                [str(x) for x in line_nodes] +
                                end_line_str
                                ) + '\n'
                        else:
                            # replaces params for numbers
                            # <device> <name>
                            device = [arg1, line_vars[1]]
                            for param in line_vars[2:]:
                                # exception for parameters which will explicitly use =
                                if "=" in param:
                                    end_line_str += [param]
                                elif param == "0":
                                    line_nodes.append(0)
                                else:
                                    if param not in nodeList.keys():
                                        # we do not want 0
                                        nodeList[param] = len(nodeList) + 1
                                    line_node = nodeList[param]
                                    line_nodes.append(line_node)
                            # append all
                            new_sp_line = ' '.join(
                                device +
                                [str(x) for x in line_nodes] +
                                end_line_str
                                ) + '\n'

                        SPfile_n.write(new_sp_line + line_comment)
                    else:
                        new_sp_line = ""
                        SPfile_n.write(line + line_comment+'\n')
                        SPfile_n.write(new_sp_line + line_comment)

        node_file = f + ".nodes"
        with open(node_file, "w") as node_f:
            json.dump(nodeList, node_f)

        SPfile_o.close()


def visualize_netlist(in_cir):
    netlist_parse_reg = r"^[ ]*((?P<std_comp>[IVivRrCc]\w*)\s+(?P<pos_node>\w+)\s+(?P<neg_node>\w+)\s+(\d+[\w]?[\w]?)\s*?$|(?P<custom_component>[Yy]\w*)\s+(?P<instance>\w+)\s+(?P<params>[\w\s=.]*?$))"

    net_reg = bytes(netlist_parse_reg, "utf-8")

    with open(in_cir, "r+") as f:
        data = mmap.mmap(f.fileno(), 0)
        mo = regex.finditer(net_reg, data, re.MULTILINE)

    for m in mo:

        if "std_comp" in m.groups():
            pass
        elif "custom_component" in m.groups():
            pass

            param_reg = r"[\w=.]+"

            params = regex.finditer()


def generate_cir_main(
    design,
    verilog_file,
    config_file,
    length_file,
    out_file,
    basename_only=False,
    pcell_file=None,
    wl_graph_file=None,
    simulation_type="flow",
    channel_dev=None
):

    sys.path.insert(0, os.path.dirname(os.path.realpath(__file__))+'/v_2_NX/')

    from Verilog2NX import get_modules, visual_graph

    net_dict, net_graph = get_modules(in_v=verilog_file, visual=False)

    # out_probes, netlist_graph_out = add_probes_to_device(probes, netlist_graph['smart_toilet']['netlist'])

    from SimulationXyce import SimulationXyce
    import add_probes

    Xcl = SimulationXyce()
    Xcl.parse_config_file(config_file)

    if Xcl.simulation_type != simulation_type:
        print("Overriding simulation type argument due to config file")
        simulation_type = Xcl.simulation_type

    print("Importing simulation config:")
    print(Xcl.get_sim_str())

    # print(net_graph.keys())
    out_probes, netlist_graph_out, assumed_sim = add_probes.add_probes_to_device(
            Xcl.probes,
            net_graph[design]['netlist']
    )

    print("ASSUMED TYPE:", assumed_sim)

    if assumed_sim == "chem" and simulation_type == "flow":
        simulation_type = "chem"

    if assumed_sim == "heat" and simulation_type == "flow":
        simulation_type = "heat"
    elif assumed_sim == "heat" and simulation_type == "chem":
        simulation_type = "heat"

    dev_lines, chem_args = generate_source_list(
        Xcl,
        has_chem=True,
        has_temp=(simulation_type == "heat")
    )

    sim_lines = generate_time_lines(Xcl)

    sp_files = write_spice_file(
        net_graph[design]['netlist'],
        probes_list=out_probes,
        source_lines=dev_lines,
        length_list=length_file,
        chem_list=chem_args,
        sims_time_lines=sim_lines,
        sim_type="transient",
        out_file=out_file,
        add_prn_to_list=True,
        basename_only=basename_only,
        pcell_file=pcell_file,
        wl_graph=wl_graph_file,
        simulation_type=simulation_type,
        channel_dev=channel_dev
    )

    for spf in sp_files.iterrows():
        convert_nodes_2_numbers_xyce(spf[1]["spice_str_file"], cir_out=True)

    sp_files.to_csv(os.path.dirname(out_file) + "/spice_files.csv")
