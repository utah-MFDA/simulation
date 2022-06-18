



class Component():
    """
    component definitions

    types of components
    - channel
    - check valve
    - displacement valve
    - heater
    - resivior
    
    """

    # internal node that points to external nodes
    class Node():
        def __init__(self, component):
            self.externalNode = None
            self.component = component
            self.index = None
            

        def assignExternalNode(self, e_node):
            self.externalNode = e_node

        def getComponent(self):
            return self.component

        def getNodeIndex(self, e_node):
            #print(e_node)
            #print(self.component.nodeList)
            for ind, node in enumerate(self.component.nodeList):
                if e_node == node.externalNode:
                    return ind

        def getComponentKey(self):
            return self.component.getKey()

        def getExternalNode(self):
            return self.externalNode
    
    class Branch():
        def __init__(self):
            self.nodeList = []

        # A branch can only hold 2 nodes
        def __init__(self, nodes):
            self.nodeList = [nodes[0], nodes[1]]

        def getNodes(self):
            return self.nodeList
    
    def __init__(self, key):
        self.nodeList = []
        self.branchList = []
        self.key = key

    # TODO see if this is needed
    # the i node will be the internal node (int)
    # the e_node will be the netlist node
    def connectInternalNode(self, i_node, e_node):
        for node in self.nodeList:
            if node.internalNode == i_node:
                node.setExternallNode(e_node)

    def isIO(self):
        return False

    def isValve(self):
        return False

    def assignNode(self, e_node, i_node_index):
        self.nodeList[i_node_index].assignExternalNode(e_node)

    def getNode(self, nodeIndex):
        return self.nodeList[nodeIndex]

    def getKey(self):
        return self.key

    def assignExternalNode(self, e_node, nodeIndex):
        self.nodeList[nodeIndex].assignExternalNode(e_node)

    def getExternalNodes(self):
        # returns a list of nodes with [key, nodePointer]
        e_node_list = []
        for node in self.nodeList:
            e_node_list.append([node.getExternalNode().getKey(), node.getExternalNode()])
        return e_node_list

    # TODO not implemented
    """
    def getNodeIndex(self, e_node):
        for ind, node in self.nodeList:
            if e_node == node.externalNode:
                return ind
    """
    #def getInternalNode(self, e_node):
    #    for node in self.nodeList:
    #        if node.getExternalNode == e_node:
    #            return 

# -- Valve Class -----------------------------------------------

class Valve(Component):
    def __init__(self, key):
        # 1 - closed, 0 - open
        self.key = key
        self.valveState = 0
        self.displacement = 0


    def setState(self, state):
        # This will return the displacement of the valve
        if self.valveState == 0 and state == 1:
            self.closeValve()
        if self.valveState == 1 and state == 0:
            self.openValve()

    def getState(self):
        return self.valveState

    def closeValve(self):
        self.valveState = 1

    def openValve(self):
        self.valveState = 0

    def getDisplacement(self):
        return self.displacement

    def isValve(self):
        return True

# -- Membrane valve class

class MembraneValve(Valve):
    def __init__(self, radius, fluid_chamber_height, key, completeSeal=True):
        self.key = key
        
        # normally open
        self.valveState = 0

        # convert str to float
        radius = float(radius)
        fluid_chamber_height = float(fluid_chamber_height)

        fluid_vol = 3.141 * radius * radius * fluid_chamber_height

        # This is not nessarily true, but an assumption we are making for now
        self.displacement = fluid_vol

        self.completeSeal = completeSeal

        # A typical membrane valve has 2 nodes
        self.nodeList = [Component.Node(self), Component.Node(self)]

        self.branchList = [Component.Branch()]

# -- Channel Class

class Channel(Component):

    def __init__(self, ch_dimensions, key):
        self.width = ch_dimensions[0]
        self.height= ch_dimensions[1]
        self.length= ch_dimensions[2]

        #
        # The array has the following information
        # [fluidType, end_1, end_2]
        # end_1 and end_2 are the floats that describe the different points of the ends of the fluid slug
        #
        
        self.fluidArr= []

        # nodes to point to other components
        # channels have 2 nodes
        self.nodeList = [Component.Node(self), Component.Node(self)]
        
        # nodes will be added as supplied by the list
        #i = 0
        #for node in range(0,1):
        #    self.nodeList.append(Component_node(i, None))
        #    i += 1

        self.key = key


    def addFluid(self, node, fluidType, size, initDisplacement=0):
        
        size = (size-initDisplacement)/(self.width * self.height)
        
        initDisplaceVol = initDisplacement/(self.width * self.height)
        # 0 -> 1 is positive
        # channels will only has 2 nodes
        if node == 0:
            self.fluidArr.append([fluidType, 0+initDisplaceVol, -size])

        if node == 1:
            self.fluidArr.append([fluidType, self.length-initDisplaceVol, self.length+size])

    def removeFluid(self, fluid_ind):
        del self.fluidArr[fluid_ind]

    def moveFluids(self, direction, displacement):
        
        # There will need to be a check where if the ends of the fluid are both negative past node 0
        # or both greater than the length of the fluid, past node 1
        # The fluids are removed from the channel

        # This method moves the fluids based on the desired direction and displacement
        # in the future this can be done in a single step, but for now we are for looping

        displaceLen = displacement/(self.width * self.height)

        if direction == 0:      # reverses the direction
            displaceLen *= -1

        for slug in self.fluidArr:
            slug[1] += displaceLen
            slug[2] += displaceLen

        pass

    # --- LS methods

    def getResistance(self):
        # we assume water for now
        eta = 1.0016e-3

        R = 12*eta*self.length/((1-0.63(self.height/self.width)*(self.height**3*self.width)))
        return R

    def fluidStr(self):
        returnString = ''

        for fluid in self.fluidArr:
            returnString += 'Type: ' + fluid[0] + ', Loc 1: ' + str(fluid[1]) + ', Loc 2: ' + str(fluid[2]) + '\n'

        return returnString

# -- Reservior Class

class Reservoir(Component):

    def __init__(self):
        pass

# -- Pump Class -------------------------------------------------------------

class Pump(Component):
    pass

# -- IO class ---------------------------------------------------------------

class IO_Connection(Component):
    def __init__(self, key):
        self.key = key
        self.nodeList = [Component.Node(self)]
        self.flow = None
        self.pressure = None

    def setFlow(self, flow):
        self.flow = flow

    def setPressure(self, pressure):
        self.pressure = pressure


    def isIO(self):
        return True

# -- Junction Class ----------------------------------------------------------

class Junction(Component):
    def __init__(self, key, numOfConnections):
        self.key = key
        self.nodeList = []
        for i in range(numOfConnections):
            self.nodeList.append(Component.Node(self))

# -- Node Class --------------------------------------------------------------

class Component_node():
    def __init__(self, internalNode, externalNode):
        self.internalNode = internalNode
        # used by the netlist class to connect to other components
        self.externalNode = externalNode

    def internalNode(self):
        return self.internalNode

    def externalNode(self):
        return self.externalNode

    def setExternalNode(self, externalNode):
        self.externalNode = externalNode

    # if the issue of internal nodes arise a method will be created
