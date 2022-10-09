import pytest
import numpy as np
import colorize
from color_utils import yuv_to_rgb


grey = np.array([[[100, 100, 100],
                  [200, 200, 200],
                  [100, 100, 100]],
                 [[100, 100, 100],
                  [200, 200, 200],
                  [100, 100, 100]],
                 [[100, 100, 100],
                  [200, 200, 200],
                  [100, 100, 100]]])

scribble = np.array([[[100, 100, 100],
                      [100, 200, 100],
                      [100, 100, 100]],
                     [[100, 100, 100],
                      [100, 200, 100],
                      [100, 100, 100]],
                     [[100, 100, 100],
                      [100, 200, 100],
                      [100, 100, 100]]])

colorization = colorize.Colorization(grey, scribble)


def test_colorization_inst():
    assert isinstance(colorization, colorize.Colorization)


def test_colorization_grey():
    assert (colorization.grey * 255. == grey / 1.).all()


mask = np.array([[False,  True, False],
                 [False,  True, False],
                 [False,  True, False]])


def test_colorization_mask():
    assert (colorization.color_mask == mask).all()


exp_A = [[1., -0.00127, 0., -0.9975, -0.00127, 0., 0., 0., 0.]]


def test_linear_equations():
    colorization.optimize()
    assert pytest.approx(colorization.A.todense()[0], 0.01) == exp_A


colorized_exp = np.array([[[41.34, 141.34, 41.28],
                           [141.34, 241.34, 141.28],
                           [41.34, 141.34, 41.28]],
                          [[41.34, 141.34, 41.28],
                           [141.34, 241.34, 141.28],
                           [41.34, 141.34, 41.28]],
                          [[41.34, 141.34, 41.28],
                           [141.34, 241.34, 141.28],
                           [41.34, 141.34, 41.28]]])


def test_output():
    colorized = colorization.optimize()
    colorized = yuv_to_rgb(colorized) * 255
    assert colorized_exp == pytest.approx(colorized, 0.01)