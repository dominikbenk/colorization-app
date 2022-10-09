import pytest
import numpy as np
from color_utils import rgb_to_yuv, yuv_to_rgb,\
    get_neighbours, calculate_weights


def test_color_conversions():
    RGB = np.array([100, 200, 100])
    YUV = np.array([0.622, -0.113, -0.202])

    assert (pytest.approx(rgb_to_yuv(RGB / 255.), 0.01) == YUV)
    assert (pytest.approx(yuv_to_rgb(YUV), 0.01) == RGB / 255.)


matrix = np.array([[1, 2, 1],
                   [2, 3, 2],
                   [1, 2, 1]])

mat_idx = np.array([[1, 2, 3],
                    [4, 5, 6],
                    [7, 8, 9]])


@pytest.mark.parametrize(
    'm, n, exp_neighbours, exp_neighbours_idx, exp_center_idx',
    [(0, 0, [[1, 2], [2, 3]], [2, 4, 5],  [0]),
     (0, 2, [[2, 1], [3, 2]], [2, 5, 6],  [1]),
     (1, 1, [[1, 2, 1], [2, 3, 2], [1, 2, 1]],
      [1, 2, 3, 4, 6, 7, 8, 9], [4])])
def test_neighbours(m, n, exp_neighbours, exp_neighbours_idx, exp_center_idx):

    neighbours, neighbours_idx, center_idx =\
        get_neighbours(matrix=matrix, idx_matrix=mat_idx, m=m, n=n)

    assert (exp_neighbours == neighbours).all()
    assert (exp_neighbours_idx == neighbours_idx).all()
    assert exp_center_idx == center_idx[0]


def test_weight_calc():
    w = calculate_weights(matrix, idx=5)
    exp_w = [-0.0075435,
             -0.3207607,
             -0.0075435,
             -0.3207607,
             -0.0075435,
             -0.0075435,
             -0.3207607,
             -0.0075435]
    assert pytest.approx(w, 0.00001) == exp_w