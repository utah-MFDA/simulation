
import os, sys
#sys.path.append('./..')
sys.path.append('.')

#from ValveArray.simulation import valveArraySimulation
import  netListParse
import simulation

net1 = netListParse.main('./ValveArray/tests/testDev2')

net1.subForJunctions()

linSim = simulation.LinearSolver(net1)

linSim.generateEquations()

solutionVec = linSim.getSolution()

print(solutionVec)
