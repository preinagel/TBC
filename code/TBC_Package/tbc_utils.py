# functions useful for processing temporal barcode project data files
import numpy as np
from warnings import filterwarnings
filterwarnings("ignore")
from pynwb import *

def readNWB(filepath: str):
    """
    Load an NWB file and return the NWBFile object.

    Parameters
    ----------
    filepath : str
        Full path to the `.nwb` file to be read.

    Returns
    -------
    NWBFile
        Parsed NWB file object.

    Raises
    ------
    ValueError
        If the file is not an NWB file (.nwb extension missing).
    """
    if filepath[-4:]!='.nwb':
        raise ValueError("Provide an NWB File to be read") #Check if file is actually nwb
    io = NWBHDF5IO(filepath, mode="r", load_namespaces=True)
    nwb = io.read() # reads nwb file based on HDF5 encoding
    return nwb

def getUnits(nwb):
    """
    Retrieve the Units table from an NWB file.

    Parameters
    ----------
    nwb : NWBFile
        Parsed NWB file object.

    Returns
    -------
    Units
        NWB Units table containing metadata and spike times.

    Raises
    ------
    ValueError
        If the input is not a valid NWB file object.
    """
    try:
        return nwb.units
    except:
        raise ValueError("Please provide an nwb object. Use the readNWB function provided in the module.")
   

def getUnitsSpikeTimes(nwb):
    """
    Extract spike times for all units from an NWB file.

    Parameters
    ----------
    nwb : NWBFile
        Parsed NWB file object.

    Returns
    -------
    list of list of float
        A list where each element contains the spike times for one unit.

    Raises
    ------
    ValueError
        If the input is not a valid NWB file object.
    """
    try:
        return getUnits(nwb)['spike_times'] 
    except:
        raise ValueError("Please provide an nwb object. Use the readNWB function provided in the module.")
    

def getUnitsLocation(nwb):
    """
    Retrieve anatomical locations of recorded units based on peak channels.

    Parameters
    ----------
    nwb : NWBFile
        Parsed NWB file object.

    Returns
    -------
    np.ndarray of str
        Array of anatomical region labels corresponding to each unit’s peak channel.
    """
    units=getUnits(nwb)
    units_peak_channel_id = list(units.peak_channel_id)
    n_units=len(units_peak_channel_id)
    electrodes = nwb.electrodes  
    channelLocations=list(electrodes.location) # anatomic locations of each channel
    channelIDs =list(electrodes.id)  # the id for that channel
    unit_locations=np.zeros((n_units,)).astype(str)
    for i in range(n_units):
        #find the brain region closest to the channel which has the peak value for that unit
        unit_locations[i]=channelLocations[channelIDs.index(units_peak_channel_id[i])] 
    return unit_locations
    

def makeAlignedEvents(spike_times, stim_times, duration: float):
    """
    Align spike times to repeated stimulus onsets.

    Parameters
    ----------
    spike_times : list of float
        Continuous spike times from a single unit, in seconds.
    stim_times : list of float
        Start times of repeated stimulus presentations.
    duration : float
        Duration of each stimulus trial in seconds.

    Returns
    -------
    list of list of float
        Trial-aligned spike times. Each inner list contains spikes relative to stimulus onset.
    """
    nRepeats=len(stim_times) #number of stim_time entries would give us the number of repeats for that stimulus
    events=np.zeros((nRepeats,)).tolist()
    
    for stim_idx, stim_time in enumerate(stim_times): 
        first_spike_in_range, last_spike_in_range = np.searchsorted(spike_times, [stim_time, stim_time+duration])
        spike_times_in_range = np.array(spike_times[first_spike_in_range:last_spike_in_range])  
        spike_times_in_range=spike_times_in_range-stim_time #set trial start as time 0 
        events[stim_idx]=spike_times_in_range.tolist()

    return events