# fmt:off
import SimulationXyce

import logging

def add_probes_to_device(probes, netlist_graph):

    probe_list = []
    node = "node"
    dev = "device"

    assumed_sim_type = "flow"

    def add_probe_no_node(probe, probe_list, probe_type):
        print(probe)
        if isinstance(probe, SimulationXyce.SimulationXyce.Probe):
            if p.getNode() not in netlist_graph.nodes:
                logging.debug(f"Nodes in netlist:\n{netlist_graph.nodes}")
                raise KeyError(
                    f"Probe for node {probe.getNode()} not in netlist")
            dev_node = list(netlist_graph[probe.getNode()].keys())[0]
            pr_node = probe.getNode()
        elif isinstance(probe, dict):
            if probe[node] not in netlist_graph.nodes:
                logging.debug(f"Nodes in netlist:\n{netlist_graph.nodes}")
                raise KeyError(f"Probe for node {probe[node]} not in netlist")
            dev_node = list(netlist_graph[probe[node]].keys())[0]
            pr_node = probe[node]
        else:
            raise ValueError("Passed probe is not of type dict or Probe")

        # check for existing probes
        if f'V({pr_node}_{dev_node}_chem)' not in probe_list:
            dev_node = list(netlist_graph[pr_node].keys())[0]
            probe_list.append(f'V({pr_node}_{dev_node}_chem)')

    # sub-functions ---------------------------------------
    def add_probe_w_node(probe, probe_list, probe_type):
        print(probe)
        if isinstance(probe, SimulationXyce.SimulationXyce.Probe):
            if p.getNode() not in netlist_graph.nodes:
                logging.debug(f"Nodes in netlist:\n{netlist_graph.nodes}")
                raise KeyError(
                    f"Probe for node {probe.getNode()} not in netlist")
            dev_node = list(netlist_graph[probe.getNode()].keys())[0]
            pr_node = probe.getNode()
        elif isinstance(probe, dict):
            if probe[node] not in netlist_graph.nodes:
                logging.debug(f"Nodes in netlist:\n{netlist_graph.nodes}")
                raise KeyError(f"Probe for node {probe[node]} not in netlist")
            dev_node = list(netlist_graph[probe[node]].keys())[0]
            pr_node = probe[node]
        else:
            raise ValueError("Passed probe is not of type dict or Probe")

        netlist_graph.remove_edge(pr_node, dev_node)
        flow_probe = f"vfl_{pr_node}_{p[dev]}"
        new_probe_nodes = [
            # node for probe -> device
            (f"{pr_node}_{dev_node}_pr", {
                'node_type': 'connection',
                'chem_wire': pr_node}),
            # node for
            (f"{flow_probe}", {
                'node_type': 'flow_probe',
                'device': dev_node,
                'param': {'': '0'}})
        ]
        # add edges to graph
        new_es = []
        # do we know what port this is connected to?
        new_es.append((new_probe_nodes[0][0], dev_node))
        new_es.append((new_probe_nodes[0][0], new_probe_nodes[1][0]))
        new_es.append((new_probe_nodes[1][0], pr_node))

        netlist_graph.add_nodes_from(new_probe_nodes)
        netlist_graph.add_edges_from(new_es)

        # do I need to return the probe list?
        if probe_type == "flow":
            probe_list.append(f'I({flow_probe})')
        elif probe_type == "pressure":
            probe_list.append(f'V({p[node]}_{p[dev]}_pr)')
        elif probe_type == "concentration":
            probe_list.append(f'V({pr_node}_{dev_node}_chem)')

    def swap_port_net(g, dev_n, curr_n, new_n):
        NODE_NAMES = [
            'in_fluid',
            'out_fluid',
            'a_fluid',
            'b_fluid',
            'out_fluid'
        ]
        for nn in NODE_NAMES:
            if nn in g.nodes[dev_n] and \
                    g.nodes[dev_n][nn] == curr_n:
                g.nodes[dev_n][nn] = new_n

    def check_probe_node_pair(dev_node, probe_node):
        if (dev_node, probe_node) not in netlist_graph.edges:
            raise KeyError(f"Device probe pair not in netlist, adj dev nodes {dev_node}:{netlist_graph[dev_node]} " +
                           f"adj probe nodes {probe_node}: {netlist_graph}")

    # start function ---------------------------------------

    if 'pressure' in probes:
        # TODO add dev to pressure probe call
        for p in probes['pressure']:
            if isinstance(p, SimulationXyce.SimulationXyce.Probe):
                dev_node = list(netlist_graph[p.getNode()].keys())[0]
                probe_list.append({
                    "probe": "pressure_probe",
                    "print": f'V({p.getNode()}_{dev_node})'
                })
            else:
                dev_node = list(netlist_graph[p[node]].keys())[0]
                probe_list.append({
                    "probe": "pressure_probe",
                    "print": f'V({p[node]}_{dev_node})'
                })

    if 'flow' in probes:
        for p in probes['flow']:
            if isinstance(p, SimulationXyce.SimulationXyce.Probe):
                if p.getNode() not in netlist_graph.nodes:
                    logging.debug(f"Nodes in netlist:\n{netlist_graph.nodes}")
                    raise KeyError(
                        f"Probe for node {p.getNode()} not in netlist")
                try:
                    dev_node = list(netlist_graph[p.getNode()].keys())[0]
                except IndexError:
                    raise IndexError(
                        f"Flow probe error: Not able to find device {list(netlist_graph[p.getNode()].keys())} for node {p.getNode()}")
                pr_node = p.getNode()
            else:
                if p[node] not in netlist_graph.nodes:
                    logging.debug(f"Nodes in netlist:\n{netlist_graph.nodes}")
                    raise KeyError(f"Probe for node {p[node]} not in netlist")
                dev_node = list(netlist_graph[p[node]].keys())[0]
                pr_node = p[node]

            check_probe_node_pair(dev_node, pr_node)
            print(f"Adding flow probe at: {pr_node}, dev: {dev_node}")
            flow_probe = f"vfl_{pr_node}_{dev_node}"
            netlist_graph.edges[(pr_node, dev_node)]["flow_probe"] = flow_probe
            probe_list.append({
                "probe": "flow_probe",
                "name": flow_probe,
                "edge": (dev_node, pr_node),
                "print": f'I({flow_probe})'
            })

    if 'pressureNode' in probes:
        for p in probes['pressureNode']:
            if isinstance(p, SimulationXyce.SimulationXyce.Probe):
                if p.getNode() not in netlist_graph.nodes:
                    logging.debug(f"Nodes in netlist:\n{netlist_graph.nodes}")
                    raise KeyError(
                        f"Probe for node {p.getNode()} not in netlist")
                dev_node = list(netlist_graph[p.getNode()].keys())[0]
                pr_node = p.getNode()
            else:
                if p[node] not in netlist_graph.nodes:
                    logging.debug(f"Nodes in netlist:\n{netlist_graph.nodes}")
                    raise KeyError(f"Probe for node {p[node]} not in netlist")
                dev_node = list(netlist_graph[p[node]].keys())[0]
                pr_node = p[node]

            check_probe_node_pair(dev_node, pr_node)
            pressure_probe = f'vpr_{pr_node}_{dev_node}'
            pressure_probe_nd = f'{pr_node}_{dev_node}_comp'
            netlist_graph.edges[(dev_node, pr_node)
                                ]["pressure_probe"] = pressure_probe

            probe_list.append({
                "probe": "pressure_probe",
                "name": pressure_probe,
                "edge": (dev_node, pr_node),
                "print": f'V({pressure_probe_nd})'
            })

    # concentration probes are assumed (<connect_name>_chem)
    if "concentration" in probes and len(probes['concentration']) > 0:
        assumed_sim_type = "chem"
        for p in probes["concentration"]:

            #print(list(netlist_graph.nodes))
            #print(list(netlist_graph.edges))
            if isinstance(p, SimulationXyce.SimulationXyce.Probe):
                if p.getNode() not in netlist_graph.nodes:
                    logging.debug(f"Nodes in netlist:\n{netlist_graph.nodes}")
                    raise KeyError(
                        f"Probe for node {p.getNode()} not in netlist")
                dev_node = list(netlist_graph[p.getNode()].keys())[0]
                pr_node = p.getNode()
            else:
                if p[node] not in netlist_graph.nodes:
                    logging.debug(f"Nodes in netlist:\n{netlist_graph.nodes}")
                    raise KeyError(f"Probe for node {p[node]} not in netlist")
                dev_node = list(netlist_graph[p[node]].keys())[0]
                pr_node = p[node]

            check_probe_node_pair(dev_node, pr_node)
            # check for existing probes
            if f'V({pr_node}_{dev_node}_chem)' not in [p_pr['print'] for p_pr in probe_list]:
                dev_node = list(netlist_graph[pr_node].keys())[0]
                probe_list.append({
                    "probe": "chem_probe",
                    "print": f'V({pr_node}_{dev_node}_chem)'
                })

    if 'concentrationNode' in probes and len(probes['concentrationNode']) > 0:
        assumed_sim_type = "chem"
        for p in probes['concentrationNode']:
            # explicit chem node dev
            if isinstance(p, SimulationXyce.SimulationXyce.Probe):
                if p.getNode() not in netlist_graph.nodes:
                    logging.debug(f"Nodes in netlist:\n{netlist_graph.nodes}")
                    raise KeyError(
                        f"Probe for node {p.getNode()} not in netlist")
                pr_node = p.getNode()
                dev_node = p.getDevice()
            else:  # is dictionary
                pr_node = p[node]
                dev_node = p[dev]

            check_probe_node_pair(dev_node, pr_node)
            if "chem_probe" not in netlist_graph.nodes[dev_node]:
                # netlist_graph.nodes[dev_node]["chem_probe"] = []
                netlist_graph.edges[(dev_node, pr_node)]["chem_probe"] = []

            if isinstance(p, SimulationXyce.SimulationXyce.Probe):
                chem_probe = f'V({p.getNode()}_{p.getDevice()}_comp_chem)'
            else:
                chem_probe = f'V({p[node]}_{p[dev]}_comp_chem)'
            # handled by downstream instructions
            # netlist_graph.nodes[dev_node]["chem_probe"].append([chem_probe])
            if chem_probe not in netlist_graph.edges[(dev_node, pr_node)]['chem_probe']:
                netlist_graph.edges[(dev_node, pr_node)
                                    ]["chem_probe"].append([chem_probe])
                # same as if in list
            if chem_probe not in [p_pr['print'] for p_pr in probe_list]:
                probe_list.append({
                    "probe": "chem_probe",
                    "name": f"vch_{dev_node}_{pr_node}",
                    "edge": (dev_node, pr_node),
                    "print": chem_probe
                })


    if 'pressure' in probes:
        # TODO add dev to pressure probe call
        for p in probes['pressure']:
            if isinstance(p, SimulationXyce.SimulationXyce.Probe):
                dev_node = list(netlist_graph[p.getNode()].keys())[0]
                probe_list.append({
                    "probe": "temperature_probe",
                    "print": f'V({p.getNode()}_{dev_node}_heat)'
                })
            else:
                dev_node = list(netlist_graph[p[node]].keys())[0]
                probe_list.append({
                    "probe": "temperature_probe",
                    "print": f'V({p[node]}_{dev_node}_heat)'
                })

    # temperature probes are assumed (<connect_name>_heat)
    if "temperature" in probes and (len(probes['temperature']) > 0):
        assumed_sim_type = "heat"
        for p in probes["temperature"]:

            #print(list(netlist_graph.nodes))
            #print(list(netlist_graph.edges))
            if isinstance(p, SimulationXyce.SimulationXyce.Probe):
                if p.getNode() not in netlist_graph.nodes:
                    logging.debug(f"Nodes in netlist:\n{netlist_graph.nodes}")
                    print(f"Nodes in netlist:\n{netlist_graph.nodes}")
                    raise KeyError(
                        f"Probe for node {p.getNode()} not in netlist")
                dev_node = list(netlist_graph[p.getNode()].keys())[0]
                pr_node = p.getNode()
            else:
                if p[node] not in netlist_graph.nodes:
                    logging.debug(f"Nodes in netlist:\n{netlist_graph.nodes}")
                    raise KeyError(f"Probe for node {p[node]} not in netlist")
                dev_node = list(netlist_graph[p[node]].keys())[0]
                pr_node = p[node]

            check_probe_node_pair(dev_node, pr_node)
            # check for existing probes
            if f'V({pr_node}_{dev_node}_heat)' not in [p_pr['print'] for p_pr in probe_list]:
                dev_node = list(netlist_graph[pr_node].keys())[0]
                probe_list.append({
                    "probe": "temp_probe",
                    "print": f'V({pr_node}_{dev_node}_heat)'
                })

    if ('temperatureNode' in probes) and (len(probes['temperatureNode']) > 0):
        assumed_sim_type = "heat"
        for p in probes['temperatureNode']:
            # explicit chem node dev
            if isinstance(p, SimulationXyce.SimulationXyce.Probe):
                if p.getNode() not in netlist_graph.nodes:
                    logging.debug(f"Nodes in netlist:\n{netlist_graph.nodes}")
                    raise KeyError(
                        f"Probe for node {p.getNode()} not in netlist")
                pr_node = p.getNode()
                dev_node = p.getDevice()
            else:  # is dictionary
                pr_node = p[node]
                dev_node = p[dev]

            check_probe_node_pair(dev_node, pr_node)
            if "temp_probe" not in netlist_graph.nodes[dev_node]:
                # netlist_graph.nodes[dev_node]["chem_probe"] = []
                netlist_graph.edges[(dev_node, pr_node)]["temp_probe"] = []

            if isinstance(p, SimulationXyce.SimulationXyce.Probe):
                temp_probe = f'V({p.getNode()}_{p.getDevice()}_comp_heat)'
            else:
                temp_probe = f'V({p[node]}_{p[dev]}_comp_heat)'
            # handled by downstream instructions
            # netlist_graph.nodes[dev_node]["chem_probe"].append([chem_probe])
            if temp_probe not in netlist_graph.edges[(dev_node, pr_node)]['temp_probe']:
                netlist_graph.edges[(dev_node, pr_node)
                                    ]["temp_probe"].append([temp_probe])
                # same as if in list
            if temp_probe not in [p_pr['print'] for p_pr in probe_list]:
                probe_list.append({
                    "probe": "temp_probe",
                    "name": f"vth_{dev_node}_{pr_node}",
                    "edge": (dev_node, pr_node),
                    "print": temp_probe
                })

    return probe_list, netlist_graph, assumed_sim_type
