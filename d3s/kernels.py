#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy as _numpy
from scipy.spatial import distance


class gaussianKernel(object):
    '''Gaussian kernel with bandwidth sigma.'''
    def __init__(self, sigma):
        self.sigma = sigma
    def __call__(self, x, y):
        return _numpy.exp(-_numpy.linalg.norm(x-y)**2/(2*self.sigma**2))
    def __repr__(self):
        return 'Gaussian kernel with bandwidth sigma = %f.' % self.sigma


class laplacianKernel(object):
    '''Laplacian kernel with bandwidth sigma.'''
    def __init__(self, sigma):
        self.sigma = sigma
    def __call__(self, x, y):
        return _numpy.exp(-_numpy.linalg.norm(x-y)/self.sigma)
    def __repr__(self):
        return 'Laplacian kernel with bandwidth sigma = %f.' % self.sigma


class polynomialKernel(object):
    '''Polynomial kernel with degree p and inhomogeneity c.'''
    def __init__(self, p, c=1):
        self.p = p
        self.c = c
    def __call__(self, x, y):
        return (self.c + x@y)**self.p
    def __repr__(self):
        return 'Polynomial kernel with degree p = %f and inhomogeneity c = %f.' % (self.p, self.c)


class stringKernel(object):
    '''
    String kernel implementation based on Marianna Madry's C++ code, see
    https://github.com/mmadry/string_kernel.
    '''
    def __init__(self, kn = 2, l = 0.9):
        self._kn = kn # level of subsequence matching
        self._l  = l  # decay factor

    def __call__(self, x, y):
        return self.evaluate(x, y) / _numpy.sqrt(self.evaluate(x, x)*self.evaluate(y, y))

    def __repr__(self):
        return 'String kernel.'

    def evaluate(self, x, y):
        '''Unnormalized string kernel evaluation.'''
        lx = len(x)
        ly = len(y)
        Kd = _numpy.zeros([2, lx+1, ly+1])

        # dynamic programming
        for i in range(2):
            Kd[i, :, :] = (i + 1) % 2

        # calculate Kd and Kdd
        for i in range(1, self._kn):
            # set the Kd to zero for those lengths of s and t where s (or t) has exactly length i-1 and t (or s)
            # has length >= i-1. L-shaped upside down matrix
            for j in range(i - 1,  lx):
                Kd[i % 2, j, i - 1] = 0
            for j in range(i - 1, ly):
                Kd[i % 2, i - 1, j] = 0
            for j in range(i, lx):
                Kdd = 0
                for m in range(i, ly):
                    if x[j - 1] != y[m - 1]:
                        Kdd = self._l * Kdd
                    else:
                        Kdd = self._l * (Kdd + self._l * Kd[(i + 1) % 2, j - 1, m - 1])
                    Kd[i % 2, j, m] = self._l * Kd[i % 2, j - 1, m] + Kdd

        # calculate value of kernel function evaluation
        s = 0
        for i in range(self._kn, len(x) + 1):
            for j in range(self._kn, len(y)+1):
                if x[i - 1] == y[j - 1]:
                    s += self._l**2 * Kd[(self._kn - 1) % 2, i - 1, j - 1]

        return s


def gramian(X, k):
    '''Compute Gram matrix for training data X with kernel k.'''
    name = k.__class__.__name__
    if name == 'gaussianKernel':
        return _numpy.exp(-distance.squareform(distance.pdist(X.transpose(), 'sqeuclidean'))/(2*k.sigma**2))
    elif name == 'laplacianKernel':
        return _numpy.exp(-distance.squareform(distance.pdist(X.transpose(), 'euclidean'))/k.sigma)
    elif name == 'polynomialKernel':
        return (k.c + X.transpose()@X)**k.p
    elif name == 'stringKernel':
        n = len(X)
        # compute weights for normalization
        d = _numpy.zeros(n)
        for i in range(n):
            d[i] = k.evaluate(X[i], X[i])
        # compute Gram matrix
        G = _numpy.ones([n, n]) # diagonal automatically set to 1
        for i in range(n):
            for j in range(i):
                G[i, j] = k.evaluate(X[i], X[j]) / _numpy.sqrt(d[i]*d[j])
                G[j, i] = G[i, j]
        return G
    else:
        #print('User-defined kernel.')
        if isinstance(X, list): # e.g., for strings
            n = len(X)
            G = _numpy.zeros([n, n])
            for i in range(n):
                for j in range(i+1):
                    G[i, j] = k(X[i], X[j])
                    G[j, i] = G[i, j]
        else:
            n = X.shape[1]
            G = _numpy.zeros([n, n])
            for i in range(n):
                for j in range(i+1):
                    G[i, j] = k(X[:, i], X[:, j])
                    G[j, i] = G[i, j]
        return G


def gramian2(X, Y, k):
    '''Compute Gram matrix for training data X and Y with kernel k.'''
    name = k.__class__.__name__
    if name == 'gaussianKernel':
        #print('Gaussian kernel with sigma = %f.' % k.sigma)
        return _numpy.exp(-distance.cdist(X.transpose(), Y.transpose(), 'sqeuclidean')/(2*k.sigma**2))
    elif name == 'laplacianKernel':
        #print('Laplacian kernel with sigma = %f.' % k.sigma)
        return _numpy.exp(-distance.cdist(X.transpose(), Y.transpose(), 'euclidean')/k.sigma)
    elif name == 'polynomialKernel':
        #print('Polynomial kernel with degree = %f and c = %f.' % (k.p, k.c))
        return (k.c + X.transpose()@Y)**k.p
    elif name == 'stringKernel':
        n = len(X)
        d = _numpy.zeros([n, 2])
        for i in range(n):
            d[i, 0] = k.evaluate(X[i], X[i])
            d[i, 1] = k.evaluate(Y[i], Y[i])
        # compute Gram matrix
        G = _numpy.zeros([n, n])
        for i in range(n):
            for j in range(n):
                G[i, j] = k.evaluate(X[i], Y[j]) / _numpy.sqrt(d[i, 0]*d[j, 1])
        return G
    else:
        #print('User-defined kernel.')
        if isinstance(X, list): # e.g., for strings
            n = len(X)
            G = _numpy.zeros([n, n])
            for i in range(n):
                for j in range(n):
                    G[i, j] = k(X[i], Y[j])
        else:
            n = X.shape[1]
            G = _numpy.zeros([n, n])
            for i in range(n):
                for j in range(n):
                    G[i, j] = k(X[:, i], Y[:, j])
        return G
