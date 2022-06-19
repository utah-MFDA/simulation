
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
        solver_vector = np.zeros((1, numOfNodes*2))

        for node in self.netlist.nodeList:
            nodeKeys.append(node.getKey())

        #print(nodeKeys)

        # Componnent is returned [key, pointer]
        eqInd = 0

        for component in self.netlist.componentList:
            if component[1].isIO():
                node = component[1].getExternalNode().getKey()

                PInd1 = nodeKeys.index(node)
                FInd1 = nodeKeys.index(node) + numOfNodes

                defValue = component[1].hasConstraint()
                
                if defValue == "flow":
                    ioInd = FInd1
                    value = component[1].getFlow()

                elif defValue == "pressure":
                    ioInd = PInd1
                    value = component[1].getPressure()

                else:
                    # TODO throw exception
                    print(str(component[1]) + " has issue")

                solver_vector[0, eqInd] = value
                eq = np.zeros((numOfNodes*2))
                eq[ioInd] = 1
                eq2 = solver_matrix[eqInd,:]
                solver_matrix[eqInd,:] = eq
                eqInd += 1

                # add one equation with IO

            elif component[1].isJunction():
                PInd = []
                FInd = []
                for node in component[1].getExternalNodes():
                    PInd.append(nodeKeys.index(node[1].getKey()))
                    FInd.append(nodeKeys.index(node[1].getKey())+ numOfNodes)

                    # TODO Figure how to solve

                # set flow equation
                FEq = np.zeros((numOfNodes*2))
                for FIndInd in FInd:
                    FEq[FIndInd] = 1

                solver_matrix[eqInd,:] = FEq
                eqInd += 1

                # set Pressure Equations
                PEq = []
                for i in range(len(PInd)-1):
                    tempEq = np.zeros((numOfNodes*2))
                    tempEq[PInd[i]]   = 1
                    tempEq[PInd[i+1]] = -1
                    #PEq.append(tempEq)
                    solver_matrix[eqInd,:] = tempEq
                    eqInd += 1

                


            else:
                nodes = component[1].getExternalNodes()
                for branch in component[1].getBranches():
                    nodes = branch.getNodes()
                    eq1 = np.zeros((numOfNodes*2))
                    eq2 = np.zeros((numOfNodes*2))
                    # get flow and potential node indexes
                    PInd1 = nodeKeys.index(nodes[0].getExternalNode().getKey())
                    PInd2 = nodeKeys.index(nodes[1].getExternalNode().getKey())
                    FInd1 = nodeKeys.index(nodes[0].getExternalNode().getKey()) + numOfNodes
                    FInd2 = nodeKeys.index(nodes[1].getExternalNode().getKey()) + numOfNodes

                    # set equation 1
                    eq1[PInd1] = -1
                    eq1[PInd2] = 1
                    eq1[FInd1] = component[1].getResistance()

                    # set equation 2
                    eq2[FInd1] = 1
                    eq2[FInd2] = -1

                    # TODO insert into matrix

                    solver_matrix[eqInd,:] = eq1
                    eqInd += 1
                    solver_matrix[eqInd,:] = eq2
                    eqInd += 1

        self.solverMatix = solver_matrix
        self.solverVector= solver_vector

        pass

    def getSolution(self):

        solution = np.linalg.solve(self.solverMatix, self.solverVector.transpose())

        return solution

