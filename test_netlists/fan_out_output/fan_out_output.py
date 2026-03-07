
import os, sys
sys.path.append(os.path.realpath(os.path.dirname(__file__) + '/..'))

import result_gen_script

pins = [
    {'name':'soln1', 'layer':'met9', 'pos':[0, 0]},
    {'name':'soln2', 'layer':'met9', 'pos':[0, 2]},
    {'name':'out1', 'layer':'met9', 'pos':[7, 3]},
]

result_gen_script.main(
    test_name='fan_out_output',
    io_list=pins,
    platform='h.r.3.3',
)