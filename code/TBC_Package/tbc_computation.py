import numpy as np
from joblib import Parallel, delayed
from tqdm import tqdm  # Import tqdm for progress bar
from raster_utils import create_all_pairs, calc_firing_rate

def spkd(tli, tlj, duration, cost):
    """
    Compute the Victor-Purpura spike train distance between two spike trains.

    This distance metric evaluates the dissimilarity between two spike trains by calculating
    the minimal cost of transforming one into the other using spike insertions, deletions,
    or temporal shifts. The `cost` parameter controls the penalty for shifting a spike in time.

    Parameters
    ----------
    tli : list of float
        Spike times (in seconds) for the first spike train.
    tlj : list of float
        Spike times (in seconds) for the second spike train.
    duration : float
        Total duration (in seconds) for which to compare spike trains. Spikes beyond this
        are ignored.
    cost : float
        Cost per unit time of shifting a spike. Special cases:
        - If cost == 0: only spike count differences matter.
        - If cost == inf: only spike insertions/deletions are allowed.

    Returns
    -------
    float
        Victor-Purpura distance between the two spike trains.

    Notes:
        Copyright (c) 1999 by Daniel Reich and Jonathan Victor.
        Translated to MATLAB by Daniel Reich from FORTRAN code by Jonathan Victor.
    """
    tli = [x for x in tli if x <= duration]
    tlj = [x for x in tlj if x <= duration]

    nspi = len(tli)
    nspj = len(tlj)

    if cost == 0:
        return abs(nspi - nspj)
    elif cost == float('inf'):
        return nspi + nspj

    # Initialize the cost matrix
    scr = np.zeros((nspi + 1, nspj + 1))

    # Margins with the cost of adding a spike
    scr[:, 0] = np.arange(nspi + 1)
    scr[0, :] = np.arange(nspj + 1)

    # Calculate the costs for aligning spike trains
    if nspi > 0 and nspj > 0:
        for i in range(1, nspi + 1):
            for j in range(1, nspj + 1):
                scr[i, j] = min(
                    scr[i - 1, j] + 1,
                    scr[i, j - 1] + 1,
                    scr[i - 1, j - 1] + cost * abs(tli[i - 1] - tlj[j - 1])
                )

    return scr[nspi, nspj]

def spkd_parallel(tli_list, tlj_list, duration, cost, n_jobs: int = -1):
    """
    Compute Victor-Purpura distances for multiple spike-train pairs in parallel.

    Parameters
    ----------
    tli_list : list of list of float
        List of spike trains to compare (first in each pair).
    tlj_list : list of list of float
        List of spike trains to compare (second in each pair). Must be the same length as `tli_list`.
    duration : float
        Duration in seconds to consider for each spike train.
    cost : float
        Cost parameter passed to `spkd`.
    n_jobs : int, default -1
        Number of parallel workers. Use -1 to use all available cores.

    Returns
    -------
    list of float
        Victor-Purpura distances for each pair.
    """

    results = Parallel(n_jobs=n_jobs)(
        delayed(spkd)(tli, tlj, duration=duration, cost=cost)
        for tli, tlj in zip(tli_list, tlj_list)
    )
    return results

def rand_distances(spike_train_lst, duration, cost, n_jobs=-1):
    """
    Compute SPKD distances between all unordered trial pairs for a single unit.

    Parameters
    ----------
    spike_train_lst : list of list of float
        Spike trains for a single unit (one per trial).
    duration : float
        Duration in seconds for each trial.
    cost : float
        SPKD cost parameter.
    n_jobs : int, default -1
        Number of parallel jobs.

    Returns
    -------
    list of float
        SPKD distances between all unordered trial pairs.
    """

    all_pairs = create_all_pairs(spike_train_lst)

    tli_list = [pair[0] for pair in all_pairs]
    tlj_list = [pair[1] for pair in all_pairs]

    return spkd_parallel(tli_list, tlj_list, duration=duration, cost=cost, n_jobs=n_jobs)


def randSpkd(spike_train_lst, duration, cost, n_jobs=-1, returnList=False):
    """
    Compute mean and standard deviation of SPKD distances for unordered trial pairs.

    Parameters
    ----------
    spike_train_lst : list of list of float
        Spike trains for a single unit (one per trial).
    duration : float
        Duration of each trial in seconds.
    cost : float
        SPKD cost parameter.
    n_jobs : int, default -1
        Number of parallel jobs.
    returnList : bool, default False
        If True, also return list of distances.

    Returns
    -------
    dict
        Contains:
        - 'mean': Mean SPKD
        - 'std': Standard deviation
        - 'firing_rate': Average firing rate
        - 'distances' (optional): List of SPKD values
    """

    dic = {}
    dists = rand_distances(spike_train_lst, duration=duration, cost=cost, n_jobs=n_jobs)
    
    dic['mean'] = np.mean(dists)
    dic['std'] = np.std(dists)
    dic['firing_rate'] = calc_firing_rate(spike_train_lst, duration)

    if returnList:
        dic['distances'] = dists

    return dic


def populationRandSpkd(pop_spike_train_lst, duration, cost, n_jobs=-1, returnList=False):
    """
    Compute random-pair SPKD metrics across a population of units.

    Parameters
    ----------
    pop_spike_train_lst : list of list of list of float
        Spike trains organized as units × trials × spike times.
    duration : float
        Duration of each trial in seconds.
    cost : float
        SPKD cost parameter.
    n_jobs : int, default -1
        Number of parallel jobs.
    returnList : bool, default False
        If True, include per-unit distance lists in the output.

    Returns
    -------
    dict
        Contains:
        - 'mean_list': Mean SPKD per unit
        - 'std_list': Standard deviation per unit
        - 'firing_rate_list': Firing rate per unit
        - 'distance_list' (optional): List of SPKD distances per unit
    """

    M = len(pop_spike_train_lst)
    
    distances_list = []
    means_list = []
    stds_list = []
    firing_rate_list = []
    dic = {}

    for unit in range(M):
        result = randSpkd(pop_spike_train_lst[unit], duration=duration, cost=cost,
                          n_jobs=n_jobs, returnList=True)
        distances_list.append(result['distances'])
        means_list.append(result['mean'])
        stds_list.append(result['std'])
        firing_rate_list.append(result['firing_rate'])

    dic['mean_list'] = means_list
    dic['std_list'] = stds_list
    dic['firing_rate_list'] = firing_rate_list

    if returnList:
        dic['distance_list'] = distances_list

    return dic


def compute_fano_factors(pop_spike_train_lst, duration):
    """
    Compute the Fano factor (variance-to-mean ratio) of spike counts for each unit.

    Parameters
    ----------
    pop_spike_train_lst : list of list of list of float
        Spike trains organized as units × trials × spike times.
    duration : float
        Duration of each trial in seconds.

    Returns
    -------
    list of float
        Fano factor per unit.
    """

    fano_factors = []
    for unit_spike_trains in pop_spike_train_lst:
        spike_counts = [np.sum(np.array(trial) <= duration) for trial in unit_spike_trains]
        spike_counts = np.array(spike_counts)
        mean = np.mean(spike_counts)
        var = np.var(spike_counts, ddof=1)
        fano = var / mean if mean > 0 else np.nan
        fano_factors.append(fano)
    return fano_factors




