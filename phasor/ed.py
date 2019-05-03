import numpy as np
import scipy as sp
import scipy.sparse
import stukapy as st

from . import network as phasorNetwork

__all__ = ['EconomicDispatch']

class EconomicDispatch:
    def __init__(self, network):
        if type(network) is not phasorNetwork.PowerNetwork:
            raise ValueError('Invalid network type. (Required: phasorpy.network.PowerNetwork; Provided: %s)' % type(network))

        self.network = network

        if self.network.Bbus is None:
            self.network.makeDC()

    def constructLP(self, formulation='ISF'):
        if formulation == 'ISF':
            bus_ind = np.array([int(ind - 1) for ind in self.network.gen['GEN_BUS']])
            lineFlow = self.network.ISF[:, bus_ind]

            c = self.network.gencost['COST'][:, -2]
            A_ub = sp.sparse.vstack((lineFlow, -lineFlow))
            b_ub = np.concatenate((self.network.branch['RATE_A'] + self.network.ISF.dot(self.network.bus['PD']),
                                   self.network.branch['RATE_A'] - self.network.ISF.dot(self.network.bus['PD'])), axis=0)
            A_eq = sp.sparse.csr_matrix((1, self.network.n_g))
            A_eq[:, :] = 1
            b_eq = np.array([np.sum(self.network.bus['PD'])])

            lb = np.zeros((self.network.n_g, ))
            ub = self.network.gen['PMAX']

        elif formulation == 'YT':
            genI = sp.sparse.csr_matrix((self.network.n_b, self.network.n_g))
            for i in range(self.network.n_g):
                genI[int(self.network.gen['GEN_BUS'][i])-1, i] = 1.

            powerBalance = sp.sparse.bmat([[genI, -self.network.Bbus]])
            lineFlow = sp.sparse.bmat([[np.zeros((self.network.n_l, self.network.n_g)), self.network.Bf]])
            # lineFlow = sp.sparse.hstack((((self.network.n_l, self.network.n_g)), self.network.Bf))

            c = np.concatenate((self.network.gencost['COST'][:, -2], np.zeros((self.network.n_b, ))), axis=0)
            A_ub = sp.sparse.bmat([[lineFlow], [-lineFlow]])
            b_ub = np.concatenate((self.network.branch['RATE_A'], self.network.branch['RATE_A']), axis=0)
            A_eq = powerBalance
            b_eq = self.network.bus['PD']

            lb = np.concatenate((np.zeros(self.network.n_g, ), -st.inf * np.ones((self.network.n_b, ))))
            ub = np.concatenate((self.network.gen['PMAX'], st.inf * np.ones((self.network.n_b, ))))

        else:
            raise NotImplementedError

        return c, A_ub, b_ub, A_eq, b_eq, lb, ub

    def interpretState(self, x):
        return ''

    def solve(self, formulation='ISF', solveropts=None):
        if solveropts is None:
            opts = st.Options()
        elif type(solveropts) is st.Options:
            opts = solveropts
        else:
            opts = st.Options()
            if type(solveropts) is dict:
                if 'max_iter' in solveropts:
                    opts.max_iter = solveropts['max_iter']
                if 'tol' in solveropts:
                    opts.tol = solveropts['tol']
                if 'x0' in solveropts:
                    opts.x0 = solveropts['x0']
                if 'lp_solver' in solveropts:
                    opts.lp_solver = solveropts['lp_solver']
                if 'qp_solver' in solveropts:
                    opts.qp_solver = solveropts['qp_solver']
                if 'dlp_solver' in solveropts:
                    opts.dlp_solver = solveropts['dlp_solver']

        c, A_ub, b_ub, A_eq, b_eq, lb, ub = self.constructLP(formulation)
        lp = st.LinearProgram(c, A_ub, b_ub, A_eq, b_eq, lb, ub)
        res = st.linprog(lp, opts)

        return res
