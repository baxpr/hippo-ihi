#!/usr/bin/env python3

import argparse
import nibabel
import numpy
import os
import sys

def get_hipp_xyz(img):
    data = img.get_fdata()
    idx = numpy.where((data>0) & (data<1000))  # find hippocampus voxels
    ijk = numpy.vstack(idx).T  # list of arrays to (voxels, 3) array
    xyz = nibabel.affines.apply_affine(img.affine, ijk)  # get mm coords
    return xyz

parser = argparse.ArgumentParser()
parser.add_argument('--img_dir', required=True)
parser.add_argument('--hatag', required=True)
args = parser.parse_args()

lh_img = nibabel.load(os.path.join(args.img_dir,f'lh.{args.hatag}.nii.gz'))
rh_img = nibabel.load(os.path.join(args.img_dir,f'rh.{args.hatag}.nii.gz'))

lh_xyz = get_hipp_xyz(lh_img)
rh_xyz = get_hipp_xyz(rh_img)

# mm coords of all voxels in both hippocampi
xyz = numpy.concatenate((lh_xyz, rh_xyz), axis=0)

print('left affine')
print(lh_img.affine)

print('right affine')
print(rh_img.affine)

print('Shape of xyz')
print(xyz.shape)

print('xyz[0,]')
print(xyz[0,])

# mm coords relative to center of mass
com = numpy.array([
    numpy.mean(xyz[:,0]),
    numpy.mean(xyz[:,1]),
    numpy.mean(xyz[:,2]),
    ])

x = xyz[:,0] - com[0]
y = xyz[:,1] - com[1]
z = xyz[:,2] - com[2]

# Inertia tensor
Ixx = numpy.sum(numpy.square(y) + numpy.square(z))
Iyy = numpy.sum(numpy.square(x) + numpy.square(z))
Izz = numpy.sum(numpy.square(x) + numpy.square(y))

Ixy = -numpy.sum(numpy.multiply(x, y))
Ixz = -numpy.sum(numpy.multiply(x, z))
Iyz = -numpy.sum(numpy.multiply(y, z))

Imat = numpy.array([
    [Ixx, Ixy, Ixz],
    [Ixy, Iyy, Iyz],
    [Ixz, Iyz, Izz],
    ])

print('Imat')
print(Imat)

# Eigenvectors
eigval, eigvec = numpy.linalg.eig(Imat)
print('Raw eigvec')
print(eigvec)
print('eigval')
print(eigval)

# Sort eigenvectors by eigenvalue so that principal axes are ordered
#     x, y, z  =  ~LR, ~AP, ~IS
# This is dependent on the hippocampus structure having smallest 
# moment of inertia around its ~LR axis, second smallest around ~AP, 
# largest around ~IS.
idx = eigval.argsort()
eigval = eigval[idx]
eigvec = eigvec[:,idx]

print('Sorted eigvec')
print(eigvec)
print('Sorted eigval')
print(eigval)

# Eigvec direction is arbitrary and algorithm dependent. So flip signs 
# on principal axes (rows of np_eigvec) to make the largest element positive.
for a in range(0,3):
    idx = numpy.argmax(abs(eigvec[a,]))
    flip = numpy.sign(eigvec[a,idx])
    eigvec[a,] = flip * eigvec[a,]

print('Flipped eigvec')
print(eigvec)
sys.exit(0)

# Post-multiplying an inertial frame coord by eigvec gives the same coord in
# the lab frame. E.g. the lab frame coord of the inertial frame's x axis is
#
#   [1 0 0] * eigvec
#
# In other words, the rows of eigvec are the principal axes in the lab frame.
#
# Pre-multiplying a lab frame coord by eigvec gives the same coord in the
# inertial frame. To re-orient the hippocampus, we want these inertial
# frame coords for each voxel in the structure.

# Rotation
rotmat = eigvec;
rotmat = numpy.hstack(( rotmat, numpy.array([[0], [0], [0]]) ))
rotmat = numpy.vstack(( rotmat, numpy.array([[0, 0, 0, 1]]) ))

transmat0 = numpy.array([
    [1, 0, 0, -com[0]],
    [0, 1, 0, -com[1]],
    [0, 0, 1, -com[2]],
    [0, 0, 0, 1],
    ])
transmatCOM = numpy.array([
    [1, 0, 0, com[0]],
    [0, 1, 0, com[1]],
    [0, 0, 1, com[2]],
    [0, 0, 0, 1],
    ])

# Apply the rotation to the affines and save rotated images.
# We first translate to COM, then rotate, then translate back,
# and the resulting matrix is left side multiplied with the affine
# to produce the new affine.
allmat = numpy.matmul(rotmat, transmat0)
allmat = numpy.matmul(transmatCOM, allmat)

new_lh_affine = numpy.matmul(allmat, lh_img.affine)
new_lh_img = nibabel.Nifti1Image(lh_img.get_fdata(), new_lh_affine)
nibabel.save(new_lh_img, os.path.join(args.img_dir, f'rlh.{args.hatag}.nii.gz'))

new_rh_affine = numpy.matmul(allmat, rh_img.affine)
new_rh_img = nibabel.Nifti1Image(rh_img.get_fdata(), new_rh_affine)
nibabel.save(new_rh_img, os.path.join(args.img_dir, f'rrh.{args.hatag}.nii.gz'))

# Now apply to nu to serve as underlay
nu_img = nibabel.load(os.path.join(args.img_dir,'nu.nii.gz'))
new_nu_affine = numpy.matmul(allmat, nu_img.affine)
new_nu_img = nibabel.Nifti1Image(nu_img.get_fdata(), new_nu_affine)
nibabel.save(new_nu_img, os.path.join(args.img_dir, 'rnu.nii.gz'))

