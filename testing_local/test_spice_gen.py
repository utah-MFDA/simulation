def test_add_probes():
    import sys, os
    from writeSpice import add_probes_to_device

    sys.path.insert(
        0, os.path.dirname(os.path.realpath(__file__)) + "/../verilog_2_NX/"
    )
    from Verilog2NX import get_modules, visual_graph

    probes = {}
    probes["pressure"] = [{"node": "connect1"}]
    probes["pressureNode"] = [{"node": "connect1", "device": "serp1"}]
    probes["pressureNode"] = [{"node": "connect1", "device": "serp2"}]
    probes["flow"] = [{"node": "connect1", "device": "serp1"}]
    probes["concentration"] = [{"node": "connect1"}]

    verilog_file = "testing_local/smart_toilet_test_config/smart_toilet.v"

    netlist_dict, netlist_graph = get_modules(in_v=verilog_file, visual=False)

    out_probes, netlist_graph_out = add_probes_to_device(
        probes, netlist_graph["smart_toilet"]["netlist"]
    )

    print(out_probes)

    # visual_graph(netlist_graph['smart_toilet']['netlist'])


def test_source_list_gen():
    import sys, os
    from writeSpice import add_probes_to_device, generate_source_list
    from SimulationXyce import SimulationXyce

    sys.path.insert(
        0, os.path.dirname(os.path.realpath(__file__)) + "/../verilog_2_NX/"
    )
    from Verilog2NX import get_modules, visual_graph

    verilog_file = "testing_local/smart_toilet_test_config/smart_toilet.v"
    netlist_dict, netlist_graph = get_modules(in_v=verilog_file, visual=False)

    config_file = "testing_local/smart_toilet_test_config/simulation.config"

    Xcl = SimulationXyce()
    Xcl.parse_config_file(config_file)

    dev_lines, chem_args = generate_source_list(Xcl)

    print("device lines:")
    print(dev_lines)


def test_source_list_gen():
    import sys, os
    from writeSpice import add_probes_to_device, generate_source_list
    from SimulationXyce import SimulationXyce

    sys.path.insert(
        0, os.path.dirname(os.path.realpath(__file__)) + "/../verilog_2_NX/"
    )
    from Verilog2NX import get_modules, visual_graph

    verilog_file = "testing_local/smart_toilet_test_config/smart_toilet.v"
    netlist_dict, netlist_graph = get_modules(in_v=verilog_file, visual=False)

    config_file = "testing_local/smart_toilet_test_config/simulation.config"

    Xcl = SimulationXyce()
    Xcl.parse_config_file(config_file)

    dev_lines, chem_args = generate_source_list(Xcl, has_chem=True)

    print("device lines:")
    print(dev_lines)

    print("chem lines:")
    print(chem_args)


def test_convert_netlist():
    import sys, os
    from writeSpice import (
        add_probes_to_device,
        generate_source_list,
        write_spice_file,
        convert_nodes_2_numbers_xyce,
        generate_time_lines,
        generate_spice_nets,
    )
    from SimulationXyce import SimulationXyce

    sys.path.insert(
        0, os.path.dirname(os.path.realpath(__file__)) + "/../verilog_2_NX/"
    )

    verilog_file = "testing_local/smart_toilet_test_config/smart_toilet.v"
    config_file = "testing_local/smart_toilet_test_config/simulation.config"
    length_file = "testing_local/smart_toilet_test_config/smart_toilet_lengths.xlsx"

    from Verilog2NX import get_modules, visual_graph

    netlist_dict, netlist_graph = get_modules(in_v=verilog_file, visual=False)

    generate_spice_nets(
        netlist_graph["smart_toilet"]["netlist"], length_list=length_file
    )

    # fmt:off
    print("Netlist edges:")
    for e in netlist_graph["smart_toilet"]["netlist"].edges:
        print(e)
        print(netlist_graph["smart_toilet"]["netlist"].get_edge_data(e[0], e[1]))
        print(netlist_graph["smart_toilet"]["netlist"].get_edge_data(e[0], e[1])['fl_net'])
        # print(netlist_graph["smart_toilet"]["netlist"].edges(e)['fl_net'])
    for n in netlist_graph["smart_toilet"]["netlist"].nodes:
        print(n)
        print(netlist_graph["smart_toilet"]["netlist"].nodes[n])
    # fmt:on


