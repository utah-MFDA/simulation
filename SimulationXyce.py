
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
        def __init__(self, chem, node, value, time=None):
            self.chem = chem
            self.node = node
            self.value= value
            #if time is not None:
            self.time = time
            
        def getNode(self):
            return self.node
        
        def getValue(self):
            return self.value

        def getChem(self):
            return self.chem

        #TODO time = None
        def getTime(self):
            return self.time

    # this will need some more generic definitions
    class Dev:
        def __init__(self, node, dev_type, args):
            self.type = dev_type
            self.node = node
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

    def __init__(self):
        self.netListFiles = []
        self.inlets = {}
        self.eval   = {}
        self.dev    = {}
        self.chem   = {}
        self.times  = {}
        
    def parse_config_file(self, file):
        in_conf_f = open(file)
        for l_num, line in enumerate(in_conf_f):
            # remove comments
            if '#' in line:
                line = line.split('#')[0]
            line = ' '.join(line.lstrip().split()) # removes leading and extra WS
            
            if len(line) == 0:
                continue
            
            params = line.split(' ')
            key = params[0]
            
            if key == 'input':
                self.dev[params[1]] = self.Dev(params[1], params[2], params[3:])
            elif key == 'chem':
                if params[2] in self.dev:
                    self.chem[params[1]] = self.ChemInput(params[1], params[2], params[3])
                    #if params[1] in self.eval:
                    #    self.eval[params[1]].append(self.Eval(params[1], params[4], params[5]))
                    #else:
                    #    self.eval[params[1]] = [self.Eval(params[1], params[4], params[5])]
                else:
                    raise ValueError("Device not created for input: "+params[2]+", line: "+str(l_num)+'\n'+\
                        "    chem: "+params[1]+', input port: '+params[2]+', '+'Concentration: '+params[3])
            
            # key for timing
            elif key == 'transient':
                if 'transient' in self.times:
                    self.times['transient'].append(params)
                else:
                    self.times['transient'] = [params]
            # untested method
            # would need to use DC simulations
            elif key == 'static':
                pass

    def parse_eval_file(self, ev_file):

        # reset eval list
        self.eval   = {}

        f = open(ev_file, 'r')

        for line in f:
            # remove comments
            if '#' in line:
                line = line.split('#')[0]
            line = ' '.join(line.lstrip().split()) # removes leading and extra WS
            
            if len(line) == 0:
                continue
            
            params = line.split(' ')
            key = params[0]

            if key == 'eval':
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
        
        if chem == None:
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