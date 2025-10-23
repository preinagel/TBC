import numpy as np
import json
import os
from math import log
from .tbc_computation import spkd_parallel
from itertools import combinations


def generate_poisson_unit(FR, duration, N, seed=None):
    """
    Generates a homogeneous Poisson process spike train list

    Each trial is generated using a bin-based method, where spike times 
    are determined by drawing from a Poisson distribution with rate 
    FR (firing rate in spikes per bin). The result is a list of N trials, 
    each represented as a list of spike times in seconds.

    Parameters:
        FR (float): Firing rate.
        duration (float): Duration of each trial in seconds. Default is 1.0.
        N (int): Number of trials to generate. Default is 100.
        seed (int or None): Random seed for reproducibility. Default is None.

    Returns:
        List[List[float]]: List of N spike trains (trials), 
        where each spike train is a list of spike times.
    """

    dt=1e-4

    if seed is not None:
        np.random.seed(seed)
    
    nbins = int(duration / dt)
    r = FR * dt  # probability of spike in each bin
    X = np.random.poisson(r, (N, nbins))  # shape (trials, bins)
    
    spike_trains = [np.where(X[i])[0] * dt for i in range(N)]  # convert to time
    return [list(spikes) for spikes in spike_trains]  # convert to list-of-lists



# === Main estimator ===
def poisson_spkd_estimate(FR, cost, output, duration):
    """
    Analytically estimates the expected SPKD (Victor–Purpura distance) between Poisson spike trains
    without computing actual pairwise distances. This provides a fast and smooth approximation
    of the null distribution for SPKD.

    The model assumes a logistic-shaped sigmoid governed by firing-rate-dependent asymptotes and 
    transition parameters. For a given firing rate λ (in Hz) and cost q, the SPKD per spike is modeled as:

        SPKD(q; λ) = α(λ) + β(λ) / [1 + exp(-γ(λ) * (log10(q) - δ(λ)))]

    where:
        • α(λ) = √(4 / (π * λ))
        • β(λ) = 2 − α(λ)
        • γ(λ) = (6.074 / (λ + 7.299)) + 1.870     (rational decay)
        • δ(λ) = 0.396 * log10(λ + 1.506) + 0.367  (logarithmic growth)

    These expressions were fit using empirical SPKD curves from synthetic Poisson data.
    They allow the function to smoothly interpolate across costs and firing rates.

    Parameters:
        FR (float): Firing rate λ in Hz (spikes per second).
        cost (float): Victor–Purpura cost parameter (q).
        output (str): Whether to return 'per_spike' or 'per_sec' value.
        duration (float): Duration of spike trains in seconds. Used only if output='per_sec'.

    Returns:
        float: Estimated SPKD value, normalized either per spike or per second.
    """

    json_path = 'spkd_shape_params.json'

    if FR == 0:
        return 0.0

    # Load shape parameters from JSON
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"Could not find JSON at {json_path}")
    with open(json_path, 'r') as f:
        data = json.load(f)
    gamma_params = dict(zip(['a', 'b', 'c'], data['gamma']['params']))
    delta_params = dict(zip(['a', 'b', 'c'], data['delta']['params']))

    # Define helper functions within this function
    def gamma_fn(fr):
        a, b, c = gamma_params['a'], gamma_params['b'], gamma_params['c']
        return a / (fr + b) + c

    def delta_fn(fr):
        a, b, c = delta_params['a'], delta_params['b'], delta_params['c']
        return a * log(fr + b) + c

    def alpha_beta_per_spike(fr):
        alpha = np.sqrt(4 / (fr * np.pi))
        beta = 2 - alpha
        return alpha, beta

    def alpha_beta_per_sec(fr):
        alpha = np.sqrt((4 * fr) / np.pi)
        beta = 2 * fr - alpha
        return alpha, beta

    if cost == 0:
        expected_diff = np.sqrt((2 * FR * duration) / np.pi)
        if output == 'per_sec':
            return expected_diff / duration
        elif output == 'per_spike':
            return expected_diff / (FR * duration)
        else:
            raise ValueError("output must be 'per_spike' or 'per_sec'")

    log_cost = np.log10(cost)

    # Choose alpha, beta function based on output type
    if output == 'per_spike':
        alpha, beta = alpha_beta_per_spike(FR)
    elif output == 'per_sec':
        alpha, beta = alpha_beta_per_sec(FR)
    else:
        raise ValueError("output must be 'per_spike' or 'per_sec'")

    gamma = gamma_fn(FR)
    delta = delta_fn(FR)

    exponent = -gamma * (log_cost - delta)
    spkd = alpha + beta / (1 + np.exp(exponent))
    return spkd
