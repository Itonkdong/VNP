import numpy as np
import pandas as pd
import math
from scipy.stats import mode
from sklearn.preprocessing import StandardScaler


def _scale_data(X_train, X_valid=None, X_test=None):
    """
    Function that scales the data column-wise for training, validation and
    test set.The function uses StandardScaler() fitted on training data.
    Parameters
    ----------
    X_train : pandas.Dataframe
        Dataframe containing training data.
    X_valid : pandas.Dataframe
        Dataframe containing validation data.
    X_test : pandas.Dataframe
        Dataframe contianing test data.
    Returns
    -------
    X_train, X_valid, X_test.
    """
    print("Standardizing data, zero mean, unit variance")
    for i in range(0, X_train.shape[1]):
        scaler = StandardScaler()
        X_train[:, i] = scaler.fit_transform(
            X_train[:, i].reshape(-1, 1)
        ).reshape(-1)
        if X_valid is not None:
            X_valid[:, i] = scaler.transform(
                X_valid[:, i].reshape(-1, 1)
            ).reshape(-1)
        if X_test is not None:
            X_test[:, i] = scaler.transform(
                X_test[:, i].reshape(-1, 1)
            ).reshape(-1)
    if X_valid is None:
        return X_train
    if X_test is None:
        return X_train, X_valid
    return X_train, X_valid, X_test


def slide_data(array, window, step, index=False):
    """
    Returns view of strided array for moving window calculation
    with given window size and step.

    Parameters
    ----------
    array : numpy.ndarray
        Input array with shape (x, 1) or (x,)
    window : int
        Size of the window in samples
    step : int
        Size of the step between windows in samples

    Returns
    -------
    strided : numpy.ndarray
        View of the strided data
    """

    if isinstance(array, pd.Series):
        array = array.values

    if not isinstance(array, np.ndarray):
        raise ValueError("Input type is not appropriate.")

    if array.ndim == 2 and array.shape[1] > 1:
        raise ValueError("Shape of array is not (x, 1) or (x, ).")

    if array.shape[0] < window:
        raise ValueError("Input is smaller than the given window.")

    # Transform to flattened 1D array
    array = np.ravel(array)
    # Get info how many bytes to skip to next element in array
    stride = array.strides[0]
    # Calculate total number of windows that can be created
    win_count = math.floor((len(array) - window + step) / step)
    # Get strided data with appropriate window size and step
    strided = np.lib.stride_tricks.as_strided(
        array, shape=(win_count, window), strides=(stride * step, stride)
    )
    if index:
        # Get the indices of each window
        index_stides = np.arange(
            window - 1, window + (win_count - 1) * step, step
        )
        return strided, index_stides

    return strided


def sliding_window(X, y, setup, index=False):
    """
    Segment time-series data into overlapping windows.

    Parameters:
    - X (numpy.ndarray): Input time-series data (n_samples, n_features).
    - y (numpy.ndarray): Labels for each sample in X.
    - setup (dict): Setup parameters:
        - "win_size" (float): Sliding window size in seconds.
        - "win_slide" (float): Overlap between consecutive windows in seconds.
        - "sampling_frequency" (float): Sampling frequency of the data.

    Returns:
    - X_segmented (numpy.ndarray): Segmented input data
    (n_windows, win_length, n_features).
    - y_segmented (numpy.ndarray): Labels for each window,
    determined by the mode of labels within the window.
    """
    print("Data segmenation into windows.")
    data_cols = []
    win_length = int(setup["win_size"] * setup["sampling_frequency"])
    slide = int(setup["win_slide"] * setup["sampling_frequency"])
    for i in range(0, X.shape[1]):
        slided_data = slide_data(X[:, i], win_length, slide, index=index)
        data_cols.append(slided_data)
    label_col = slide_data(y, win_length, slide)
    # Calculate mode to get the label in each window
    y_segmented = mode(label_col, axis=1, keepdims=True)[0].reshape(-1, 1)
    X_segmented = np.stack(data_cols, axis=2)

    return X_segmented, y_segmented
