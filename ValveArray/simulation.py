
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
        self.debug = False

    def __init__(self, netlist):
        self.netlist = netlist

    def loadNetList(self):
        pass

    def loadFromNetlistObj(self, netlist):
        self.netlist = netlist

    def generateGraph(self):
        pass

    def setDebug(self, boolIn):
        self.debug = boolIn

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

    #def __init__(self):
    #    super(LinearSolver, self).__init__()

    def generateEquations(self):
        
        # get number of nodes

        # TODO use method call
        numOfNodes = len(self.netlist.nodeList)

        self.nodeKeys = []

        self.componentList = np.empty((0,3))
        self.componentCount = {'IO':0, 'Junction':0, 'else':0}

        # one set of node for pressure another set for flow

        solver_matrix = np.zeros((numOfNodes*2, numOfNodes*2))
        solver_vector = np.zeros((1, numOfNodes*2))

        junction_M = np.zeros((0, numOfNodes*2))
        num_junc_eq = 0

        for node in self.netlist.nodeList:
            self.nodeKeys.append(node.getKey())

        nodeKeys = self.nodeKeys
        #print(nodeKeys)

        # Componnent is returned [key, pointer]
        eqInd = 0

        for component in self.netlist.componentList:
            if component[1].isIO():
                node = component[1].getExternalNode().getKey()

                PInd1 = nodeKeys.index(node)
                FInd1 = nodeKeys.index(node) #+ numOfNodes

                defValue = component[1].hasConstraint()
                
                if defValue == "flow":
                    ioInd = FInd1+numOfNodes
                    value = component[1].getFlow()
                    #solver_vector[0, eqInd+numOfNodes] = value
                    solver_vector[0, eqInd] = value

                elif defValue == "pressure":
                    ioInd = PInd1
                    value = component[1].getPressure()
                    solver_vector[0, eqInd] = value

                else:
                    # TODO throw exception
                    print(str(component[1]) + " has issue")

                #solver_vector[0, eqInd] = value
                eq = np.zeros((numOfNodes*2))
                eq[ioInd] = 1
                #eq2 = solver_matrix[eqInd,:]
                solver_matrix[eqInd,:] = eq
                eqInd += 1

                # add one equation with IO

                self.componentCount['IO'] += 1
                #self.componentList.append('IO')
                #numEq = 1

            elif component[1].isJunction():
                PInd = []
                FInd = []
                for node in component[1].getExternalNodes():
                    PInd.append(nodeKeys.index(node[1].getKey()))
                    FInd.append(nodeKeys.index(node[1].getKey())+ numOfNodes)

                

                # set flow equation
                FEq = np.zeros((numOfNodes*2))
                for FIndInd in FInd:
                    FEq[FIndInd] = 1

                # append flow equations
                # solver_matrix[eqInd,:] = FEq
                junction_M = np.append(junction_M, FEq.reshape(1, numOfNodes*2), axis=0)
                num_junc_eq += 1

                # set Pressure Equations
                PEq = []
                for i in range(len(PInd)-1):
                    tempEq = np.zeros((numOfNodes*2))
                    tempEq[PInd[i]]   = 1
                    tempEq[PInd[i+1]] = -1
                    #PEq.append(tempEq)
                    junction_M = np.append(junction_M, tempEq.reshape(1, numOfNodes*2), axis=0)
                    #solver_matrix[eqInd,:] = tempEq
                    num_junc_eq += 1

                #self.componentCount['Junction'] += 1
                #numEq = len(PInd)


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

                    #self.componentCount['else'] += 1
                    #numEq = 2
                    #self.componentList.append(component.getKey())
            #self.componentList = np.append(self.componentList, np.array([component[1].getKey(), component[1].getType(), numEq]).shape((1,3)), axis=1)
        self.junctionMatrix= junction_M
        self.solverMatrix = np.append(solver_matrix[0:solver_matrix.shape[0]-num_junc_eq, :], junction_M, axis=0)
        self.solverVector = solver_vector

        pass

    def getFlowSolution(self):

        numOfNodes = len(self.netlist.nodeList)

        solution = np.linalg.solve(self.solverMatrix, self.solverVector.transpose())

        #tempMat = self.solverMatrix
        #print(self.solverMatrix)
        #print(self.solverVector)
        if self.debug:
            print(solution)

        while solution[solution < 0][-numOfNodes:].any():
            #print( solution[solution < 0])
            #print("has negatives")
            nodes = solution < 0
            #nodes = (solution < 0)
            #ind1 = int(len(solution)/2)
            #ind2 = len(solution)-1
            #nodes = nodes[0,int(len(solution)/2):len(solution)-1]
            nodes = nodes[-numOfNodes:]
            nodes_vec = (solution < 0).astype(int)*-2 + 1 #[int(len(solution))/2:len(solution)-1]*-1


            compList = self.componentList[:, 1]
            jnct = (compList == 'jct')

            for ind, n in enumerate(nodes):
                # get node key
            
                # get junction to equation
                if n:
                    #nodeIndex = self.nodeKeys.index(ind) + numOfNodes
                    for rInd, row in enumerate(self.junctionMatrix):

                        #print(row[ind+numOfNodes])

                        if row[ind+numOfNodes]:
                            self.junctionMatrix[rInd, ind+numOfNodes] *= -1
                    # if n:
                        #col = self.solverMatrix[ind, :].reshape((len(nodes_vec), 1))
                        #newCol = np.multiply(col, nodes_vec)
                        
                        #self.solverMatrix[ind, :] = np.multiply(self.solverMatrix[:, ind].reshape((len(nodes_vec), 1)), nodes_vec).reshape((len(nodes_vec)))

            self.solverMatrix[-self.junctionMatrix.shape[0]:,:] = self.junctionMatrix

            solution = np.linalg.solve(self.solverMatrix, self.solverVector.transpose())

            #print(solution)
            #print(' ')
            if self.debug:
                print(solution)
                print('\n')
                self.netlist.setSolution(solution, self.nodeKeys)
                self.netlist.generateGraph('debugLinearSim', 'LinearSolnDebug')
                matrixFile = open('matrixDebug', 'w+')
                matrixFile.write(str(self.solverMatrix))
                matrixFile.close()

                vectorFile = open('vectorDebug', 'w+')
                vectorFile.write(str(self.solverVector))
                vectorFile .close()
            a = 1

        #print('')
        #print(self.solverMatrix)

        return solution

    

