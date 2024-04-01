#!/usr/bin/env python3
# 
# Get center of mass of cortex ROI, in voxel index. Need to use nifti
# images for transforms to be correct

import argparse
import nibabel
import numpy
import scipy.ndimage
import sys

parser = argparse.ArgumentParser()
parser.add_argument('--roi_niigz', required=True)
parser.add_argument('--imgval', type=int, required=True)
args = parser.parse_args()

img = nibabel.load(args.roi_niigz)
data = img.get_fdata()
roi = numpy.zeros(data.shape)

# COM unweighted
if args.imgval<0:
    roi[data>0] = 1
else:
    roi[data==args.imgval] = 1

# Get COM
com_vox = scipy.ndimage.center_of_mass(roi)
com_world = nibabel.affines.apply_affine(img.affine, com_vox)
print(f'{com_world[0]:0.0f} {com_world[1]:0.0f} {com_world[2]:0.0f}')
