
from pathlib import Path
import sys

path_root = Path(__file__).parents[0]
sys.path.append(str(path_root))

import components
import netlist
from ValveArray.components import MembraneValve, Valve

from netlist import Netlist

class baseSimulation():
    def __init__(self):
        self.netlist = None

    def loadNetList(self):
        pass

    def loadFromNetlistObj(self, netlist):
        self.netlist = netlist

class valveArraySimulation(baseSimulation):

    def loadValveStates(self, state):
        for valve in state:
            for component in self.netlist.getComponentList():
                if component[0] == valve:
                    isinstance(component[1], MembraneValve)
                    print(state[valve])
                    component[1].setState(state[valve])


    def start(self):
        pass


    #TODO find route to IO paths
    def findIORoute(self, componentKey):
        
        # get the component as start node
        for component in self.netlist.getComponentList():
            if component[0] == componentKey:
                compPointer = component[1]
                break
        
        externalNodes = compPointer.getExternalNodes()

        for node in externalNodes:
            pass

    # the parameter can be either node or component
    def searchForIO(self, param1):
        
        if   issubclass(param1, components.Component):
            externalNodes = param1.getExternalNodes()

        elif issubclass(param1, netlist.Netlist_node):       
            self.netlist
        
        #self.netlist.getNodesFromComponent(component)

    # --- get valve actions
    #  

    def getNextAction(self):
        pass

    def getValveDeltas(self):
        # compare current and previous valve states


        pass

    def getNextValveState(self):
        pass



    # print statements

    def printValveStates(self):
        valves = {}
        for component in self.netlist.getComponentList():
            
            if isinstance(component[1], components.MembraneValve):
                valves.update({str(component[1].getKey()) : component[1].getState()})
        
        print(valves)

    # --- 
    # 

    #def 

class LinearSolver(baseSimulation):

    def __init__(self):
        pass

    def generateEquations(self):
        
        # get number of nodes



        pass