def test_merge_with_wirelength_graph():
    import sys, os
    import json
    from networkx.readwrite import json_graph
    import networkx as nx
    import matplotlib.pyplot as plt
    from writeSpice import (
        add_probes_to_device,
        generate_source_list,
        write_spice_file,
        convert_nodes_2_numbers_xyce,
        generate_time_lines,
        generate_spice_nets,
        merge_wl_net,
        get_length_list
    )
    from SimulationXyce import SimulationXyce

    draw = False
    #draw = True

    sys.path.insert(
        0, os.path.dirname(os.path.realpath(__file__)) + "/../verilog_2_NX/"
    )

    verilog_file = "testing_local/grad_test/grad_gen_3.v"
    config_file = "testing_local/smart_toilet_test_config/simulation.config"
    length_file = "testing_local/grad_test/test_3_length.csv"
    wl_graph_f = "testing_local/grad_test/test_3_route_nets.json"

    from Verilog2NX import get_modules, visual_graph

    netlist_dict, netlist_graph = get_modules(in_v=verilog_file, visual=False)

    in_netlist = netlist_graph["grad_gen_3"]["netlist"]

    if draw:
        nx.draw_spring(in_netlist, with_labels=True)
        plt.show()
    # generate_spice_nets(
    # netlist_graph["smart_toilet"]["netlist"], length_list=length_file
    # )

    wl_f = get_length_list(length_file)

    # wl_graph_f = length_file.replace("_length.csv", "_route_nets.json")
    wl_graph = {}
    with open(wl_graph_f, "r") as f:
        json_f = json.load(f)
        for r in json_f.items():
            new_graph = json_graph.node_link_graph(r[1])
            print(r[0], len(new_graph))
            if len(new_graph.nodes) > 1:
                wl_graph[r[0]] = json_graph.node_link_graph(r[1])
        for wl_n in wl_graph.items():
            in_netlist = merge_wl_net(in_netlist, wl_n[1], wl_n[0], wl_file=wl_f)

    # fmt:off
    print("Netlist nodes:")
    for n in in_netlist.nodes:
        print(n)
        print(in_netlist.nodes[n])
    print("Netlist edges:")
    for e in in_netlist.edges:
        print(e)
        print(in_netlist.get_edge_data(e[0], e[1]))
        # print(netlist_graph["smart_toilet"]["netlist"].edges(e)['fl_net'])
    # for n in netlist_graph["smart_toilet"]["netlist"].nodes:
    # print(n)
    # print(netlist_graph["smart_toilet"]["netlist"].nodes[n])
    # fmt:on

def test_with_grad_3():
    import sys, os
    import json
    from networkx.readwrite import json_graph
    import networkx as nx
    import matplotlib.pyplot as plt
    from writeSpice import (
        add_probes_to_device,
        generate_source_list,
        write_spice_file,
        convert_nodes_2_numbers_xyce,
        generate_time_lines,
        generate_spice_nets,
        merge_wl_net,
        get_length_list,
        write_components_from_graph
    )
    from SimulationXyce import SimulationXyce


    os.environ['XYCE_WL_GRAPH'] = ''
    #draw = True

    sys.path.insert(
        0, os.path.dirname(os.path.realpath(__file__)) + "/../verilog_2_NX/"
    )

    verilog_file = "testing_local/grad_test/grad_gen_3.v"
    config_file = "testing_local/smart_toilet_test_config/simulation.config"
    length_file = "testing_local/grad_test/test_3_length.csv"
    wl_graph_f = "testing_local/grad_test/test_3_route_nets.json"

    out_file = ".test_out/out_spice_grad3.cir.str"

    from Verilog2NX import get_modules, visual_graph

    netlist_dict, netlist_graph = get_modules(in_v=verilog_file, visual=False)

    in_netlist = netlist_graph["grad_gen_3"]["netlist"]

    #wl_f = get_length_list(length_file)

    in_netlist = generate_spice_nets(
        in_netlist, length_list=length_file
    )
    # fmt:off
    print("Netlist nodes:")
    for n in in_netlist.nodes:
        print(n)
        print(in_netlist.nodes[n])
    print("Netlist edges:")
    for e in in_netlist.edges:
        print(e)
        print(in_netlist.get_edge_data(e[0], e[1]))
    # fmt:on

    write_components_from_graph(in_netlist, out_file)


