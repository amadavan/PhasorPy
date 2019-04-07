import stukapy as st

import phasor.network
from . import _psced, _csced, _rsced

__all__ = ['PSCED', 'CSCED', 'RSCED']

class SCED:
    def __init__(self, network):
        if type(network) is not phasor.network.PowerNetwork:
            raise ValueError('Invalid network type. (Required: phasor.network.PowerNetwork; Provided: %s)' % type(network))

        self.network = network

        if self.network.Bbus is None:
            self.network.makeDC()

        if self.network.lineOutages is None or len(self.network.lineOutages) == 0:
            self.network.makeDCLineOutages()

    def constructLP(self, formulation='ISF'):
        raise NotImplementedError

    def interpretState(self, x):
        raise NotImplementedError

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

        c, A_ub, b_ub, C_ub, A_eq, b_eq, C_eq, lb, ub = self.constructLP(formulation)
        dlp = st.DecomposedLinearProgram(c, A_ub, b_ub, C_ub, A_eq, b_eq, C_eq, lb, ub)
        res = st.linprog(dlp, opts)

        return res


class PSCED(SCED):
    def constructLP(self, formulation='ISF'):
        return _psced.constructLP(self.network, formulation)

    def interpretState(self, x):
        return _psced.interpretState(self.network, x)


class CSCED(SCED):
    def constructLP(self, formulation='ISF'):
        return _csced.constructLP(self.network, formulation)

    def interpretState(self, x):
        return _csced.interpretState(self.network, x)


class RSCED(SCED):
    def __init__(self, network, alpha=0.):
        super().__init__(network)

        assert alpha >= 0. and alpha < 1.
        self.alpha = alpha
        self.alphap = 1./(1. - self.alpha)


    def constructLP(self, formulation='ISF'):
        return _rsced.constructLP(self.network, formulation, self.alphap)

    def interpretState(self, x):
        return _rsced.interpretState(self.network, x)