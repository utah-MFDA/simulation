

# How are interfaces handled?

from components import Component_node
from components import Channel, IO_Connection, MembraneValve

class Netlist():
    def __init__(self):
        
        self.componentList = []
        self.nodeList = []

    def addComponent(self, key, componentType, componentKey, nodekeys, params=[]):
        
        # selects component based on list
        # a more generic way will be developed in the future
        if componentType == 'channel':
            component = Channel(params[0], componentKey)
        elif componentType == 'displacementValve' or 'displacement_valve' or 'MembraneValve':
            if len(params) == 2:
                component = MembraneValve(params[0], params[1], componentKey)
            else:
                component = MembraneValve(params[0], params[1], componentKey, params[2])
        elif componentType == 'IO':
            component = IO_Connection(componentKey)

        #compNodes = []

        for key in nodekeys:
            keyFound = False
            for node in self.nodeList:
                if node.getKey() == key:
                    keyFound = True
                    node.addComponent(component)
                    #compNodes.append(node)
                    break

            if not keyFound:
                newNode = Netlist_node(key)
                self.nodeList.append(newNode)
                #compNodes.append(node)
                newNode.addComponent(component)


        ## TODO check for component with same node
        # Maybe not nessary yet



        # TODO check if key is unique

        # add component to list

        self.componentList.append([key, component])


    def findOpenRoutes(self, component):
        pass
        # need to index the component then search outward

        

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
    # the component node points to component
    def addComponent(self, component, nodeIndex):
        component.addNode(self, nodeIndex)
        self.nodeComponentList.append([component.getNode(nodeIndex)])

    # Why did I need this?
    #def getInternalIndex(self, componentKey):
    #    for comp in self.nodeComponentList:
    #        if comp.getKey == componentKey:
                 

class NetlistGraph():
    def __init__(self):
        pass