def test_write_spice_grad3():
    import sys, os
    import json
    from networkx.readwrite import json_graph
    import networkx as nx
    import matplotlib.pyplot as plt
    from writeSpice import (
        add_probes_to_device,
        generate_source_list,
        write_spice_file,
        convert_nodes_2_numbers_xyce,
        generate_time_lines,
        generate_spice_nets,
        merge_wl_net,
        get_length_list,
        write_components_from_graph
    )
    from SimulationXyce import SimulationXyce


    os.environ['XYCE_WL_GRAPH'] = ''
    #draw = True

    sys.path.insert(
        0, os.path.dirname(os.path.realpath(__file__)) + "/../verilog_2_NX/"
    )

    verilog_file = "testing_local/grad_test/grad_gen_3.v"
    config_file = "testing_local/grad_test/simulation.config"
    length_file = "testing_local/grad_test/test_3_length.csv"
    wl_graph_f = "testing_local/grad_test/test_3_route_nets.json"

    out_file = ".test_out/out_spice_grad3.cir.str"

    from Verilog2NX import get_modules, visual_graph

    netlist_dict, netlist_graph = get_modules(in_v=verilog_file, visual=False)

    in_netlist = netlist_graph["grad_gen_3"]["netlist"]

    Xcl = SimulationXyce()
    Xcl.parse_config_file(config_file)
    dev_lines, chem_args = generate_source_list(Xcl, has_chem=True)
    sim_lines = generate_time_lines(Xcl)

    write_spice_file(
        in_netlist,
        probes_list={},
        source_lines=dev_lines,
        length_list=length_file,
        wl_graph=wl_graph_f,
        sims_time_lines=sim_lines,
        sim_type="transient",
        out_file=".test_out/out_spice_grad3_write.cir",
    )

def test_write_spice_grad3_chem():
    import sys, os
    import json
    from networkx.readwrite import json_graph
    import networkx as nx
    import matplotlib.pyplot as plt
    from writeSpice import (
        add_probes_to_device,
        generate_source_list,
        write_spice_file,
        convert_nodes_2_numbers_xyce,
        generate_time_lines,
        generate_spice_nets,
        merge_wl_net,
        get_length_list,
        write_components_from_graph
    )
    from SimulationXyce import SimulationXyce


    os.environ['XYCE_WL_GRAPH'] = ''
    #draw = True

    sys.path.insert(
        0, os.path.dirname(os.path.realpath(__file__)) + "/../verilog_2_NX/"
    )

    verilog_file = "testing_local/grad_test/grad_gen_3.v"
    config_file = "testing_local/grad_test/simulation_chem.config"
    length_file = "testing_local/grad_test/test_3_length.csv"
    wl_graph_f = "testing_local/grad_test/test_3_route_nets.json"

    out_file = ".test_out/out_spice_grad3.cir.str"

    from Verilog2NX import get_modules, visual_graph

    netlist_dict, netlist_graph = get_modules(in_v=verilog_file, visual=False)

    in_netlist = netlist_graph["grad_gen_3"]["netlist"]

    Xcl = SimulationXyce()
    Xcl.parse_config_file(config_file)
    dev_lines, chem_args = generate_source_list(Xcl, has_chem=True)
    sim_lines = generate_time_lines(Xcl)

    probes = {}
    probes["concentration"] = [{"node": "connect1"}] #, {"node": "connect2"}]
    out_probes, netlist_graph_out = add_probes_to_device(
        probes, in_netlist
    )

    draw = False
    #draw = True

    if draw:
        nx.draw_spring(in_netlist, with_labels=True)
        plt.show()

    write_spice_file(
        in_netlist,
        probes_list=out_probes,
        source_lines=dev_lines,
        length_list=length_file,
        wl_graph=wl_graph_f,
        sims_time_lines=sim_lines,
        sim_type="transient",
        out_file=".test_out/out_spice_grad3_write_chem.cir",
    )

