#!/usr/bin/env python3

import argparse
import nibabel
import nilearn.image
import numpy
import os
import sys

def get_hipp_xyz(img, values):
    data = img.get_fdata()
    idx = numpy.where(numpy.isin(data, values))
    ijk = numpy.vstack(idx).T  # list of arrays to (voxels, 3) array
    xyz = nibabel.affines.apply_affine(img.affine, ijk)  # get mm coords
    return xyz

parser = argparse.ArgumentParser()
parser.add_argument('--img_dir', required=True)
parser.add_argument('--maskvals', nargs='+', default=[17, 53], type=int) # 17, 53 default to aseg hippocampus
args = parser.parse_args()

aseg_img = nibabel.load(os.path.join(args.img_dir,f'aparc+aseg.nii.gz'))

xyz = get_hipp_xyz(aseg_img, args.maskvals)

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

# Eigenvectors
eigval, eigvec = numpy.linalg.eig(Imat)

# Sort eigenvectors by eigenvalue so that principal axes are ordered
#     x, y, z  =  ~LR, ~AP, ~IS
# This is dependent on the hippocampus structure having smallest 
# moment of inertia around its ~LR axis, second smallest around ~AP, 
# largest around ~IS.
idx = eigval.argsort()
eigval = eigval[idx]
eigvec = eigvec[:,idx]

# Eigvec direction is arbitrary and algorithm dependent. So flip signs 
# on principal axes (cols of np_eigvec) to make the largest element positive.
for a in range(0,3):
    idx = numpy.argmax(abs(eigvec[:,a]))
    flip = numpy.sign(eigvec[idx,a])
    eigvec[:,a] = flip * eigvec[:,a]

# Pre-multiplying a lab frame coord by eigvec.T gives the same coord in the
# inertial frame. To re-orient the hippocampus, we want these inertial
# frame coords for each voxel in the structure.

# Rotation
rotmat = eigvec.T;
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
allmat = transmatCOM @ rotmat @ transmat0

new_aseg_affine = allmat @ aseg_img.affine
new_aseg_img = nibabel.Nifti1Image(aseg_img.get_fdata(), new_aseg_affine)
nibabel.save(new_aseg_img, os.path.join(args.img_dir, f'raparc+aseg.nii.gz'))

# Now apply to nu to serve as underlay
nu_img = nibabel.load(os.path.join(args.img_dir,'nu.nii.gz'))
new_nu_affine = allmat @ nu_img.affine
new_nu_img = nibabel.Nifti1Image(nu_img.get_fdata(), new_nu_affine)
nibabel.save(new_nu_img, os.path.join(args.img_dir, 'rnu.nii.gz'))

# Now resample in addition to reorienting. 0.5mm voxel to minimize
# information loss
rnew_aseg_img = nilearn.image.resample_img(
    new_aseg_img, 
    target_affine=0.5*numpy.eye(3),
    interpolation='nearest',
    force_resample=True,
    copy_header=True,
    )
nibabel.save(
    nibabel.as_closest_canonical(rnew_aseg_img),
    os.path.join(args.img_dir, f'rraparc+aseg.nii.gz'),
    )

rnew_nu_img = nilearn.image.resample_img(
    new_nu_img, 
    target_affine=0.5*numpy.eye(3),
    interpolation='linear',
    force_resample=True,
    copy_header=True,
    )
nibabel.save(
    nibabel.as_closest_canonical(rnew_nu_img),
    os.path.join(args.img_dir, 'rrnu.nii.gz'),
    )


