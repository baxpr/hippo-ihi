#!/usr/bin/env python3

import argparse
import nibabel
import numpy
from scipy.spatial.transform import Rotation

parser = argparse.ArgumentParser()
parser.add_argument('--mask_niigz', required=True)
args = parser.parse_args()

img = nibabel.load(args.mask_niigz)

data = img.get_fdata()

idx = numpy.where(data)  # find voxels that are not zeroes
ijk = numpy.vstack(idx).T  # list of arrays to (voxels, 3) array
xyz = nibabel.affines.apply_affine(img.affine, ijk)  # get mm coords

# Coords relative to center of mass
x = xyz[:,0] - numpy.mean(xyz[:,0])
y = xyz[:,1] - numpy.mean(xyz[:,1])
z = xyz[:,2] - numpy.mean(xyz[:,2])

Ixx = numpy.sum(numpy.square(y) + numpy.square(z))
Iyy = numpy.sum(numpy.square(x) + numpy.square(z))
Izz = numpy.sum(numpy.square(x) + numpy.square(y))

Ixy = -numpy.sum(numpy.multiply(x, y))
Ixz = -numpy.sum(numpy.multiply(x, z))
Iyz = -numpy.sum(numpy.multiply(y, z))

# Inertial tensor
Imat = numpy.array([
    [Ixx, Ixy, Ixz],
    [Ixy, Iyy, Iyz],
    [Ixz, Iyz, Izz],
    ])

# SVD of the inertial tensor gives a rotation matrix
# Ue (=Ve.T) to the principal axes
Ue, Se, Ve = numpy.linalg.svd(Imat)

# Use scipy Rotation class to convert to angles.
# No idea what order mri_vol2vol applies its rotations in.
r = Rotation.from_matrix(Ue)
rots = r.as_euler('xyz', degrees=True)
print(f'{rots[0]} {rots[1]} {rots[2]}')

