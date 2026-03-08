import numpy as np

def to_complex_signal(points):
    return points[:,0]+1j*points[:,1]

def resample_by_arclength(z,num_samples=3000):
    dz = np.diff(z)
    lengths = np.abs(dz)
    s = np.concatenate([[0],np.cumsum(lengths)])
    s/=s[-1]

    t_new = np.linspace(0,1,num_samples)
    z_real = np.interp(t_new,s,z.real)
    z_imag = np.interp(t_new,s,z.imag)

    return z_real+1j*z_imag


def fourier_coefficients(z):
    z = z-np.mean(z)
    N = len(z)
    coeffs = np.fft.fft(z)/N
    freqs = np.fft.fftfreq(N)
    return coeffs,freqs

# def sort_by_magnitude(coeffs,freqs):
#     idx = np.argsort(-np.abs(coeffs))
#     return coeffs[idx],freqs[idx]



def reconstruct(coeffs,freqs,K):
    # z =0
    # for c,f in zip(coeffs,freqs):
    #     z+= c* np.exp(2j* np.pi*f*t*len(coeffs))

    # return np.fft.ifft(coeffs*len(coeffs))

    N = len(coeffs)
    truncated = np.zeros_like(coeffs)
    truncated[:K] = coeffs[:K]
    truncated[-K:] = coeffs[-K:]
    return np.fft.ifft(truncated*N)

