# This program allows generation of elementary cellular automata
# for an initial binary state input of arbitrary length for a
# desired number of generations. Various boundary conditions are also
# able to be specified.

# 2022 William Kephart

import numpy as np

class ECA:
    def __init__(self, rule):
        self.rule = rule

    # cellEvo takes as input an ECA and a 3 digit string of a cell and its
    # neighbors and outputs a single 0 or 1 according to the given rule.
    def cellEvo(self, neighborhood):
        return self.rule[7 - int(neighborhood, 2)]

    # timestep takes an ECA, an input state, and 
    # a boundary condition and outputs a child state.
    def timestep(self, state, b_cond):
        cell_arr = []
        
        if (b_cond=='null'):
            for x in range(len(state)-2):
                cell_arr.append(self.cellEvo(state[x:x+3]))
        elif (b_cond=='periodic'):
            y = len(state)
            cell_arr.append(self.cellEvo(state[y-1] + state[:2]))
            for x in range(y-2):
                cell_arr.append(self.cellEvo(state[x:x+3]))
            cell_arr.append(self.cellEvo(state[y-2:y] + state[0]))
                
        child_state = ''.join(cell_arr)
        return child_state

    # N_Gens runs an ECA for N generations.                                     
    def N_Gens(self, state, b_cond, N):
        current_state = state
        gen_arr = []
        for x in range(N):
            gen = np.frombuffer(current_state.encode('ascii'),'u1') - ord('0')
            gen_arr.append(gen)
            current_state = self.timestep(current_state, b_cond)
        return gen_arr
