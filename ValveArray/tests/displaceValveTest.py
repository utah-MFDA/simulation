

import os, sys
#sys.path.append('./..')
sys.path.append('.')
#sys.path.append(os.path.join(os.path.dirname(__file__), "lib"))

from components import Channel
from components import MembraneValve

nodeStr = ['n1', 'n2', 'n3']

comp1 = Channel([0.200, 0.200, 4], nodeStr[0:1])

comp2 = MembraneValve(0.5, 0.02, nodeStr[1:2])

disp = comp2.getDisplacement()

print('Displacement comp2: ' + str(disp))

# init position
comp1.addFluid(0, 'water', 0.3, 0.1)
print(comp1.fluidStr())

# stroke 2
comp1.moveFluids(1, disp)
print(comp1.fluidStr())

# stroke 3
comp1.moveFluids(1, disp)
print(comp1.fluidStr())

# stroke 4
comp1.moveFluids(1, disp)
print(comp1.fluidStr())

# stroke 5
comp1.moveFluids(1, disp)
print(comp1.fluidStr())