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

x = xyz[:,0]
y = xyz[:,1]
z = xyz[:,2]

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
#print(Imat)
#print(' ')

# SVD of the inertial tensor gives a rotation matrix
# Ue (=Ve.T) to the principal axes
Ue, Se, Ve = numpy.linalg.svd(Imat)
print(' ')
print('Rotation matrix')
print(Ue)
print('Singular values')
print(Se)


# Same as SVD, just ordered by incr eigval instead of decr
ev, ec = numpy.linalg.eig(Imat)
print(' ')
print('Eigenvectors')
print(ec)
print('Eigenvalues')
print(ev)


# Use scipy Rotation class to convert to angles
# These angles don't make sense, so I either don't understand
# Ue as a rotation matrix, or I don't understand the Euler 
# angle formulation. Is it wanting to rotate long axis to X because
# long axis has the highest moment of inertia? I want it on Y.
#
# At any rate the 'y' angle seems to be the one we want to apply
# on x axis. Haven't figured out the others.
#
# No idea what order mri_vol2vol applies its rotations in.
r = Rotation.from_matrix(ec)
print('Euler angles')
print(r.as_euler('xyz', degrees=True))


m = [
    [0, 0, 1],
    [1, 0, 0],
    [0, 1, 0],
    ]
rtest = Rotation.from_matrix(m)
#print(m)
#print(' ')
#print(rtest.as_euler('xyz', degrees=True))
#print(' ')
