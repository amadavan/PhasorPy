__all__ = ['branch', 'bus', 'cost', 'gen', 'help']

branch = ['F_BUS', 'T_BUS', 'BR_R', 'BR_X', 'BR_B', 'RATE_A', 'RATE_B', 'RATE_C', 'TAP', 'SHIFT', 'BR_STATUS',
          'ANGMIN', 'ANGMAX']

bus = ['BUS_I', 'BUS_TYPE', 'PD', 'QD', 'GS', 'BS', 'BUS_AREA', 'VM', 'VA', 'BASE_KV', 'ZONE', 'VMAX', 'VMIN']

cost = ['MODEL', 'STARTUP', 'SHUTDOWN', 'NCOST', 'COST']

gen = ['GEN_BUS', 'PG', 'QG', 'QMAX', 'QMIN', 'VG', 'MBASE', 'GEN_STATUS', 'PMAX', 'PMIN', 'PC1', 'PC2',
       'QC1MIN', 'QC1MAX', 'QC2MIN', 'QC2MAX', 'RAMP_AGC', 'RAMP_10', 'RAMP_30', 'RAMP_Q', 'APF']


def help():

    branchData = '\n'.join(['F_BUS'.ljust(12) + 'f, from bus number',
                            'T_BUS'.ljust(12) + 't, to bus number',
                            'BR_R'.ljust(12) + 'r, resistance (p.u.)',
                            'BR_X'.ljust(12) + 'x, reactance (p.u.)',
                            'BR_B'.ljust(12) + 'b, total line charging susceptance (p.u.)',
                            'RATE_A'.ljust(12) + 'rateA, MVA rating A (long term rating)',
                            'RATE_B'.ljust(12) + 'rateB, MVA rating B (short term rating)',
                            'RATE_C'.ljust(12) + 'rateC, MVA rating C (emergency rating)',
                            'TAP'.ljust(12) + 'ratio, transformer off nominal turns ratio',
                            'SHIFT'.ljust(12) + 'angle, transformer phase shift angle (degrees)',
                            'BR_STATUS'.ljust(12) + 'initial branch status, 1 - in service, 0 - out of service',
                            'ANGMIN'.ljust(12) + 'minimum angle difference, angle(Vf) - angle(Vt) (degrees)',
                            'ANGMAX'.ljust(12) + 'maximum angle difference, angle(Vf) - angle(Vt) (degrees)'])

    busData = '\n'.join(['BUS_I'.ljust(12) + 'bus number (1 to 29997)',
                         'BUS_TYPE'.ljust(12) + 'bus type',
                         'PD'.ljust(12) + 'Pd, real power demand (MW)',
                         'QD'.ljust(12) + 'Qd, reactive power demand (MVAr)',
                         'GS'.ljust(12) + 'Gs, shunt conductance (MW at V = 1.0 p.u.)',
                         'BS'.ljust(12) + 'Bs, shunt susceptance (MVAr at V = 1.0 p.u.)',
                         'BUS_AREA'.ljust(12) + 'area number, 1-100',
                         'VM'.ljust(12) + 'Vm, voltage magnitude (p.u.)',
                         'VA'.ljust(12) + 'Va, voltage angle (degrees)',
                         'BASE_KV'.ljust(12) + 'baseKV, base voltage (kV)',
                         'ZONE'.ljust(12) + 'zone, loss zone (1-999)',
                         'VMAX'.ljust(12) + 'maxVm, maximum voltage magnitude (p.u.)',
                         'VMIN'.ljust(12) + 'minVm, minimum voltage magnitude (p.u.)'])

    costData = '\n'.join(['MODEL'.ljust(12) + 'cost model, 1 - piecewise linear, 2 - polynomial',
                          'STARTUP'.ljust(12) + 'startup cost in US dollars',
                          'SHUTDOWN'.ljust(12) + 'shutdown cost in US dollars',
                          'NCOST'.ljust(12) + 'number of cost coefficients to follow for polynomial cost function, or number of data points for piecewise linear',
                          'COST'.ljust(12) + 'vector of cost parameters'])

    genData = '\n'.join(['GEN_BUS'.ljust(12) + 'bus number',
                         'PG'.ljust(12) + 'Pg, real power output (MW)',
                         'QG'.ljust(12) + 'Qg, reactive power output (MVAr)',
                         'QMAX'.ljust(12) + 'Qmax, maximum reactive power output at Pmin (MVAr)',
                         'QMIN'.ljust(12) + 'Qmin, minimum reactive power output at Pmin (MVAr)',
                         'VG'.ljust(12) + 'Vg, voltage magnitude setpoint (p.u.)',
                         'MBASE'.ljust(12) + 'mBase, total MVA base of this machine, defaults to baseMVA',
                         'GEN_STATUS'.ljust(12) + 'status, 1 - machine in service, 0 - machine out of service',
                         'PMAX'.ljust(12) + 'Pmax, maximum real power output (MW)',
                         'PMIN'.ljust(12) + 'Pmin, minimum real power output (MW)',
                         'PC1'.ljust(12) + 'Pc1, lower real power output of PQ capability curve (MW)',
                         'PC2'.ljust(12) + 'Pc2, upper real power output of PQ capability curve (MW)',
                         'QC1MIN'.ljust(12) + 'Qc1min, minimum reactive power output at Pc1 (MVAr)',
                         'QC1MAX'.ljust(12) + 'Qc1max, maximum reactive power output at Pc1 (MVAr)',
                         'QC2MIN'.ljust(12) + 'Qc2min, minimum reactive power output at Pc2 (MVAr)',
                         'QC2MAX'.ljust(12) + 'Qc2max, maximum reactive power output at Pc2 (MVAr)',
                         'RAMP_AGC'.ljust(12) + 'ramp rate for load following/AGC (MW/min)',
                         'RAMP_10'.ljust(12) + 'ramp rate for 10 minute reserves (MW)',
                         'RAMP_30'.ljust(12) + 'ramp rate for 30 minute reserves (MW)',
                         'RAMP_Q'.ljust(12) + 'ramp rate for reactive power (2 sec timescale) (MVAr/min)',
                         'APF'.ljust(12) + 'area participation factor'])

    print('Network case data is stored in a set of dictionary objects representing the typical MATPOWER arrays.'
          'These dictionaries have the following keys.')

    print('\033[1m BRANCH DATA \033[0m')
    print(branchData)

    print('\033[1m BUS DATA \033[0m')
    print(busData)

    print('\033[1m COST DATA \033[0m')
    print(costData)

    print('\033[1m GENERATOR DATA \033[0m')
    print(genData)