def test_write_spice_str_0():
    import sys, os
    from writeSpice import (
        add_probes_to_device,
        generate_source_list,
        write_spice_file,
        convert_nodes_2_numbers_xyce,
        generate_time_lines,
    )
    from SimulationXyce import SimulationXyce

    sys.path.insert(
        0, os.path.dirname(os.path.realpath(__file__)) + "/../verilog_2_NX/"
    )
    from Verilog2NX import get_modules, visual_graph

    verilog_file = "testing_local/smart_toilet_test_config/smart_toilet.v"
    config_file = "testing_local/smart_toilet_test_config/simulation.config"
    length_file = "testing_local/smart_toilet_test_config/smart_toilet_lengths.xlsx"

    probes = {}
    probes["pressure"] = [{"node": "connect1"}]
    # probes['pressureNode'] = [{'node':'connect1', 'device':'serp1'}]
    # probes['pressureNode'] = [{'node':'connect1', 'device':'serp2'}]
    # probes['flow'] = [{'node':'connect1', 'device':'serp1'}]
    probes["concentration"] = [{"node": "connect1"}]

    netlist_dict, netlist_graph = get_modules(in_v=verilog_file, visual=False)

    out_probes, netlist_graph_out = add_probes_to_device(
        probes, netlist_graph["smart_toilet"]["netlist"]
    )

    Xcl = SimulationXyce()
    Xcl.parse_config_file(config_file)

    dev_lines, chem_args = generate_source_list(Xcl, has_chem=True)

    sim_lines = generate_time_lines(Xcl)

    write_spice_file(
        netlist_graph["smart_toilet"]["netlist"],
        probes_list=out_probes,
        source_lines=dev_lines,
        length_list=length_file,
        sims_time_lines=sim_lines,
        sim_type="transient",
        out_file=".test_out/out_spice_0.cir",
    )

    out_spice = ".test_out/out_spice_0_.cir.str"

    convert_nodes_2_numbers_xyce(out_spice)


def test_write_spice_str_1():
    import sys, os
    import networkx as nx
    import matplotlib.pyplot as plt
    from writeSpice import (
        add_probes_to_device,
        generate_source_list,
        write_spice_file,
        convert_nodes_2_numbers_xyce,
        generate_time_lines,
    )
    from SimulationXyce import SimulationXyce

    sys.path.insert(
        0, os.path.dirname(os.path.realpath(__file__)) + "/../verilog_2_NX/"
    )
    from Verilog2NX import get_modules, visual_graph

    verilog_file = "testing_local/smart_toilet_test_config/smart_toilet.v"
    config_file = "testing_local/smart_toilet_test_config/simulation.config"
    length_file = "testing_local/smart_toilet_test_config/smart_toilet_lengths.xlsx"

    probes = {}
    probes["pressure"] = [{"node": "connect1"}]
    probes["pressureNode"] = [{"node": "connect1", "device": "serp1"}]
    probes["pressureNode"] = [{"node": "connect1", "device": "serp2"}]
    probes["flow"] = [{"node": "connect1", "device": "serp1"}]
    probes["concentration"] = [{"node": "connect1"}]

    netlist_dict, netlist_graph = get_modules(in_v=verilog_file, visual=False)
    in_netlist = netlist_graph["smart_toilet"]["netlist"]

    out_probes, netlist_graph_out = add_probes_to_device(
        probes, in_netlist
    )

    Xcl = SimulationXyce()
    Xcl.parse_config_file(config_file)

    dev_lines, chem_args = generate_source_list(Xcl, has_chem=True)

    sim_lines = generate_time_lines(Xcl)

    draw = False
    draw = True

    if draw:
        nx.draw_spring(in_netlist, with_labels=True)
        plt.show()

    write_spice_file(
        in_netlist,
        probes_list=out_probes,
        source_lines=dev_lines,
        length_list=length_file,
        sims_time_lines=sim_lines,
        sim_type="transient",
        out_file=".test_out/out_spice_1.cir",
    )

    out_spice = ".test_out/out_spice_1_.cir.str"

    convert_nodes_2_numbers_xyce(out_spice)


