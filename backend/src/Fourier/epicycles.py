import numpy as np


def epicycles_positions(coeffs,freqs,t,K):
    N = len(coeffs)
    #pair freq and coeffs
    pairs = list(zip(freqs,coeffs))
    pairs.sort(key=lambda x:x[0])

    mid = len(pairs)//2
    pairs = pairs[mid-K//2:mid+K//2]

    centers=[]
    ends = []
    pos = 0+0j
    

    for f,c in pairs:
        centers.append(pos)
        pos = pos+c*np.exp(2j*np.pi*f*t*N)
        ends.append(pos)
    return centers,ends