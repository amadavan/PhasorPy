import pkg_resources
import re
import requests

import numpy as np
import scipy as sp
import scipy.sparse
import scipy.sparse.linalg

from . import index

__all__ = ['PowerNetwork', 'load_case']


class PowerNetwork:
    def __init__(self, basemva, bus=None, gen=None, gencost=None, branch=None, perunit=True):
        if type(basemva) is dict:
            data = basemva

            self.baseMVA = data['baseMVA']

            self.branch = dict()
            for i, col in enumerate(index.branch):
                self.branch[col] = data['branch'][:, i]

            self.bus = dict()
            for i, col in enumerate(index.bus):
                self.bus[col] = data['bus'][:, i]

            self.gen = dict()
            for i, col in enumerate(index.gen):
                self.gen[col] = data['gen'][:, i]

            self.gencost = dict()
            for i, col in enumerate(index.cost):
                if col == 'COST':
                    self.gencost[col] = data['gencost'][:, i:]
                    break
                self.gencost[col] = data['gencost'][:, i]

        elif self.bus is not None and self.gen is not None and self.gencost is not None and self.branch is not None:
            self.baseMVA = basemva

            self.bus = dict()
            for i, col in enumerate(index.bus):
                self.bus[col] = bus[:, i]

            self.gen = dict()
            for i, col in enumerate(index.gen):
                self.gen[col] = gen[:, i]

            self.gencost = dict()
            for i, col in enumerate(index.cost):
                if col == 'COST':
                    self.gencost[col] = gencost[:, i:]
                    break
                self.gencost[col] = gencost[:, i]

            self.branch = dict()
            for i, col in enumerate(index.branch):
                self.branch[col] = branch[:, i]

        else:
            raise TypeError('Invalid input to power network. Must be either dict or all arguments must be filled.')

        self.n_l = int(np.sum(self.branch['BR_STATUS']))
        self.n_b = len(self.bus['BUS_I'])
        self.n_g = len(self.gen['GEN_BUS'])

        # Per-unit transformations
        if perunit:
            self.bus['PD'] /= self.baseMVA
            self.bus['QD'] /= self.baseMVA
            self.gen['PG'] /= self.baseMVA
            self.gen['QG'] /= self.baseMVA
            self.gen['QMAX'] /= self.baseMVA
            self.gen['QMIN'] /= self.baseMVA
            self.gen['VG'] /= self.baseMVA
            self.gen['PMAX'] /= self.baseMVA
            self.gen['PMIN'] /= self.baseMVA
            self.gen['PC1'] /= self.baseMVA
            self.gen['PC2'] /= self.baseMVA
            self.gen['QC1MIN'] /= self.baseMVA
            self.gen['QC1MAX'] /= self.baseMVA
            self.gen['QC2MIN'] /= self.baseMVA
            self.gen['QC2MAX'] /= self.baseMVA
            self.gen['RAMP_AGC'] /= self.baseMVA
            self.gen['RAMP_10'] /= self.baseMVA
            self.gen['RAMP_30'] /= self.baseMVA
            self.gen['RAMP_Q'] /= self.baseMVA
            self.gencost['COST'] /= self.baseMVA
            self.branch['RATE_A'] /= self.baseMVA
            self.branch['RATE_B'] /= self.baseMVA
            self.branch['RATE_C'] /= self.baseMVA

        # Add nodal value of lost load
        self.voll = 70 * np.max(self.gencost['COST'][:, -2]) * np.ones((self.n_b,))

        self.Bbus = None
        self.Bf = None
        self.Pbusinj = None
        self.Pfinj = None
        self.ISF = None
        self.lineOutages = None

    def setContingencyLimits(self, force=False):
        # Artificially enforce DA and SE limits if unenforced
        if force or np.all(self.branch['RATE_A'] >= self.branch['RATE_B']):
            self.branch['RATE_B'] *= 1.1
        if force or np.all(self.branch['RATE_A'] >= self.branch['RATE_C']):
            self.branch['RATE_C'] *= 1.7

        # Artificially set ramp capacity if unset
        if np.all(self.gen['RAMP_AGC'] == 0):
            self.gen['RAMP_AGC'] = np.ones((self.n_g,)) * 20. / self.baseMVA

    def makeDC(self, setglobal=True):
        '''Construct the parameters for solution of DC optimal power flow problems.

        This file emulates MATPOWER's makeBDC function.
        '''
        if not np.array_equal(self.bus['BUS_I'], np.arange(self.n_b) + 1):
            raise ValueError('Buses must be ordered consecutively.')

        # Determine online branches in order to ignore offline branches
        online = np.where(self.branch['BR_STATUS'] != 0)[0]
        n_online = len(online)

        # for each branch, compute the elements of the branch B matrix and the phase shift "quiescent" injections, where
        #
        #   | Pf |   | Bff Bft |   | Vaf |   | Pfinj |
        #   |    | = |         | * |     | + |       |
        #   | Pt |   | Btf Btt |   | Vat |   | Ptinj |
        #
        b = np.divide(np.ones(n_online), self.branch['BR_X'][online])  # Series susceptance
        tap = self.branch['TAP'][online]  # Set tap ratio
        tap[tap == 0] = 1.  # Set zero tap ratios to 1
        b = np.divide(b, tap)

        # build connection matrix Cft = Cf - Ct for line and from - to buses
        rows = np.concatenate((np.arange(n_online), np.arange(n_online)))  # Set of row indices
        cols = np.concatenate(
            (self.branch['F_BUS'][online] - 1, self.branch['T_BUS'][online] - 1))  # List of 'from' and 'to' buses
        vals = np.concatenate((np.ones((n_online,)), -np.ones((n_online,))))  # Connection value
        Cft = sp.sparse.csc_matrix((vals, (rows, cols)), (n_online, self.n_b))  # Connection matrix

        # build Bf such that Bf * Va is the vector of real branch powers injected at each branch's "from" bus
        vals = np.concatenate((b, -b))
        Bf = sp.sparse.csc_matrix((vals, (rows, cols)), (n_online, self.n_b))

        # build Bbus
        Bbus = sp.sparse.csr_matrix(Cft.transpose().dot(Bf))

        # build phase shift injection vectors
        Pfinj = np.multiply(b, (-self.branch['SHIFT'][online] * np.pi / 180))  # Injected at the from bus
        Pbusinj = Cft.transpose().dot(Pfinj)  # Pbusinj = Cf * Pfinj + Ct * Ptinj;

        # ISF Formulation - assumes Pbusinj is 0
        nonslack_buses = np.where(self.bus['BUS_TYPE'] != 3)[0]
        Bf_ref = Bf[:, nonslack_buses]
        Bbus_ref = Bbus[:, nonslack_buses]
        ISF = Bf_ref.dot(sp.sparse.linalg.spsolve(Bbus_ref.transpose().dot(Bbus_ref), Bbus_ref.transpose()))

        if setglobal:
            # Y-Theta Formulation
            self.Bbus = Bbus
            self.Bf = Bf
            self.Pfinj = Pfinj
            self.Pbusinj = Pbusinj

            # ISF Formulation
            self.ISF = sp.sparse.csc_matrix(ISF)

        return Bbus, Bf, Pbusinj, Pfinj, ISF

    def makeDCLineOutages(self):
        self.lineOutages = []

        for line in range(self.n_l):
            if not self.branch['BR_STATUS'][line]:
                continue

            self.branch['BR_STATUS'][line] = 0

            try:
                Bbus, Bf, _, _, ISF = self.makeDC(False)
                self.lineOutages.append({
                    'prob': 0.001,
                    'Bbus': Bbus,
                    'Bf': Bf,
                    'ISF': ISF,
                    'branch': {
                        'RATE_A': self.branch['RATE_A'][np.arange(self.n_l) != line],
                        'RATE_B': self.branch['RATE_B'][np.arange(self.n_l) != line],
                        'RATE_C': self.branch['RATE_C'][np.arange(self.n_l) != line]
                    }
                })
            except RuntimeError:
                # Ensure that removal of a line does not disconnect graph
                print('Failed to create contingency for line', line)

            self.branch['BR_STATUS'][line] = 1


