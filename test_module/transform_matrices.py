"""Functions for working with 4x4 transform matrices."""

from typing import Iterable

import numpy as np
from scipy.spatial.transform import Rotation

N = 4
R_SLICE = np.index_exp[:3, :3]
T_SLICE = np.index_exp[:3, 3]

PACKED_LEN = 6
PACKED_T_SLICE = slice(0, 3)
PACKED_R_SLICE = slice(3, 6)

ROTATION_SEQ = "xyz"


def identity():
    """Identity transform matrix."""

    return np.eye(N)


def generate_random_from_mean_and_half_extents(mean_tuple: Iterable[float], half_extents_tuple: Iterable[float]):
    """Generate a random 4x4 transform matrix
    from packed origin and half extents."""

    mean_np, hex_np = np.asarray(mean_tuple), np.asarray(half_extents_tuple)
    return unpack(mean_np - hex_np + 2 * hex_np * np.random.random_sample(PACKED_LEN))


def mean(matrices: Iterable[np.ndarray], weights: Iterable[float] = None):
    """Get the mean of multiple 4x4 transform matrices."""

    if len(matrices) == 1:
        return matrices[0]

    rotations = np.asarray([mat[R_SLICE] for mat in matrices])
    translations = np.asarray([mat[T_SLICE] for mat in matrices])

    mean_tm = identity()
    if weights is None:
        mean_tm[R_SLICE] = Rotation.from_matrix(rotations).mean().as_matrix()
        mean_tm[T_SLICE] = np.mean(translations, axis=0)
    else:
        weights_sum1 = np.asarray(weights) / np.sum(weights)

        mean_tm[R_SLICE] = Rotation.from_matrix(rotations).mean(weights_sum1).as_matrix()
        weighted_translations = [translation * weight for translation, weight in zip(translations, weights_sum1)]
        mean_tm[T_SLICE] = np.sum(weighted_translations, axis=0)

    return mean_tm


def inverse(matrix: np.ndarray):
    """Invert a 4x4 transform matrix."""

    inverted = identity()
    inverted[R_SLICE] = matrix[R_SLICE].T
    inverted[T_SLICE] = -np.matmul(inverted[R_SLICE], matrix[T_SLICE])

    return inverted


def pack(matrix: np.ndarray):
    """Pack to a 6-tuple of position + Euler."""

    euler = Rotation.from_matrix(matrix[R_SLICE]).as_euler(ROTATION_SEQ)
    return matrix[T_SLICE].tolist() + euler.tolist()


def unpack(tup: Iterable[float]):
    """Unpack a 6-tuple of position + Euler."""

    matrix = identity()
    matrix[T_SLICE] = tup[PACKED_T_SLICE]
    matrix[R_SLICE] = Rotation.from_euler(ROTATION_SEQ, tup[PACKED_R_SLICE]).as_matrix()

    return matrix


def to_pos_and_quat(matrix: np.ndarray):
    """4x4 transform matrix to (xyz) position and (xyzw) quaternion."""
    return matrix[T_SLICE], Rotation.from_matrix(matrix[R_SLICE]).as_quat()


def from_pos_and_quat(pos: Iterable[float], quat: Iterable[float]):
    """(xyz) position and (xyzw) quaternion to 4x4 transform matrix."""

    matrix = identity()
    matrix[T_SLICE] = pos
    matrix[R_SLICE] = Rotation.from_quat(quat).as_matrix()

    return matrix


def to_readable_str(matrix: np.ndarray):
    """Generates a string of various representations for human-friendly printout."""

    translation_str = "Translation (xyz): {:.3f} {:.3f} {:.3f}".format(*matrix[T_SLICE])
    euler_str = "Rotation (xyz) (radians): {:.3f} {:.3f} {:.3f}".format(*pack(matrix)[3:])
    quat_str = "Quaternion (xyzw): {:.3f} {:.3f} {:.3f} {:.3f}".format(*to_pos_and_quat(matrix)[1])
    mat_str = "\n".join(["Matrix:"] + ["{:.3f} {:.3f} {:.3f} {:.3f}".format(*row) for row in matrix])

    return "\n".join([translation_str, euler_str, quat_str, mat_str])