def test_write_spice_str_2():
    import sys, os
    from writeSpice import (
        add_probes_to_device,
        generate_source_list,
        write_spice_file,
        convert_nodes_2_numbers_xyce,
        generate_time_lines,
    )
    from SimulationXyce import SimulationXyce

    sys.path.insert(
        0, os.path.dirname(os.path.realpath(__file__)) + "/../verilog_2_NX/"
    )
    from Verilog2NX import get_modules, visual_graph

    verilog_file = "testing_local/smart_toilet_test_config/smart_toilet.v"
    config_file = "testing_local/smart_toilet_test_config/simulation.config"
    length_file = "testing_local/smart_toilet_test_config/smart_toilet_lengths.xlsx"

    probes = {}
    probes["pressure"] = [{"node": "connect1"}]
    probes["flow"] = [{"node": "connect1", "device": "serp1"}]
    probes["concentration"] = [{"node": "connect1"}]

    netlist_dict, netlist_graph = get_modules(in_v=verilog_file, visual=False)

    out_probes, netlist_graph_out = add_probes_to_device(
        probes, netlist_graph["smart_toilet"]["netlist"]
    )

    Xcl = SimulationXyce()
    Xcl.parse_config_file(config_file)

    dev_lines, chem_args = generate_source_list(Xcl, has_chem=True)

    sim_lines = generate_time_lines(Xcl)

    write_spice_file(
        netlist_graph["smart_toilet"]["netlist"],
        probes_list=out_probes,
        source_lines=dev_lines,
        length_list=length_file,
        sims_time_lines=sim_lines,
        sim_type="transient",
        out_file=".test_out/out_spice_2.cir",
    )

    out_spice = ".test_out/out_spice_2_.cir.str"

    convert_nodes_2_numbers_xyce(out_spice)


def test_write_spice_str_3():
    import sys, os
    from writeSpice import (
        add_probes_to_device,
        generate_source_list,
        write_spice_file,
        convert_nodes_2_numbers_xyce,
        generate_time_lines,
    )
    from SimulationXyce import SimulationXyce

    sys.path.insert(
        0, os.path.dirname(os.path.realpath(__file__)) + "/../verilog_2_NX/"
    )
    from Verilog2NX import get_modules, visual_graph

    verilog_file = "testing_local/smart_toilet_test_config/smart_toilet.v"
    config_file = "testing_local/smart_toilet_test_config/simulation.config"
    length_file = "testing_local/smart_toilet_test_config/smart_toilet_lengths.xlsx"

    probes = {}
    probes["pressure"] = [{"node": "connect1"}]
    probes["flow"] = [{"node": "connect1", "device": "serp1"}]
    probes["concentration"] = [{"node": "connect1"}]

    netlist_dict, netlist_graph = get_modules(in_v=verilog_file, visual=False)

    out_probes, netlist_graph_out = add_probes_to_device(
        probes, netlist_graph["smart_toilet"]["netlist"]
    )

    Xcl = SimulationXyce()
    Xcl.parse_config_file(config_file)

    dev_lines, chem_args = generate_source_list(Xcl, has_chem=True)

    print("chem lines:")
    print(chem_args)
    print(dev_lines)

    sim_lines = generate_time_lines(Xcl)

    write_spice_file(
        netlist_graph["smart_toilet"]["netlist"],
        probes_list=out_probes,
        source_lines=dev_lines,
        length_list=length_file,
        chem_list=chem_args,
        sims_time_lines=sim_lines,
        sim_type="transient",
        out_file=".test_out/out_spice_3.cir",
    )

    out_spice = ".test_out/out_spice_3_H2O.cir.str"

    convert_nodes_2_numbers_xyce(out_spice)


