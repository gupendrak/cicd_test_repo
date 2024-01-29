import numpy as np
from scipy.spatial.transform import Rotation

from test_module import transform_matrices as tm


def random_transform_matrix():
    rand_tm = tm.identity()
    rand_tm[tm.T_SLICE] = np.random.random_sample(3)
    rand_tm[tm.R_SLICE] = Rotation.from_euler(tm.ROTATION_SEQ, np.random.random_sample(3)).as_matrix()

    return rand_tm


def test_tm_mean():
    tm_b = random_transform_matrix()
    tm_b_rot_eul = np.asarray((0, 0, 1))
    tm_b[tm.R_SLICE] = Rotation.from_euler(tm.ROTATION_SEQ, tm_b_rot_eul).as_matrix()

    mean_tm = tm.mean([tm.identity(), tm_b])
    mean_tm_eul = Rotation.from_matrix(mean_tm[tm.R_SLICE]).as_euler(tm.ROTATION_SEQ)

    assert np.allclose(mean_tm[tm.T_SLICE], tm_b[tm.T_SLICE] / 2)
    assert np.allclose(mean_tm_eul, tm_b_rot_eul / 2)


def test_tm_inv():
    rand_tm = random_transform_matrix()
    rand_tm_inv = tm.inverse(rand_tm)

    assert np.allclose(np.matmul(rand_tm, rand_tm_inv), tm.identity())


def test_tm_6tuple_packing():
    rand_tm = random_transform_matrix()
    rand_tm_roundtrip = tm.unpack(tm.pack(rand_tm))

    assert np.allclose(rand_tm, rand_tm_roundtrip)


def test_tm_7tuple_packing():
    rand_tm = random_transform_matrix()
    rand_tm_roundtrip = tm.from_pos_and_quat(*tm.to_pos_and_quat(rand_tm))

    assert np.allclose(rand_tm, rand_tm_roundtrip)
