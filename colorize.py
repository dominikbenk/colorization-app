import numpy as np
import color_utils
from scipy import sparse
from scipy.sparse.linalg import spsolve
from tqdm import tqdm


class Colorization():
    """
    Defines the colorization algorithm using optimization
    as described on https://www.cs.huji.ac.il/~yweiss/Colorization/
        - grey - matrix from grey image (RGB)
        - scribble - matrix from scribble image (RGB)
    """
    def __init__(self, grey: np.ndarray, scribble: np.ndarray):
        # rescale
        self.grey = grey / 255.
        self.scribble = scribble / 255.
        # difference mask between gray and scribble
        self.color_mask = (np.sum(abs(
            self.grey - self.scribble), axis=2) > 0)
        # convert to YIQ
        self.Y = color_utils.rgb_to_yuv(self.grey)[:, :, 0]
        self.U = color_utils.rgb_to_yuv(self.scribble)[:, :, 1]
        self.V = color_utils.rgb_to_yuv(self.scribble)[:, :, 2]

    def optimize(self) -> np.ndarray:
        """
        Performs the optimization algorithm.
        Output is the new colorized image (YUV)
        """
        # define variables and shapes
        color_mask = self.color_mask
        Y = self.Y
        U = self.U
        V = self.V
        h, w = Y.shape
        output = np.empty([*Y.shape, 3])
        # Y is the same in output
        output[:, :, 0] = Y
        # initialize lists
        weights = []
        weights_idx = []
        index_pointer = [0]
        # matrix ov indices
        idx_matrix = np.arange(0, h * w).reshape((h, w))
        print('Calculating weight matrix')
        # looping through input image
        for (m, n) in tqdm(np.ndindex(Y.shape)):
            # check if there is no color
            if not color_mask[m, n]:
                # get neighbours and center
                neighbours, neighbours_idx, center_idx =\
                    color_utils.get_neighbours(Y, idx_matrix, m, n)
                # calculate weights and indices
                weights.extend(
                    color_utils.calculate_weights(neighbours, center_idx))
                weights_idx.extend(
                    neighbours_idx)

            weights.append(1)
            weights_idx.append(idx_matrix[m, n])
            # pointer for sparse matrix
            index_pointer.append(len(weights))
        # matrix for optimization
        self.A = sparse.csr_matrix((weights, weights_idx, index_pointer),
                              shape=(h * w, h * w))
        # constraints for optimization
        b_U = np.zeros(h * w)
        b_V = np.zeros(h * w)
        # keep values for colored pixels
        b_U[color_mask.flatten()] = U.flatten()[color_mask.flatten()]
        b_V[color_mask.flatten()] = V.flatten()[color_mask.flatten()]

        # solving the linear equations
        print('Solving 1st chrominance component')
        output[:, :, 1] = spsolve(self.A, b_U).reshape(h, w)
        print('Solving 2nd chrominance component')
        output[:, :, 2] = spsolve(self.A, b_V).reshape(h, w)
        print('Colorization done')

        return output