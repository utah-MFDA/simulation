from types import NoneType
from netlist import netlist

class valveArraySimulation():
    def __init__(self):
        self.netlist = NoneType

    def loadNetList(self):
        pass

    def loadFromNetlistObj(self, netlist):
        self.netlist = netlist

    def loadValveStates(self):
        pass

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



    # --- 
    # 

    #def 

