
#import os, sys
#sys.path.append('./')

from pathlib import Path
import sys
path_root = Path(__file__).parents[0]
sys.path.append(str(path_root))

# How are interfaces handled?

from components import Component, Component_node, Junction
from components import Channel, IO_Connection, MembraneValve

class Netlist():
    
    def __init__(self):
        
        self.componentList = []
        self.nodeList = []
        self.chemicalList = []

        self.numJunction = 0
        self.virtualNodes= 0

        self.solution = None
        self.solutionNodeKey = None

    def addComponent(self, componentType, componentKey, nodekeys, params=[]):
        
        # selects component based on list
        # TODO develop a more generic way will be developed in the future
        if componentType == 'channel':
            component = Channel(params, componentKey)
        elif componentType == 'displacementValve' or componentType == 'displacement_valve' or componentType == 'MembraneValve':
            if len(params) == 2:
                component = MembraneValve(params[0], params[1], componentKey)
            else:
                component = MembraneValve(params[0], params[1], componentKey, params[2])
        elif componentType == 'IO':
            component = IO_Connection(componentKey, params)
            # store chemical values in chem-list
            if component.hasChemical():
                for chem in component.getChemicalNames():
                    if chem not in self.chemicalList:
                        self.chemicalList.append(chem)
                    
        elif componentType == 'Junction':
            component = Junction(componentKey, params[0])

        #compNodes = []

        # TODO This can be redone with a different structure
        for ind, key in enumerate(nodekeys):
            keyFound = False
            #print(ind)
            for node in self.nodeList:
                if node.getKey() == key:
                    keyFound = True
                    node.addComponent(component, ind)
                    #compNodes.append(node)
                    break

            if not keyFound:
                #self.addNode(self, key)
                newNode = Netlist_node(key)
                self.nodeList.append(newNode)
                #compNodes.append(node)
                newNode.addComponent(component, ind)


        ## TODO check for component with same node
        # Maybe not nessary yet



        # TODO check if key is unique

        # add component to list

        self.componentList.append([componentKey, component])

    def addNode(self, nodeKey):
        newNode = Netlist_node(nodeKey)
        self.nodeList.append(newNode)

    def getComponentList(self):
        return self.componentList

    def getNodesFromComponent(self, component):
        pass

    #TODO finish this method
    def getComponentsFromNode(self, in_node):
        for node in self.nodeList:
            if node == in_node:
                pass

    # Probably for init component search
    # TODO look over if is needed
    def getNodesFromComponentKey(self, componentKey):
        pass

    def findOpenRoutes(self, component):
        pass
        # need to index the component then search outward

    # TODO implement with a better structure
    def getNode(self, nodeKey):
        for node in self.nodeList:
            if node.getKey() == nodeKey:
                return node



    # ----------------------------------------------------------

    def subForJunctions(self):
        for node in self.nodeList:
            self.addJunction(node)

    def addJunction(self, node):
        
        # Function in is a  

        #nodeRef = self.getNode(nodeKey)

        # check the amount of nodes connected

        numComp = len(node.nodeComponentList)

        if numComp < 3:
            # do not add junction
            pass
        else:
            # TODO check component keys
            #componentExist = False
            #while()
            self.numJunction =+ 1

            # TODO this requires making virtual nodes 

            newNodes = ['vn'+str(self.virtualNodes), 'vn'+str(self.virtualNodes+1)]
            nodeKeys = [node.getKey()] + newNodes
            #nodeKeys.append(newNodes)
            # adds virtual node count
            self.virtualNodes =+ 2

            for n in newNodes:
                self.addNode(n)

            # first component keeps initial node
            
            for ind, compNode in enumerate(node.nodeComponentList):
                if ind == 0:
                    pass
                #elif ind == len(node.nodeComponentList):
                #    pass
                else:
                    # Add component to Netlist node
                    component = compNode.getComponent()
                    nodeIndex = compNode.getNodeIndex(node)

                    self.getNode(nodeKeys[ind]).addComponent(component, nodeIndex)

            # remove other nodes from node list
            node.nodeComponentList = [node.nodeComponentList[0]]

            # build junction component
            self.addComponent('Junction', 'J'+str(self.numJunction), nodeKeys ,[numComp])


    def setSolution(self, solution, solutionNodeKey):
        self.solution = solution
        self.solutionNodeKey = solutionNodeKey

    def getNodeSolutionIndex(self, key):
        for index, n in enumerate(self.solutionNodeKey):
            if n == key:
                return index

    def getNumberOfNodes(self):
        return len(self.nodeList)

    def getNumberOfChemicals(self):
        return len(self.chemicalList)

    def getComponentList(self):
        compList = []
        for comp in self.componentList:
            compList.append(comp[1])
        #a = self.componentList[:]

        return compList
    
    def getChemIndex(self, chemNames):
        chemIndex = []
        
        for chem in chemNames:
            chemIndex.append(self.chemicalList.index(chem))

        return chemIndex

    # Graph generating code ----

    def genGraphGetNode(self, component, outFile, simInfo, nodeRef=None, solutionVec=None):
        for node in component.getExternalNodes():
            if nodeRef == node[1]:
                # skip if it is the calling node
                pass
            elif self.solution is None:
                outFile.write('\t"' + str(component.getKey()) + '" -- "' + str(node[1].getKey()) + '";\n')
                self.genGraphGetComponent(node[1], outFile, component)
            else:
                if simInfo == "flow":
                    nodeIndex = self.getNodeSolutionIndex(node[1].getKey())
                    NodeP = self.solution[nodeIndex]
                    NodeF = self.solution[int(len(self.solution)/2 + nodeIndex)]
                    outFile.write('\t"' + str(component.getKey()) + '" -- "' + str(node[1].getKey()) + '\\n' +
                        'P:'+ "{:.4f}".format(NodeP[0]) + '\\n' +
                        'F:'+ "{:.4f}".format(NodeF[0]) + '";\n')
                    self.genGraphGetComponent(node[1], outFile, simInfo, component)
                elif simInfo == "chem":
                    nodeIndex = self.getNodeSolutionIndex(node[1].getKey())
                    NodeP = self.solution[nodeIndex]
                    NodeF = self.solution[int(len(self.solution)/2 + nodeIndex)]
                    outFile.write('\t"' + str(component.getKey()) + '" -- "' + str(node[1].getKey()) + '\\n' +
                        'P:'+ "{:.4f}".format(NodeP[0]) + '\\n' +
                        'F:'+ "{:.4f}".format(NodeF[0]) + '";\n')
                    # Chemical printing
                    self.genGraphGetComponent(node[1], outFile, simInfo, component)

    def genGraphGetComponent(self, node,  outFile, simInfo, componentRef=None):
        for componentNode in node.getComponents():
            component = componentNode.getComponent()
            if componentRef == component:
                # skip if it is the calling component
                pass
            elif self.solution is None:
                outFile.write('\t"' + str(node.getKey()) + '" -- "' + str(component.getKey()) + '";\n')
                self.genGraphGetNode(component, outFile, node)
            else:
                if simInfo == "flow":
                    nodeIndex = self.getNodeSolutionIndex(node.getKey())
                    NodeP = self.solution[nodeIndex]
                    NodeF = self.solution[int(len(self.solution)/2 + nodeIndex)]
                    outFile.write('\t"' + str(node.getKey()) + '\\n' +
                        'P:'+ "{:.4f}".format(NodeP[0]) + '\\n' +
                        'F:'+ "{:.4f}".format(NodeF[0]) + '" -- "' + str(component.getKey()) + '";\n')
                    self.genGraphGetNode(component, outFile, simInfo, node)
                if simInfo == "chem":
                    nodeIndex = self.getNodeSolutionIndex(node.getKey())
                    NodeP = self.solution[nodeIndex]
                    NodeF = self.solution[int(len(self.solution)/2 + nodeIndex)]
                    outFile.write('\t"' + str(node.getKey()) + '\\n' +
                        'P:'+ "{:.4f}".format(NodeP[0]) + '\\n' +
                        'F:'+ "{:.4f}".format(NodeF[0]) + '" -- "' + str(component.getKey()) + '";\n')
                    self.genGraphGetNode(component, outFile, simInfo, node)


