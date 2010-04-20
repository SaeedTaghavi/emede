#! /usr/bin/env python

import numpy as np
from itertools import combinations, product

def LJ(r2):
    ir2 = 1.0 / r2
    ir6 = 1.0 / r2**3
    return 48 * ir2 * ir6 * (ir6 - 0.5)
    
def latt(L, D, N):
    n = np.ceil(N**(1.0 / D))
    l = L / n
    print l
    ax = np.linspace(0, L, n, endpoint=False)
    axs = [ax] * D
    x0 = np.array([l/2.0] * D)
    result = np.array(list(product(*axs))) + x0
    rr = range(len(result))
    indices = []
    for i in range(len(result)-N):
        pos = np.random.randint(len(rr)-i)
        print i, pos, rr[pos], rr
        indices.append(rr[pos])
        rr[pos], rr[len(rr)-i-1] = rr[len(rr)-i-1], rr[pos]  
    print indices
    return np.delete(result, indices, axis=0)
    
def mic(r, L):
    mic = np.abs(r) > L / 2.0
    r[mic] = r[mic] - L * np.sign(r)[mic]

class MD(object):
    
    def __init__(self, size=10, D=2, nparts=8, T=1, cutoff=4.0, dt=0.001):
        self.size = size
        self.D = D
        self.nparts = nparts
        self.cutoff = cutoff
        self.cutoff2 = self.cutoff**2
        self.ecut = 4.0 * (1.0 / cutoff**12 - 1.0 / cutoff**6)
        self.dt = dt
        self.positions = latt(size, D, nparts)
        self.velocities = np.random.random((nparts,D))
        vcm = np.sum(self.velocities, axis=0) / nparts
        self.velocities -= vcm
        v2 = np.sum(self.velocities**2) / nparts
        self.velocities *= np.sqrt(D * T / v2)
        self.forces = np.zeros((nparts,D))
        self._start_acums()
    
    def _start_acums(self):
        self._e = None
        self._ek = None
        self._ep = None
        
    @property
    def T(self):
        return np.sum(self.velocities**2) / (self.D * len(self.velocities))
        
    @property
    def EK(self):
        if self._ek is None:
            self._ek = 0.5 * np.sum(self.velocities**2)
        return self._ek
        
    @property
    def EP(self):
        if self._ep is None:
            self._ep = 0.0
            for i, j in combinations(xrange(len(self.positions)), 2):
                r = self.positions[i] - self.positions[j]
                mic(r, self.size)
                r2 = np.sum(r**2)
                if r2 <= self.cutoff2:
                    ir6 = 1.0 / r2**3
                    self._ep += 4.0 * ir6 * (ir6 - 1) - self.ecut
        return self._ep
        
    @property
    def E(self):
        ek = self.EK
        ep = self.EP
        return ek+ep, ek, ep
        
    @property
    def VCM(self):
        return np.sum(self.velocities, axis=0) / self.nparts
        
    def check_distances(self):
        min = self.size
        for i, j in combinations(xrange(len(self.positions)), 2):
            r = self.positions[i] - self.positions[j]
            r = r - self.size * np.floor_divide(r, self.size)
            r = np.sum(r**2)**0.5
            if r < min:
                min = r
        print 'min=', min
    
    def do_step(self):
        self._start_acums()
        self.positions += self.velocities * self.dt + 0.5 * self.forces * self.dt**2
        self.positions = self.positions - np.floor_divide(self.positions, self.size)
        self.velocities += 0.5 * self.forces * self.dt
        self.forces = np.zeros((self.nparts,self.D))
        for i, j in combinations(xrange(len(self.positions)), 2):
            r = self.positions[i] - self.positions[j]
            mic(r, self.size)
            r2 = np.sum(r**2)
            if r2 <= self.cutoff2:
                ff = LJ(r2)
                self.forces[i] += ff * r
                self.forces[j] -= ff * r
        self.velocities += 0.5 * self.forces * self.dt
            
    
if __name__ == '__main__':
    print 'HEllO WORld'
    
