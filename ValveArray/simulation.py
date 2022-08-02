
from unittest import skip
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
        self.componentKeys = []
        self.juntionKeys = []
        self.ioKeys = []

        self.componentList = np.empty((0,3))
        self.componentCount = {'IO':0, 'Junction':0, 'else':0}

        # one set of node for pressure another set for flow

        solver_matrix = np.zeros((numOfNodes*2, numOfNodes*2))
        solver_vector = np.zeros((1, numOfNodes*2))

        # initialize component matrix
        component_M = np.zeros((0, numOfNodes*2))
        num_comp_eq = 0

        # initialize junction matrix
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

                self.ioKeys.append(component[1].getKey())

                # add one equation with IO

                #self.componentCount['IO'] += 1
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
                self.juntionKeys.append(component[1].getKey())


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

                    #solver_matrix[eqInd,:] = eq1
                    component_M = np.append(component_M, eq1.reshape(1, numOfNodes*2), axis=0)
                    num_comp_eq += 1
                    #eqInd += 1
                    #solver_matrix[eqInd,:] = eq2
                    component_M = np.append(component_M, eq2.reshape(1, numOfNodes*2), axis=0)
                    num_comp_eq += 1
                    #eqInd += 1

                    self.componentKeys.append(component[1].getKey())

                    #self.componentCount['else'] += 1
                    #numEq = 2
                    #self.componentList.append(component.getKey())
            #self.componentList = np.append(self.componentList, np.array([component[1].getKey(), component[1].getType(), numEq]).shape((1,3)), axis=1)
        self.junctionMatrix= junction_M
        self.componentMatrix = component_M
        # build solver matrix
        self.solverMatrix = solver_matrix
        self.solverMatrix[-num_comp_eq-num_junc_eq:-num_junc_eq, :] = component_M
        self.solverMatrix = np.append(solver_matrix[0:-num_junc_eq, :], junction_M, axis=0)
        # create pointer to solver vector
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
            print('\n')
            self.netlist.setSolution(solution, self.nodeKeys)
            self.netlist.generateGraph('debugLinearSim', 'LinearSolnDebug', 'flow')
            self.netlist.generateGraph('debugLinearSimCh', 'LinearSolnDebugCh', 'chem')
            matrixFile = open('matrixDebug', 'w+')
            matrixFile.write(str(self.solverMatrix))
            matrixFile.close()

            vectorFile = open('vectorDebug', 'w+')
            vectorFile.write(str(self.solverVector))
            vectorFile .close()


        # check for flow of nodes
        while solution[solution < 0][-numOfNodes:].any():
            #print( solution[solution < 0])
            #print("has negatives")
            nodes = solution < 0
            #nodes = (solution < 0)
            #ind1 = int(len(solution)/2)
            #ind2 = len(solution)-1
            #nodes = nodes[0,int(len(solution)/2):len(solution)-1]
            #Gets flow nodes
            nodes = nodes[-numOfNodes:]
            nodes_vec = (solution < 0).astype(int)*-2 + 1 #[int(len(solution))/2:len(solution)-1]*-1


            #compList = self.componentList[:, 1]
            #jnct = (compList == 'jct')

            #Iterate through nodes
            for ind, n in enumerate(nodes):
                # get node key
            
                # get junction to equation
                if n:
                    #nodeIndex = self.nodeKeys.index(ind) + numOfNodes
                    # check for flow of components
                    for rInd, row in enumerate(self.componentMatrix):
                        # find component with negative node
                        if row[ind] != 0:
                            # check other node is negative
                            for rNInd, rNode in enumerate(row[:int(len(row)/2)]):
                                # check if the row has another other node
                                # check if the node is also negative
                                # check if it is not the same node
                                indexNode = nodes[rNInd]
                                if rNode and (ind != rNInd) and nodes[rNInd]:
                                    self.componentMatrix[rInd,ind] *= -1
                                    self.componentMatrix[rInd,rNInd] *= -1

                                    

                                    continue

                    # check for flow of junctions
                    for rInd, row in enumerate(self.junctionMatrix):

                        #print(row[ind+numOfNodes])

                        if row[ind+numOfNodes]:

                            k = self.juntionKeys[rInd]
                            c = self.netlist.getComponentFromKey(k)
                            nK = self.nodeKeys[ind]
                            c.changeDirection(nK)

                            # Changes direction of node in eqeuations
                            self.junctionMatrix[rInd, ind+numOfNodes] *= -1
                    # if n:
                        #col = self.solverMatrix[ind, :].reshape((len(nodes_vec), 1))
                        #newCol = np.multiply(col, nodes_vec)
                        
                        #self.solverMatrix[ind, :] = np.multiply(self.solverMatrix[:, ind].reshape((len(nodes_vec), 1)), nodes_vec).reshape((len(nodes_vec)))

            self.solverMatrix[-self.componentMatrix.shape[0]-self.junctionMatrix.shape[0]:-self.junctionMatrix.shape[0], :] = self.componentMatrix
            self.solverMatrix[-self.junctionMatrix.shape[0]:,:] = self.junctionMatrix

            solution = np.linalg.solve(self.solverMatrix, self.solverVector.transpose())

            #print(solution)
            #print(' ')
            if self.debug:
                print(solution)
                print('\n')
                self.netlist.setSolution(solution, self.nodeKeys)
                self.netlist.generateGraph('debugLinearSim', 'LinearSolnDebug', 'flow')
                self.netlist.generateGraph('debugLinearSimCh', 'LinearSolnDebugCh', 'chem')
                matrixFile = open('matrixDebug', 'w+')
                matrixFile.write(str(self.solverMatrix))
                matrixFile.close()

                vectorFile = open('vectorDebug', 'w+')
                vectorFile.write(str(self.solverVector))
                vectorFile .close()
            a = 1

        self.setNodeValues(solution, 'flow')

        #print('')
        #print(self.solverMatrix)

        return solution

    def setNodevalues(self, solution, solnType):
        numOfNodes = len(self.nodeKeys)
        
        if solnType == 'flow':
            for ind, node in enumerate(self.netlist.nodeList):
                node.setPressure(solution[ind])
                node.setFlow(solution[ind+numOfNodes])
                # internal nodes
                #for iNodes in node.getInternalNodes

        if solnType == 'chem':
            pass

    # Chemical solution -----------------------------------------

    def generateChemicalSolution(self):
        
        # get number of nodes
        numOfNodes = len(self.netlist.nodeList)

        # get chemicals at each IO
        numOfChem = len(self.netlist.chemicalList)

        # solution vector
        # chem_solutionVec = np.zeros((numOfNodes, 1, numOfChem))
        chem_solutionVec = np.zeros((numOfChem, numOfNodes, 1))

        for node in self.netlist.nodeList:
            # set vector length
            node.setChemicalVec(numOfChem)


        IOcomp = []
        # get inlet IO nodes
        for comp in self.componentList:
            if comp[1].isIO():
                # go form in to out
                if comp[1].getDirection() == 'inlet':
                    IOcomp.append(comp[1])
                    #break

        # get chemical vector
        chemVecKeys = self.netlist.chemicalList

        

        # set values for inlet node
        for io in IOcomp:
            # get first node
            node1 = io.getExternalNode()
            for ind, chemC in enumerate(IO1.getChemicalConcentrations()):
                chemName = io.getChemicalNames()[ind]
                chemVecInd = chemVecKeys.index(chemName)
                node1.setChemicalFlow(chemC, chemVecInd)

                # get component then get next node
                self.genChemGetNextNode(node1)


    def genChemGetNextNode(self, startNode, refComponent):
        for comp in startNode.getComponents():
            if refComponent == comp:
                pass
            else:
                nodes = comp.getExternalNodes()
                for node in nodes:
                    if node == nodes:
                        pass
                    else:
                        self.genChemSetNodeSolution(node, startNode.getChemicalFlow())

    def genChemSetNodeSolution(self, node, inletChem):
        pass



