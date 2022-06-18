
import numpy as np

# local imports

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

    def __init__(self, netlist):
        self.netlist = netlist

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


    def generateEquations(self):
        
        # get number of nodes

        # TODO use method call
        numOfNodes = len(self.netlist.nodeList)

        nodeKeys = []

        # one set of node for pressure another set for flow

        solver_matrix = np.zeros((numOfNodes*2, numOfNodes*2))

        for node in self.netlist.nodeList:
            nodeKeys.append(node.getKey())

        #print(nodeKeys)

        for component in self.netlist.componentList:
            nodes = component.getExternalNodes()
            for branch in component:
                nodes = branch.getNodes()
                eq1 = np.zeros((1, numOfNodes*2))
                eq2 = np.zeros((1, numOfNodes*2))
                # get flow and potential node indexes
                PInd1 = nodeKeys.index(nodes[0])
                PInd2 = nodeKeys.index(nodes[1])
                FInd1 = nodeKeys.index(nodes[0]) + numOfNodes
                FInd2 = nodeKeys.index(nodes[1]) + numOfNodes

                # set equation 1
                eq1[PInd1] = -1
                eq1[PInd2] = 1
                eq1[FInd1] = component.getResistance()

                # set equation 2
                eq2[FInd1] = 1
                eq2[FInd2] = -1

            

        pass