#    def genGraphGetComponent(self, node,  outFile, componentRef=None):
#        for componentNode in node.getComponents():
#            component = componentNode.getComponent()
#            if componentRef == component:
#                # skip if it is the calling component
#                pass
#            elif self.solution is None:
#                outFile.write('\t"' + str(node.getKey()) + '" -- "' + str(component.getKey()) + '";\n')
#                self.genGraphGetNode(component, outFile, node)
#            else:
#                nodeIndex = self.getNodeSolutionIndex(node.getKey())
#                NodeP = self.solution[nodeIndex]
#                NodeF = self.solution[int(len(self.solution)/2 + nodeIndex)]
#                outFile.write('\t"' + str(node.getKey()) + '\\n' +
#                    'P:'+ "{:.4f}".format(NodeP[0]) + '\\n' +
#                    'F:'+ "{:.4f}".format(NodeF[0]) + '" -- "' + str(component.getKey()) + '";\n')
#                self.genGraphGetNode(component, outFile, node)

    def generateGraph(self, outFileName, graphName, simInfo, solutionVec=None):
        # get first IO
        IO1 = None

        outFile = open(outFileName, 'w+')

        outFile.write('graph ' + str(graphName) + ' {\n')

        for comp in self.componentList:
            if comp[1].isIO():
                IO1 = comp[1]
                break

        # Recersively look for next component then for the next node
        self.genGraphGetNode(IO1, outFile, simInfo, None, solutionVec)

        outFile.write('}')
        outFile.close()
        


    # print methods ---------------------------------------------

    def printNodes(self):
       for node in self.nodeList:
           node.toString()

    def printComponents(self):
        print(str(self.componentList).replace('], [', '],\n['))


        

# These might not be needed
class nl_component():
    pass

class Netlist_node():
    def __init__(self, key):
        self.nodeComponentList = []

        # the key is a unique string for the node, generally pretty short
        self.nodeKey  = key

    def getKey(self):
        return self.nodeKey

    # node points to component node
    # the component node points to netlist node
    def addComponent(self, component, nodeIndex):
        # assign internal ndoe to point to external node
        component.assignExternalNode(self, nodeIndex)
        # assign external node to point to internal node
        self.nodeComponentList.append(component.getNode(nodeIndex))

    def getComponents(self):
        return self.nodeComponentList
    # Why did I need this?
    #def getInternalIndex(self, componentKey):
    #    for comp in self.nodeComponentList:
    #        if comp.getKey == componentKey:

    def toString(self):
        print('Node Key: ' + self.nodeKey)
        compKeys = []
        for compNode in self.nodeComponentList:
            compKeys.append(compNode.getComponentKey())

        print(compKeys)
        print('')
                 

class NetlistGraph():
    def __init__(self):
        pass