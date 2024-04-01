#!/usr/bin/env python3

import argparse
import nibabel
import numpy
import os

def get_hipp_xyz(img):
    data = img.get_fdata()
    idx = numpy.where((data>0) & (data<1000))  # find hippocampus voxels
    ijk = numpy.vstack(idx).T  # list of arrays to (voxels, 3) array
    xyz = nibabel.affines.apply_affine(img.affine, ijk)  # get mm coords
    return xyz

parser = argparse.ArgumentParser()
parser.add_argument('--img_dir', required=True)
args = parser.parse_args()

lh_img = nibabel.load(os.path.join(args.img_dir,'lh.hippoAmygLabels.nii.gz'))
rh_img = nibabel.load(os.path.join(args.img_dir,'rh.hippoAmygLabels.nii.gz'))

lh_xyz = get_hipp_xyz(lh_img)
rh_xyz = get_hipp_xyz(rh_img)

# mm coords of all voxels in both hippocampi
xyz = numpy.concatenate((lh_xyz, rh_xyz), axis=0)

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

# SVD of the inertial tensor gives a rotation matrix Ue 
# (=Ve.T) to the principal axes
Ue, Se, Ve = numpy.linalg.svd(Imat)

# But we need to re-sort axes and transpose to get the right result.
# What is the principled way to do this?
# As this uses xyz mm coords, the data order of the file is irrelevant.
t = numpy.array([
    [0, 0, 1],
    [0, 1, 0],
    [-1, 0, 0],
])
reUe = numpy.matmul(Ue,t).T

#testmat = numpy.array([
#    [1, 0, 0],
#    [0, .9397, -.3420],
#    [0, .3420, .9397],
#])
#print('testmat'), print(testmat)

# Translate COM to origin
# Rotate
# Translate COM back to position
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
rotmat = reUe;
rotmat = numpy.hstack(( rotmat, numpy.array([[0], [0], [0]]) ))
rotmat = numpy.vstack(( rotmat, numpy.array([[0, 0, 0, 1]]) ))

allmat = numpy.matmul(rotmat, transmat0)
allmat = numpy.matmul(transmatCOM, allmat)

new_lh_affine = numpy.matmul(allmat, lh_img.affine)
new_lh_img = nibabel.Nifti1Image(lh_img.get_fdata(), new_lh_affine)
nibabel.save(new_lh_img, os.path.join(args.img_dir, 'rlh.hippoAmygLabels.nii.gz'))

new_rh_affine = numpy.matmul(allmat, rh_img.affine)
new_rh_img = nibabel.Nifti1Image(rh_img.get_fdata(), new_rh_affine)
nibabel.save(new_rh_img, os.path.join(args.img_dir, 'rrh.hippoAmygLabels.nii.gz'))
