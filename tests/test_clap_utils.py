import numpy as np

import clap_utils


def test_l2norm_produces_unit_vectors():
    x = np.array([[3.0, 4.0], [1.0, 0.0]])
    normed = clap_utils._l2norm(x)
    assert np.allclose(np.linalg.norm(normed, axis=-1), 1.0)


def test_l2norm_zero_vector_does_not_divide_by_zero():
    x = np.zeros((1, 4))
    normed = clap_utils._l2norm(x)
    assert np.allclose(normed, 0.0)
