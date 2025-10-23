import numpy as np
from itertools import combinations

def permute_train(spike_train, total_duration):
    """
    Apply a random circular time shift to a single spike train.

    Entire list of spike times are shifted by a random amount between 0 and `total_duration`, 
    and wrapped modulo `total_duration` to keep spikes within the valid time window.

    Parameters
    ----------
    spike_train : array-like
        A single spike train (list or array of spike times, in seconds).
    total_duration : float
        Duration of the recording window (in seconds).

    Returns
    -------
    np.ndarray
        A permuted spike train with spike times randomly shifted and wrapped.
    """

    if len(spike_train) == 0:  # Handle empty spike trains
        return spike_train
    random_offsets = np.random.uniform(0, total_duration, size=len(spike_train))
    permuted_spike_train = (spike_train + random_offsets) % total_duration
    return np.sort(permuted_spike_train)


def permute_train_lst(spike_train_lst, total_duration):
    """
    Wrapper function that applies a different random circular time shift
    to each trial in a list of spike trains.

    Parameters
    ----------
    spike_train_lst : list of array-like
        List of spike trains, each representing one trial.
    total_duration : float
        Duration of the recording window (in seconds).

    Returns
    -------
    list of np.ndarray
        List of permuted spike trains, one per trial.
    """

    return [permute_train(train, total_duration) for train in spike_train_lst]


def calc_firing_rate(spike_train_lst, duration):
    """
    Compute the average firing rate from a list of spike trains.

    Parameters
    ----------
    spike_train_lst : list of array-like
        List of spike trains, each representing one trial.
    duration : float
        Duration of each spike train in seconds.

    Returns
    -------
    float
        Average firing rate across all trials, in Hz (spikes per second).
    """
    spike_counts = np.array([np.sum(np.array(train) <= duration) for train in spike_train_lst])
    return np.mean(spike_counts) / duration



def create_all_pairs(spike_train_lst):
    """
    Create all unique unordered pairs of spike trains.

    Parameters
    ----------
    spike_train_lst : list of array-like
        List of spike trains (one per trial).

    Returns
    -------
    list of tuple
        All unique (i, j) pairs where i < j, excluding self-pairs.
    """
    return list(combinations(spike_train_lst, 2))


