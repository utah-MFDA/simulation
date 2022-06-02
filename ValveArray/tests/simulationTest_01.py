import os, sys
#sys.path.append('./..')
sys.path.append('.')

from ValveArray.simulation import valveArraySimulation

import netListTest


net1 = netListTest.main()

sim1 = valveArraySimulation()

sim1.loadFromNetlistObj(net1)