import numpy as np
import scipy as sp
import scipy.sparse
import stukapy as st


def constructLP(network, formulation, alphap):
    if formulation == 'ISF':
        c, Aub, bub, Cub, Aeq, beq, Ceq, lb, ub = [], [], [], [], [], [], [], [], []
        p0 = 1.

        for lineOutage in network.lineOutages:
            p0 -= lineOutage['prob']

            # State: yk, dgk+ (positive post-generation), dgk- (negative post-generation), ddkp (load shed), slack (flexibility)
            H = sp.sparse.csc_matrix(lineOutage['ISF'])
            Hg = sp.sparse.csc_matrix(lineOutage['ISF'][:, network.gen['GEN_BUS'] - 1])

            # Delta formulation
            ck = alphap * np.concatenate((lineOutage['prob'] * np.ones((1,)),
                                          np.zeros((network.n_g,)),
                                          np.zeros((network.n_g,)),
                                          np.zeros((network.n_b,)),
                                          999999 * np.ones((network.n_g,)),
                                          999999 * np.ones((network.n_l - 1,))))

            # Constraints
            # yk >= c^T dgk+ + c^T dgk- + v^T ddkp + c^T g - z
            # H(g - d) - slack <= f_dal
            # dgk+ - dgk- + g >= 0
            # dgk+ - dgk- + g <= gmax
            # H(g + dgk+ - dgk- + ddkp - s - d) <= f_ste
            # dgk+ - dgk- <= delta g
            # -dgk+ + dgk- <= delta g
            Aubk = sp.sparse.bmat(
                [[-1, network.gencost['COST'][:, -2], network.gencost['COST'][:, -2], network.voll, None, None],
                 [None, None, None, None, None, -sp.sparse.eye(network.n_l - 1)],
                 [None, None, None, None, None, -sp.sparse.eye(network.n_l - 1)],
                 [None, -sp.sparse.eye(network.n_g), sp.sparse.eye(network.n_g), None, -sp.sparse.eye(network.n_g),
                  None],
                 [None, sp.sparse.eye(network.n_g), -sp.sparse.eye(network.n_g), None, -sp.sparse.eye(network.n_g),
                  None],
                 [None, Hg, -Hg, H, None, -sp.sparse.eye(network.n_l - 1)],
                 [None, -Hg, Hg, -H, None, -sp.sparse.eye(network.n_l - 1)],
                 [None, sp.sparse.eye(network.n_g), -sp.sparse.eye(network.n_g), None, -sp.sparse.eye(network.n_g),
                  None],
                 [None, -sp.sparse.eye(network.n_g), sp.sparse.eye(network.n_g), None, -sp.sparse.eye(network.n_g),
                  None]
                 ], 'csc')
            Cubk = sp.sparse.bmat([[-1, 0, network.gencost['COST'][:, -2]],
                                   [None, None, Hg],
                                   [None, None, -Hg],
                                   [None, None, -sp.sparse.eye(network.n_g)],
                                   [None, None, sp.sparse.eye(network.n_g)],
                                   [None, None, Hg],
                                   [None, None, -Hg],
                                   [np.zeros((network.n_g, 1)), None, None],
                                   [np.zeros((network.n_g, 1)), None, None]
                                   ], 'csc')
            bubk = np.concatenate((np.zeros((1,)),
                                   lineOutage['branch']['RATE_C'] + H.dot(network.bus['PD']),
                                   lineOutage['branch']['RATE_C'] - H.dot(network.bus['PD']),
                                   np.zeros((network.n_g,)),
                                   network.gen['PMAX'],
                                   lineOutage['branch']['RATE_B'] + H.dot(network.bus['PD']),
                                   lineOutage['branch']['RATE_B'] - H.dot(network.bus['PD']),
                                   network.gen['RAMP_AGC'] * 5,
                                   network.gen['RAMP_AGC'] * 5
                                   ))

            Aeqk = sp.sparse.bmat([[np.zeros((1, 1)), np.ones((network.n_g,)), -np.ones((network.n_g,)),
                                    np.ones((network.n_b,)), np.zeros((network.n_g,)), np.zeros((network.n_l - 1,))]],
                                  'csc')
            Ceqk = sp.sparse.bmat([[np.zeros((1, 1)), np.zeros((1, 1)), np.ones((network.n_g,))]], 'csc')
            beqk = np.array([np.sum(network.bus['PD'])])

            lbk = np.concatenate((np.zeros((1,)), np.zeros((network.n_g,)), np.zeros((network.n_g,)),
                                  np.zeros((network.n_b,)), np.zeros((network.n_g,)), np.zeros((network.n_l - 1,))))
            ubk = np.concatenate((st.inf * np.ones((1,)), st.inf * np.ones((network.n_g,)),
                                  st.inf * np.ones((network.n_g,)), network.bus['PD'], st.inf * np.ones((network.n_g,)),
                                  st.inf * np.ones((network.n_l - 1,))))

            c.append(ck)
            Aub.append(Aubk)
            bub.append(bubk)
            Cub.append(Cubk)
            Aeq.append(Aeqk)
            beq.append(beqk)
            Ceq.append(Ceqk)
            lb.append(lbk)
            ub.append(ubk)

        c0 = np.concatenate((np.ones((1,)), alphap * p0 * np.ones((1,)), np.zeros((network.n_g,))))

        H = sp.sparse.csc_matrix(network.ISF)
        Hg = sp.sparse.csc_matrix(network.ISF[:, network.gen['GEN_BUS'] - 1])

        Aub0 = sp.sparse.bmat([[-np.ones((1, 1)), -np.ones((1, 1)), network.gencost['COST'][:, -2]],
                               [None, None, Hg],
                               [None, None, -Hg]], 'csc')
        bub0 = np.concatenate((np.zeros((1,)),
                               network.branch['RATE_A'] + H.dot(network.bus['PD']),
                               network.branch['RATE_A'] - H.dot(network.bus['PD'])))

        Aeq0 = sp.sparse.bmat([[np.zeros((1, 1)), np.zeros((1, 1)), np.ones((network.n_g,))]], 'csc')
        beq0 = np.array([np.sum(network.bus['PD'])])

        lb0 = np.concatenate((np.zeros((2,)), np.zeros((network.n_g,))))
        ub0 = np.concatenate((st.inf * np.ones((2,)), network.gen['PMAX']))

        c.append(c0)
        Aub.append(Aub0)
        bub.append(bub0)
        Aeq.append(Aeq0)
        beq.append(beq0)
        lb.append(lb0)
        ub.append(ub0)
    else:
        raise NotImplementedError

    return c, Aub, bub, Cub, Aeq, beq, Ceq, lb, ub


def interpretState(network, x):
    pass