def load_case(mfile, verbose=0):
    """
    Imports data from Matpower case file (MATLAB m-file).
    """
    # Read m-file and strip MATLAB comments
    if mfile.startswith('http'):
        if verbose: print("Downloading case file: %s." % (mfile))
        response = requests.get(mfile)
        lines = response.text.split('\n')
    elif pkg_resources.resource_exists('phasorpy', 'data/' + mfile):
        if verbose: print("Loading case file: %s." % (mfile))
        with pkg_resources.resource_stream('phasorpy', 'data/' + mfile) as f:
            lines = [str(l, 'utf-8') for l in f.readlines()]
    else:
        if verbose: print("Reading case file: %s." % (mfile))
        with open(mfile, "r") as f:
            lines = f.readlines()

    for k in range(len(lines)): lines[k] = lines[k].split('%')[0]
    case_as_str = "\n".join(lines)

    def str_to_array(s):
        return np.array([[float(v) for v in r.strip().split()] for r in s.strip(';\n\t ').split(';')])

    try:
        baseMVA = re.search("mpc.baseMVA = (\d+)", case_as_str).group(1)
        version = re.search("mpc.version = '(\d+)'", case_as_str).group(1)
        bus_str = re.search("mpc.bus = \[([-\s0-9e.;]+)\]", case_as_str).group(1)
        gen_str = re.search("mpc.gen = \[([-\s0-9e.;Iinf]+)\]", case_as_str).group(1)
        branch_str = re.search("mpc.branch = \[([-\s0-9e.;]+)\]", case_as_str).group(1)
        gencost_str = re.search("mpc.gencost = \[([-\s0-9e.;]+)\]", case_as_str).group(1)
    except:
        raise TypeError("Failed to parse case file.")
    else:
        if re.search('mpc.branch\(', case_as_str) or re.search('mpc.bus\(', case_as_str) or re.search('mpc.gen\(',
                                                                                                      case_as_str):
            raise TypeError("Case file not supported.")

        if version != 2 and version != '2':
            raise TypeError('Invalid case file version. (Requires 2: Provided"', version, '")')

        return PowerNetwork({'baseMVA': float(baseMVA),
                             'bus': str_to_array(bus_str),
                             'gen': str_to_array(gen_str),
                             'gencost': str_to_array(gencost_str),
                             'branch': str_to_array(branch_str)})

def available_cases():
    return pkg_resources.resource_listdir('phasorpy', 'data')