def test_write_spice_str_4():
    import sys, os
    from writeSpice import (
        add_probes_to_device,
        generate_source_list,
        write_spice_file,
        convert_nodes_2_numbers_xyce,
        generate_time_lines,
    )
    from SimulationXyce import SimulationXyce

    sys.path.insert(
        0, os.path.dirname(os.path.realpath(__file__)) + "/../verilog_2_NX/"
    )
    from Verilog2NX import get_modules, visual_graph

    verilog_file = "testing_local/smart_toilet_test_config/smart_toilet.v"
    config_file = "testing_local/smart_toilet_test_config/simulation.config"
    length_file = "testing_local/smart_toilet_test_config/smart_toilet_lengths.xlsx"

    probes = {}
    # probes['pressure'] = [{'node':'connect1'}]
    # probes['flow'] = [{'node':'connect1', 'device':'serp1'}]
    probes["concentrationNode"] = [{"node": "connect1", "device": "serp1"}]

    netlist_dict, netlist_graph = get_modules(in_v=verilog_file, visual=False)

    out_probes, netlist_graph_out = add_probes_to_device(
        probes, netlist_graph["smart_toilet"]["netlist"]
    )

    Xcl = SimulationXyce()
    Xcl.parse_config_file(config_file)

    dev_lines, chem_args = generate_source_list(Xcl, has_chem=True)

    print("chem lines:")
    print(chem_args)
    print(dev_lines)

    sim_lines = generate_time_lines(Xcl)

    write_spice_file(
        netlist_graph["smart_toilet"]["netlist"],
        probes_list=out_probes,
        source_lines=dev_lines,
        length_list=length_file,
        chem_list=chem_args,
        sims_time_lines=sim_lines,
        sim_type="transient",
        out_file=".test_out/out_spice_4.cir",
    )

    out_spice = ".test_out/out_spice_4_H2O.cir.str"

    convert_nodes_2_numbers_xyce(out_spice)


def test_write_spice_str_5():
    import sys, os
    from writeSpice import (
        add_probes_to_device,
        generate_source_list,
        write_spice_file,
        convert_nodes_2_numbers_xyce,
        generate_time_lines,
    )
    from SimulationXyce import SimulationXyce

    sys.path.insert(
        0, os.path.dirname(os.path.realpath(__file__)) + "/../verilog_2_NX/"
    )
    from Verilog2NX import get_modules, visual_graph

    verilog_file = "testing_local/two_out_cnode/smart_toilet.v"
    config_file = "testing_local/two_out_cnode/simulation.config"
    length_file = "testing_local/two_out_cnode/smart_toilet_lengths.xlsx"

    probes = {}
    # probes['pressure'] = [{'node':'connect1'}]
    # probes['flow'] = [{'node':'connect1', 'device':'serp1'}]
    probes["concentrationNode"] = [{"node": "out", "device": "serp11"}]
    probes["concentrationNode"] = [{"node": "out", "device": "serp5"}]

    netlist_dict, netlist_graph = get_modules(in_v=verilog_file, visual=False)

    out_probes, netlist_graph_out = add_probes_to_device(
        probes, netlist_graph["smart_toilet"]["netlist"]
    )

    Xcl = SimulationXyce()
    Xcl.parse_config_file(config_file)

    dev_lines, chem_args = generate_source_list(Xcl, has_chem=True)

    print("chem lines:")
    print(chem_args)
    print(dev_lines)

    sim_lines = generate_time_lines(Xcl)

    write_spice_file(
        netlist_graph["smart_toilet"]["netlist"],
        probes_list=out_probes,
        source_lines=dev_lines,
        length_list=length_file,
        chem_list=chem_args,
        sims_time_lines=sim_lines,
        sim_type="transient",
        out_file=".test_out/out_spice_5.cir",
    )

    out_spice = ".test_out/out_spice_5_H2O.cir.str"

    convert_nodes_2_numbers_xyce(out_spice)


def test_write_spice_main():

    from writeSpice import generate_cir_main

    verilog_file = "testing_local/smart_toilet_test_config/smart_toilet.v"
    config_file = "testing_local/smart_toilet_test_config/simulation.config"
    length_file = "testing_local/smart_toilet_test_config/smart_toilet_lengths.xlsx"

    generate_cir_main(
        design="smart_toilet",
        verilog_file=verilog_file,
        config_file=config_file,
        length_file=length_file,
        out_file="results/testing/out_spice_main_1",
    )


def test_write_spice_main_pcell():

    from writeSpice import generate_cir_main

    verilog_file = "testing_local/smart_toilet_test_config_pcell/smart_toilet.v"
    config_file = "testing_local/smart_toilet_test_config_pcell/simulation.config"
    length_file = (
        "testing_local/smart_toilet_test_config_pcell/smart_toilet_lengths.xlsx"
    )
    pcell_file = "testing_local/smart_toilet_test_config_pcell/pcell_out_xyce"

    generate_cir_main(
        design="smart_toilet",
        verilog_file=verilog_file,
        config_file=config_file,
        length_file=length_file,
        out_file="results/testing/out_spice_main_1p",
        pcell_file=pcell_file,
    )