"""
    def generateChemicalSolutions(self):
        
        # get number of nodes
        numOfNodes = len(self.netlist.nodeList)

        # get chemicals at each IO
        numOfChem = len(self.netlist.chemicalList)

        # get number components
        numOfComp = len(self.netlist.getComponentList())

        ### generate vectors
        # solution vector
        # chem_solutionVec = np.zeros((numOfNodes, 1, numOfChem))
        chem_solutionVec = np.zeros((numOfChem, numOfNodes, 1))

        # solver matrix
        # chem_solverMatrix = np.zeros((numOfNodes, numOfNodes, numOfChem))
        chem_solverMatrix = np.zeros((numOfChem, numOfNodes, numOfNodes))

        #nodeKeys = self.nodeKeys

        numOutlets = 0

        for compInd, component in enumerate(self.netlist.getComponentList()):
            
            if component.isIO():
                if component.getDirection() == 'outlet':
                    numOutlets += 1
                else:
                    # Get chemical names
                    chemNames = component.getChemicalNames()
                    chemConc  = component.getChemicalConcentrations()
                    # Get chemical index
                    chemIndex = self.netlist.getChemIndex(chemNames)

                    # Generate equation
                    eqS = np.zeros((numOfChem, 1))
                    eq1 = np.zeros((numOfChem, 1, numOfNodes))

                    for chemC in chemConc:
                        for chemI in chemIndex:
                            eq1[chemI, 0,compInd] = 1
                            eqS[chemI,0] = chemC

                    chem_solutionVec[:, compInd, :] = eqS
                    # .reshape((numOfChem, 1, numOfNodes))
                    for chemId, mat in enumerate(chem_solverMatrix):
                        mat[compInd-numOutlets, :] = eq1[chemId, :, :]
                    #chem_solverMatrix[:, compInd, :]= eq1


            elif component.isJunction():
                # for each node the set chem in / flow in = chem out / flow out

                # Get sign for nodes at junction

                junctionNodes = []

                #for equation_row in self.junctionMatrix:
                for nodeInd, node in enumerate(self.solverMatrix[:, compInd]):
                    if node == 1:
                        junctionNodes.append([nodeInd, 'i'])
                    if node == -1:
                        junctionNodes.append([nodeInd, 'o'])
                    else: # node == 0 
                        # since no flow do not add node
                        pass

                # generate equation
                eq1 = np.zeros((numOfChem, 1, numOfNodes))

                for node in junctionNodes:
                    if node[1] == 'o':
                        tempEq = -1 * np.ones((numOfChem, 1, 1))
                    else:
                        tempEq = np.ones((numOfChem, 1, 1))
                    for chemId, mat in enumerate(eq1):
                        mat[0, node[0]] = tempEq[chemId, :, :]
                    #eq1[:, 0, node[0]] = tempEq
                for chemId, mat in enumerate(chem_solverMatrix):
                    mat[compInd-numOutlets, :] = eq1[chemId, :, :]
                #chem_solverMatrix[:, compInd, :]= eq1


            else: # component is a genaric flow component
                
                # get component nodes
                componentNodes = component.getExternalNodes()
                eq1 = np.zeros((numOfChem, 1, numOfNodes))

                # generate equation
                tempEq = np.ones((1, 1, numOfChem))
                nodeInd = self.nodeKeys.index(componentNodes[0][0])
                eq1[:, 0, nodeInd] = tempEq

                nodeInd = self.nodeKeys.index(componentNodes[1][0])
                eq1[:, 0, nodeInd] = -1*tempEq

                for chemId, mat in enumerate(chem_solverMatrix):
                    mat[compInd-numOutlets, :] = eq1[chemId, :, :]
                #chem_solverMatrix[:, compInd, :]= eq1

        self.chem_solverMatrix = chem_solverMatrix
        self.chem_solutoinVec = chem_solutionVec
"""
"""
    def getChemicalSolution(self):
        
        chemSolution = np.linalg.solve(self.chem_solverMatrix, self.chem_solutoinVec)

        return chemSolution
""" 

