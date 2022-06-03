
from pathlib import Path
import sys

path_root = Path(__file__).parents[0]
sys.path.append(str(path_root))

import components
from ValveArray.components import MembraneValve, Valve

from netlist import Netlist

class valveArraySimulation():
    def __init__(self):
        self.netlist = None

    def loadNetList(self):
        pass

    def loadFromNetlistObj(self, netlist):
        self.netlist = netlist

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
        for component in self.netlist.getComponentList():
            if component[0] == componentKey:
                compPointer = component[1]
                break
        
        externalNodes = compPointer.getExternalNodes()


    def searchForIO(self, component):
        self.netlist.getNodesFromComponent(component)

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

