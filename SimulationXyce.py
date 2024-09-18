import yaml
import json5


class SimulationXyce:

    class Node:
        def __init__(self, name, args):
            self.name = name
            self.args = args

        def getName(self):
            return self.name

        def getArgs(self):
            return self.args

    class Inlet(Node):
        def __init__(self, name, args):
            super.__init__(name, args)

    class Outlet(Node):
        def __init__(self, name, args):
            super.__init__(name, args)

    class Eval:
        def __init__(self, prop, node, value=None, time=None, device=None):
            #self.chem  = chem
            self.prop  = prop
            self.node  = node
            self.value = value
            #if time is not None:
            self.time  = time
            self.dev   = device

        def getNode(self):
            return self.node

        def getValue(self):
            return self.value

        def getChem(self):
            if self.prop not in ['pressure', 'flow']:
                return self.prop
            else:
                print(f"Chemical is of type: {self.prop}")
                return None

        #TODO if time = None
        def getTime(self):
            return self.time

        def getDev(self):
            return self.dev

    # this will need some more generic definitions
    class Dev:
        def __init__(self, node, dev_type, args, is_grounded=True):
            self.type = dev_type
            self.node = node
            self.is_grounded = is_grounded
            self.args = args

        def getType(self):
            return self.type

        def getNode(self):
            return self.node

        def getArgs(self):
            return self.args

        def addArgument(self, arg):
            self.args.append(arg)

    class ChemInput:
        def __init__(self, chem, node, in_value):
            self.chem = chem
            self.node = node
            self.value=in_value

        def getInValue(self):
            return self.value

        def getNode(self):
            return self.node

        def getChem(self):
            return self.chem

    class Probe:
        def __init__(self, probe_type, node, device=None):
            self.probe_type = probe_type
            self.node = node
            self.device = device

        def getNode(self):
            return self.node

        def getProbeType(self):
            return self.probe_type

        def getDevice(self):
            if self.device is None:
                raise ValueError("No device in probe")
            return self.device


    def __init__(self):
        self.netListFiles = []
        self.inlets = {}
        self.eval   = {}
        self.dev    = {}
        self.chem   = {}
        self.times  = {}
        self.probes = {}
        self.probes['pressure'] = []
        self.probes['pressureNode'] = []
        self.probes['flow'] = []
        self.probes['concentration'] = []
        self.probes['concentrationNode'] = []

    def load_analysis_file(self, file, ftype=None):
        if '.' in file.split['/'][-1]:
            extn = file.split['.'][-1]
        else:
            extn = None

        if ftype is None:
            if extn == 'yaml':
                ftype = 'YAML'
            elif ftype in ['json', 'jsonc']:
                ftype = 'JSONC'
            elif extn in ['config', 'conf']:
                ftype = 'CONFIG'
            else:
                ftype = None

        if ftype == 'YAML':
            self.parse_yaml_file(file)
        if ftype == 'JSONC':
            self.parse_jsonc_file(file)
        elif ftype == 'CONFIG':
            self.parse_config_file(file)
        else:  # default parser
            self.parse_config_file(file)


    def parse_config_file(self, file):
        in_conf_f = open(file)
        for l_num, line in enumerate(in_conf_f):
            # remove comments
            if '#' in line:
                line = line.split('#')[0]
            line = ' '.join(line.lstrip().split())  # removes leading and extra WS

            if len(line) == 0:
                continue

            params = line.split(' ')
            key = params[0]

            if key == 'input':
                port = params[1]
                device = params[2]
                dev_params = params[3:]

                self.add_input_device(port, device, dev_params)
                #def __init__(self, node, dev_type, args, is_grounded=True):
                #self.dev[params[1]] = self.Dev(params[1], params[2], params[3:])

            elif key == 'chem':
                solution = params[1]
                in_port  = params[2]
                value    = params[3]

                self.add_solution(solution, in_port, value)

                # if params[2] in self.dev:
                #     self.chem[params[1]] = self.ChemInput(params[1], params[2], params[3])
                #     #if params[1] in self.eval:
                #     #    self.eval[params[1]].append(self.Eval(params[1], params[4], params[5]))
                #     #else:
                #     #    self.eval[params[1]] = [self.Eval(params[1], params[4], params[5])]
                # else:
                #     raise ValueError("Device not created for input: "+params[2]+", line: "+str(l_num)+'\n'+\
                #         "    chem: "+params[1]+', input port: '+params[2]+', '+'Concentration: '+params[3])

            # key for timing
            elif key in ['transient', 'static']:
                self.add_analysis(key, params)
            # elif key == 'transient':
            #     if 'transient' in self.times:
            #         self.times['transient'].append(params)
            #     else:
            #         self.times['transient'] = [params]
            # # untested method
            # # would need to use DC simulations
            # elif key == 'static':
            #     pass

            elif key == 'probe':
                probe_type = params[1]
                if probe_type in ['flow', 'pressureNode', 'concentrationNode']:
                    node = params[3]
                    device = params[2]
                elif probe_type in ['pressure']:
                    node = params[2]
                    device = None
                else:
                    node = None
                    device = None

                self.add_probe(probe_type, node, device)

                # if params[1] == 'pressure':
                #     self.probes['pressure'].append(self.Probe(
                #         'pressure',
                #         node=params[2]))
                # elif params[1] == 'flow':
                #     self.probes['flow'].append(self.Probe(
                #         'flow',
                #         node=params[3],
                #         device=params[2]))
                # elif (len(self.chem) > 0) and params[1] in [ch.getChem() for ch in self.chem.values()]:
                #     self.probes['concentration'].append(self.Probe(
                #         'concentration',
                #         node=params[2]))
                # elif params[1] == "pressureNode":
                #     self.probes['pressureNode'].append(self.Probe(
                #         'pressureNode',
                #         node=params[3],
                #         device=params[2]
                #     ))
                # elif params[1] == "concentrationNode":
                #     self.probes['concentrationNode'].append(self.Probe(
                #         'concentrationNode',
                #         node=params[3],
                #         device=params[2]
                #     ))
                # else:
                #     raise ValueError(f'{params[1]} is not a valid node, use "pressure", "flow", "pressureNode", "concentrationNode" or declare the input chemical before this line. Line number {l_num+1}')

            elif key == 'eval':
                if len(params) == 5:
                    prop  = params[1]
                    time  = params[2]
                    node  = params[3]
                    value = params[4]
                    self.add_eval_node(prop, node, value, time)
                elif len(params) == 6:
                    prop  = params[1]
                    time  = params[2]
                    node  = params[3]
                    dev   = params[4]
                    value = params[5]
                    self.add_eval_node(prop, node, value, time, dev)
                # if params[1] in self.eval:
                #     #Eval def __init__(self, chem, node, value, time=None):
                #     self.eval[params[1]].append(self.Eval(
                #         params[1],
                #         params[3],
                #         self.convert_sufix_number(params[4]),
                #         self.convert_sufix_number(params[2])
                #         ))
                # else:
                #     self.eval[params[1]] = [self.Eval(
                #         params[1],
                #         params[3],
                #         self.convert_sufix_number(params[4]),
                #         self.convert_sufix_number(params[2])
                #         )]
                # self.probes['concentration'].append(self.Probe('concentration', params[3]))

    def parse_jsonc_file(self, analysis_file):
        # dictionaries should load identiacally
        json_str = open(analysis_file, 'r').read()
        in_dict = json5.loads(json_str)
        self.parse_dict_from_file(in_dict)

    def parse_yaml_file(self, analysis_file):
        in_dict = yaml.safe_load(open(analysis_file, 'r'))
        self.parse_dict_from_file(in_dict)

    def parse_dict_from_file(self, in_dict):

        if 'analysis' in in_dict:
            for a in in_dict['analysis']:
                #def add_analysis(self, analysis_type, params):
                self.add_analysis(a['analysis_type'], a['params'])

        if 'inputs' in in_dict:
            for ins in in_dict['inputs'].items():
                # def add_input_device(self, port, device, dev_params):
                self.add_input_device(
                    ins[0],
                    ins[1]['device'],
                    [f'{p[0]}={p[1]}' for p in ins[1]['params'].items()]
                )

        if 'solutions' in in_dict:
            for s in in_dict['solutions'].items():
                # def add_solution(self, solution, port, value, line_num=None):
                self.add_solution(
                    s[0],
                    s[1]['input'],
                    s[1]['concentration']
                )
        if 'probes' in in_dict:
            for pr_type in in_dict['probes'].items():
                # def add_probe(self, probe_type, node, device):
                if isinstance(pr_type[1], list):
                    for pr_node in pr_type[1]:
                        if isinstance(pr_node, str):
                            # defitions are node-device
                            pr_item = pr_node.split('-')
                            if len(pr_item) == 1:
                                self.add_probe(pr_type[0], pr_item[0], None)
                            elif len(pr_item) == 2:
                                self.add_probe(pr_type[0], pr_item[0], pr_item[1])
                            else:
                                raise ValueError('probe definition should be "node-device", no more than one "-" is allowed')
                        elif isinstance(pr_node, dict):
                            if 'device' in pr_node:
                                self.add_probe(pr_type[0], pr_node['node'], pr_node['device'])
                            else:
                                self.add_probe(pr_type[0], pr_node['node'], None)
                        else:
                            ValueError(f"Issue with probe definition in {pr_type[0]}")
        if 'eval' in in_dict:
            for ev in in_dict['eval'].items():
                # def add_eval_node(self, prop, node, value, time):
                if ev[0] in ['pressure', 'flow', 'concentration']:
                    for ev_inst in ev[1].values():
                        ev_time = None
                        if 'time' in ev[1]['time']:
                            ev_time = ev[1]['time']
                        if ev[0] == 'concentration':
                            self.add_eval_node(
                                ev_inst['chemical'],
                                ev_inst['node'],
                                ev_inst['concentration'],
                                ev_time
                            )
                        elif ev[0] == 'flow':
                            self.add_eval_node(
                                ev[0],
                                ev_inst['node'],
                                ev_inst['flow'],
                                ev_time
                            )
                        elif ev[0] == 'pressure':
                            self.add_eval_node(
                                ev[0],
                                ev_inst['node'],
                                ev_inst['pressure'],
                                ev_time
                            )
                # TODO check nodes
                # this requires having loaded the netlist
                else:
                    ev_time = None
                    if 'time' in ev[1]['time']:
                        ev_time = ev[1]['time']
                    if ev[1]['type'] == 'concentration':
                        self.add_eval_node(
                            ev[1]['type'],
                            ev[1]['node'],
                            ev[1]['concentration'],
                            ev_time
                        )
                    elif ev[1]['type'] == 'flow':
                        self.add_eval_node(
                            ev[1]['type'],
                            ev[1]['node'],
                            ev[1]['flow'],
                            ev_time
                        )
                    elif ev[1]['type'] == 'pressure':
                        self.add_eval_node(
                            ev[1]['type'],
                            ev[1]['node'],
                            ev[1]['pressure'],
                            ev_time
                        )


    def parse_eval_file(self, ev_file):

        # reset eval list
        self.eval   = {}

        f = open(ev_file, 'r')

        for line in f:
            # remove comments
            if '#' in line:
                line = line.split('#')[0]
            line = ' '.join(line.lstrip().split())  # removes leading and extra WS

            if len(line) == 0:
                continue

            params = line.split(' ')
            key = params[0]

            if key == 'eval':
                if params[1] == 'pressure':
                    self.eval['pressure'].append(self.Eval(
                        params[1],
                        params[3],
                        self.convert_sufix_number(params[4]),
                        self.convert_sufix_number(params[2])
                    ))
                if params[1] == 'flow':
                    self.eval['flow'].append(self.Eval(
                        params[1],
                        params[3],
                        self.convert_sufix_number(params[4]),
                        self.convert_sufix_number(params[2])
                    ))

                if params[1] in self.eval:
                    #Eval def __init__(self, chem, node, value, time=None):
                    self.eval[params[1]].append(self.Eval(
                        params[1],
                        params[3],
                        self.convert_sufix_number(params[4]),
                        self.convert_sufix_number(params[2])
                        ))
                else:
                    self.eval[params[1]] = [self.Eval(
                        params[1],
                        params[3],
                        self.convert_sufix_number(params[4]),
                        self.convert_sufix_number(params[2])
                        )]
            else:
                print('No valid handler for: '+key)

    def add_input_device(self, port, device, dev_params):
        #def __init__(self, node, dev_type, args, is_grounded=True):
        self.dev[port] = self.Dev(port, device, dev_params)

    def add_solution(self, solution, port, value, line_num=None):
        #def __init__(self, chem, node, in_value):
        if port in self.dev:
            self.chem[solution] = self.ChemInput(solution, port, value)
            #if params[1] in self.eval:
            #    self.eval[params[1]].append(self.Eval(params[1], params[4], params[5]))
            #else:
            #    self.eval[params[1]] = [self.Eval(params[1], params[4], params[5])]
        else:
            raise ValueError("Device not created for input: "+port+", line: "+str(line_num)+'\n'+ \
                "    chem: "+solution+', input port: '+port+', '+'Concentration: '+value)

    #def add_eval_node(self, params):
    def add_eval_node(self, prop, node, value, time, dev=None):
        if prop in self.eval:
            #Eval def __init__(self, chem, node, value, time=None):
            self.eval[prop].append(self.Eval(
                prop=prop,
                node=node,
                value=self.convert_sufix_number(value),
                time=self.convert_sufix_number(time),
                device=dev
                ))
        else:
            self.eval[prop] = [self.Eval(
                prop=prop,
                node=node,
                value=self.convert_sufix_number(value),
                time=self.convert_sufix_number(time),
                device=dev
                )]
        self.probes['concentration'].append(self.Probe('concentration', node))


    def add_probe(self, probe_type, node, device, l_num=None):
        if probe_type == 'pressure':
            self.probes['pressure'].append(self.Probe(
                'pressure',
                node=node))
        elif probe_type == 'flow':
            self.probes['flow'].append(self.Probe(
                'flow',
                node=node,
                device=device))
        elif (len(self.chem) > 0) and probe_type in [ch.getChem() for ch in self.chem.values()]:
            self.probes['concentration'].append(self.Probe(
                'concentration',
                node=device))
        elif probe_type == "pressureNode":
            self.probes['pressureNode'].append(self.Probe(
                'pressureNode',
                node=node,
                device=device
            ))
        elif probe_type == "concentrationNode":
            self.probes['concentrationNode'].append(self.Probe(
                'concentrationNode',
                node=node,
                device=device
            ))
        else:
            if isinstance(l_num, int):
                raise ValueError(f'{probe_type} is not a valid node, use "pressure", "flow", "pressureNode", "concentrationNode" or declare the input chemical before this line. Line number {l_num+1}')
            else:
                raise ValueError(f'{probe_type} is not a valid node, use "pressure", "flow", "pressureNode", "concentrationNode" or declare the input chemical before this line. Line number {l_num}')


    def add_analysis(self, analysis_type, params):
        if analysis_type == 'transient':
            if 'transient' in self.times:
                self.times['transient'].append(params)
            else:
                self.times['transient'] = [params]
        elif analysis_type == 'static':
            if 'static' in self.times:
                self.times['static'].append(params)
            else:
                self.times['static'] = [params]


    def convert_sufix_number(self, in_value):

        if isinstance(in_value, str):
            if in_value[-1] == 'm':
                out_val = float(in_value[:-1])*1e-3
            elif in_value[-1] == 'u':
                out_val = float(in_value[:-1])*1e-6
            elif in_value[-1] == 'n':
                out_val = float(in_value[:-1])*1e-9
            elif in_value[-1] == 'p':
                out_val = float(in_value[:-1])*1e12
            elif in_value[-1] == 'k':
                out_val = float(in_value[:-1])*1e3
            elif in_value[-1] == 'M':
                out_val = float(in_value[:-1])*1e6
            elif in_value[-1] == 'G':
                out_val = float(in_value[:-1])*1e9
            else:
                out_val = float(in_value)
            return out_val
        else:
            raise ValueError("Input value not a string: "+str(in_value))

    def addNetlistFile(self, nFile):
        self.netListFiles.append(nFile)

    def removeNelistFile(self):
        # find file that matches key

        # remove file
        pass

    def clearNetlistFile(self):
        self.netListFiles = []

    def addInlet(self, inletName, inletArgs):
        #' '.join(str.split()) reduces multispaces to single space
        inletArgs = ' '.join(inletArgs.split()).split(' ')
        self.inlets[inletName] = {'args':inletArgs}

    def removeInlet(self):
        pass

    def addEval(self, evalNode, evalArgs):
        evalArgs = ' '.join(evalArgs.split()).split(' ')
        self.eval[evalNode] = {'args':evalArgs}

    def removeEval(self):
        pass

    def addDev(self, dev, node, args):
        self.dev[node] = {'dev':dev, 'args':args}

    def getDeviceList(self):
        return self.dev

    def getDevice(self, port):
        return self.dev[port]

    def getEvaluation(self, chem=None):

        if chem is None:
            return self.eval
        else:
            eval = self.eval[chem]
            e_out = {}
            for e in eval:
                e_out[e.getNode()] = 'C:'+e.getValue()

            return e_out

    def getInputChemList(self):
        return self.chem

    def getInputChem(self, chem):
        return self.chem[chem].getNode(), self.chem[chem].getValue()

    def getSimulationTimes(self):
        return self.times

    def getProbeList(self):
        return self.probes
