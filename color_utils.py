import numpy as np
from scipy import sparse


def rgb_to_yuv(RGB: np.ndarray) -> np.ndarray:
    """
    Converts RGB colors to YUV
    """
    weights = np.array([[0.299, -0.147, 0.615],
                        [0.587, -0.289, -0.515],
                        [0.114, 0.436, -0.1]])
    YUV = np.dot(RGB, weights)
    return YUV


def yuv_to_rgb(YUV: np.ndarray) -> np.ndarray:
    """
    Converts YUV colors to RGB
    """
    weights = np.array([[1.0, 1.0, 1.0],
                        [0., -0.395, 2.032],
                        [1.139, -0.581, 0.]])
    RGB = np.dot(YUV, weights)
    RGB = np.where(RGB > 0, RGB, 0)
    RGB = np.where(RGB <= 1., RGB, 1.)
    return RGB


def get_neighbours(matrix: np.ndarray, idx_matrix: np.ndarray,
                   m: int, n: int) -> np.ndarray:
    """
    Determines which pixels are neighbours and which centers.
    Required to adress the problem with edges (center is not
    allways in the middle nor there is allways 9 elements).
        - matrix - matrix of image
        - idx_matrix - matrix of indexes of image
        - m, n - current position for itteration
    """
    h, w = matrix.shape
    s = np.s_[max(0, m-1):min(m+2, h), max(0, n-1):min(n+2, w)]
    neighbours = matrix[s]
    neighbours_idx = idx_matrix[s].flatten()

    center_idx = np.where(neighbours_idx == idx_matrix[m, n])
    neighbours_idx = np.delete(neighbours_idx, center_idx)

    return neighbours, neighbours_idx, center_idx


def calculate_weights(matrix: np.ndarray, idx: int) -> list:
    """
    Calculate wrights for given matrix of neighbours,
    it assumes center is included.
        - matrix - matrix of neighbours
        - idx - tuple index of center
    """
    # calculating variance
    var = np.mean((matrix - np.mean(matrix))**2)
    # making sure numbers dont overflow
    sigma = max(0.6 * var, 0.000002)

    flat = matrix.flatten()
    center = flat[idx]
    neighbours = np.delete(flat, idx)

    # calculate the weights according to formula from paper
    # w_rs = e^{-(Y(s) - Y(r))^2 / (2 * sigma_r^2)}
    weights = np.exp(-(((neighbours - center)**2)/sigma))

    # normalize
    weights = weights / np.sum(weights)

    return list(-weights)