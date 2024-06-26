import numpy as np
from copy import deepcopy
import matplotlib.pyplot as plt 
from scipy import signal
from scipy.ndimage import uniform_filter

def find_signal(data):
    """
    Find the most prominent peak in the given data.

    Parameters:
    ----------
    data : array-like
        Input data array in which to find the signal.

    Returns:
    -------
    int
        The index of the most prominent peak in the data.
    """
    data_copy = deepcopy(data)
    data_copy[data_copy<0] = 0
    #data_copy[data_copy>5*np.nanstd(data_copy)]= 0
    size = data_copy.shape
    if data_copy.shape[0]>800:
        mask = np.ones(size[0], dtype=bool)
        I = np.r_[0:200, 800:1000]
        mask[I]=False
        data_copy = data_copy * mask
    if np.all(data_copy==0):
        return np.nan
    #why this works with 10?
    window =signal.windows.general_gaussian(10, p=1, sig=5)
    filtered = signal.convolve(window, data_copy)
    filtered = (np.average(data_copy) / np.average(filtered)) * filtered
    filtered = np.roll(filtered,0)
    #just to avoid negatives that are not ussefull to do this
    filtered[filtered<0] = 0
    peaks, _ = signal.find_peaks(filtered)
    prominences = signal.peak_prominences(filtered, peaks)[0]
    return  peaks[np.argmax(prominences)] - (filtered.shape[0]-data.shape[0])


def guess_picks_image(image,objects_guess=2,plot=False):
    """
    Guess the locations of peaks in a 2D image.

    Parameters:
    ----------
    image : array-like
        2D input image.
    
    objects_guess : int, optional, default=2
        Number of peaks to guess.
    
    plot : bool, optional, default=False
        Whether to plot the intermediate results.

    Returns:
    -------
    array-like
        Indices of the guessed peaks.
    """
    
    data = deepcopy(image)
    data[data<0] = 0
    if np.all(data==0):
        return np.nan*np.ones(objects_guess)
    #why this works with 2?
    window =signal.windows.general_gaussian(2, p=1, sig=5)
    filtered = signal.convolve(window, data)
    filtered = (np.average(data) / np.average(filtered)) * filtered
    filtered = np.roll(filtered,-(filtered.shape[0]-data.shape[0]))
    #just to avoid negatives that are not ussefull to do this
    filtered[filtered<0] = 0
    peaks, _ = signal.find_peaks(filtered)
    #print(peaks)
    prominences = signal.peak_prominences(filtered, peaks)[0]
    sorted_indices = np.argsort(prominences)[::-1][:objects_guess]
    if plot:
        plt.plot(window)
        plt.show()
        plt.plot(filtered)
        plt.plot(data)
        plt.show()
    picks =  np.array([peaks[i] for i in sorted_indices])  + (filtered.shape[0]-data.shape[0])
    if len(picks)<objects_guess:
        return np.array(list(picks)+[np.nan]*(objects_guess-len(picks)))
    return picks




def gaussian(x, center, height, sigma):
    """
    Gaussian distribution function.

    Parameters:
    ----------
    x : array-like
        Input array.
    
    center : float
        Center of the Gaussian peak.
    
    height : float
        Height of the Gaussian peak.
    
    sigma : float
        Standard deviation of the Gaussian peak.

    Returns:
    -------
    array-like
        Gaussian distribution evaluated at x.
    """
    return height * np.exp(-(x - center)**2 / (2 * sigma**2))


def moffat(x,center,height,alpha,sigma):
    """
    Moffat distribution function.

    Parameters:
    ----------
    x : array-like
        Input array.
    
    center : float
        Center of the Moffat peak.
    
    height : float
        Height of the Moffat peak.
    
    alpha : float
        Alpha parameter of the Moffat function.
    
    sigma : float
        Sigma parameter of the Moffat function.

    Returns:
    -------
    array-like
        Moffat distribution evaluated at x.
    """
    
    return height*(1+((x-center)**2/(sigma**2)))**-alpha

def smooth_boxcar(y, filtwidth,var=None, verbose=True):
        """
        Apply a boxcar smoothing to the spectrum.

        Note: This function is not authored by me.

        Parameters:
        ----------
        y : array-like
            Input spectrum to be smoothed.
        
        filtwidth : int
            Width of the smoothing filter.
        
        var : array-like or None, optional
            Variance spectrum for inverse variance weighting. If None, uniform weighting is used.
        
        verbose : bool, optional, default=True
            Whether to print verbose messages.

        Returns:
        -------
        tuple
            Smoothed spectrum and smoothed variance (or None if var is None).
        """
        
        """
        this is not mine 
        Does a boxcar smooth of the spectrum.
        The default is to do inverse variance weighting, using the variance
         spectrum if it exists.
        The other default is not to write out an output file.  This can be
        changed by setting the outfile parameter.
        """

        """ Set the weighting """
        if var is not None:
            if verbose:
                pass
                #print('Weighting by the inverse variance')
            wht = 1.0 / var
        else:
            if filtwidth==0:
                 ysmooth,varsmooth=y,None
                 return ysmooth, varsmooth
            if verbose:
                pass
                #print('Uniform weighting')
            wht = 0.0 * y + 1.0
        """ Smooth the spectrum and variance spectrum """
        yin = wht * y
        smowht = uniform_filter(wht, filtwidth)
        ysmooth = uniform_filter(yin, filtwidth)
        ysmooth /= smowht
        if var is not None:
            varsmooth = 1.0 / (filtwidth * smowht)
        else:
            varsmooth = None

        return ysmooth, varsmooth