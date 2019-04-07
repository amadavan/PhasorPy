import stukapy as st

import numpy as np
import phasor as ph
import phasor.network, phasor.ed, phasor.sced

# Test load from data
case = 'pglib_opf_case30_ieee__api.m'

network = ph.network.load_case(case, True)

# Augment the case
if 'case14_ieee' in case:
    network.gencost['COST'][:, -2] = np.array([20, 25, 35, 40, 45])
    network.gen['PMAX'][2:] += 1
    network.voll = 2 * np.max(network.gencost['COST'][:, -2]) * np.ones((network.n_b, ))

if 'case30_ieee' in case:
    network.gencost['COST'][2:6, -2] = np.array([1.4, 1.8, 1.6, 1.7]) # (wasn't used)
    network.gen['PMAX'][2:6] = 3
    network.branch['RATE_A'][24] *= 1.1
    network.branch['RATE_A'][25] *= 1.2
    network.branch['RATE_A'][26] *= 1.2
    network.branch['RATE_A'][27] *= 1.1
    network.branch['RATE_A'][30] *= 1.2

# Construct necessary network properties
network.setContingencyLimits(True)

# Run economic dispatch for initial solution
ed = ph.ed.EconomicDispatch(network)
res = ed.solve('ISF')

ed = ph.sced.RSCED(network, 0.)
opts = {
    'dlp_solver': st.solver.BENDER,
    'x0': np.append(np.zeros((2,)), res['x']),
    'max_iter': 100
}

# print(opts['x0'])
print(ed.solve('ISF', opts))