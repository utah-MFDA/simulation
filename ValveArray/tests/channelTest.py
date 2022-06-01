
import os, sys
#sys.path.append('./..')
sys.path.append('.')
#sys.path.append(os.path.join(os.path.dirname(__file__), "lib"))

from components import Channel

dev1 = Channel([0.200, 0.200, 4], [2, 3])

dev1.addFluid(0, 'water', 0.3)

print(dev1.fluidStr())

dev1.moveFluids(1, 0.4)

print(dev1.fluidStr())

dev1.addFluid(0, 'water2', 0.2)

dev1.moveFluids(1, 0.3)

print(dev1.fluidStr())

