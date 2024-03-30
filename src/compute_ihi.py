#!/usr/bin/env python3
#
# Compute extents of a binary mask on all axes, reporting in mm RAS

# FIXME need to get correct sets of subregions
# Reference ${FREESURFER_HOME}/FreeSurferColorLUT.txt

# FIXME we need to generate combined ROIs BEFORE resampling to
# the rotated space, so we get them at high resolution.
# The resampling is needed to align voxel axes with anatomical
# axes so we can use voxel indexing to do our measurements.
#
# Hmm. Would be better if we can either (1) do the measurements 
# based on the anatomical coords or (2) resample without losing
# resolution (i.e. not with mri_vol2vol).
#
# For a high res template, FS seems to only have 
# average/HippoSF/atlas/AtlasDump.mgz
# Which is 0.25mm voxel, but in the wrong location in space.


import argparse
import nibabel
import numpy
import os

parser = argparse.ArgumentParser()
parser.add_argument('--seg_niigz', required=True)
parser.add_argument('--out_dir', required=True)
args = parser.parse_args()

# Filename tag
ftag = os.path.basename(args.seg_niigz).strip('.nii.gz')

# Load the Freesurfer hippocampus segmentations. We need nifti format
# for the affines to work out correctly.
seg_img = nibabel.load(args.seg_niigz)
seg_data = seg_img.get_fdata()

# Verify that the long axis of this image (Y) is the third voxel coord
# and has '-' orientation. If this check is passed, we can assume the
# third coord is our desired axis and the posterior end of hippocampus
# has lower voxel coordinate.
if (seg_img.affine[2,0:3] != numpy.array([0, -1, 0])).any():
    raise Exception('Cannot handle image geometry')

# Grab the sets of subregions we need
hipphead_vals = [203, 233, 235, 237, 239, 241, 243, 245]
hipphead_data = numpy.zeros(seg_data.shape)
hipphead_data[numpy.isin(seg_data, hipphead_vals, invert=False)] = 1

subicular_vals = [234, 236, 238]
subicular_data = numpy.zeros(seg_data.shape)
subicular_data[numpy.isin(seg_data, subicular_vals)] = 1

dentate_vals = [242, 244, 246]
dentate_data = numpy.zeros(seg_data.shape)
dentate_data[numpy.isin(seg_data, dentate_vals)] = 1

# Range to use for measurements, in voxels (should be 1mm voxel)
locs = numpy.where(hipphead_data>0)
body_posterior_edge = min(locs[2])
meas_kmin = body_posterior_edge - 7
meas_kmax = body_posterior_edge - 2

# Zero out the the ROI images outside the measurement slices
subicular_data[:,:,0:meas_kmin] = 0
subicular_data[:,:,meas_kmax:] = 0
dentate_data[:,:,0:meas_kmin] = 0
dentate_data[:,:,meas_kmax:] = 0

# Write out the measurement slices for later viewing
subicular_cropped_img = nibabel.Nifti1Image(subicular_data, seg_img.affine)
nibabel.save(
    subicular_cropped_img, 
    os.path.join(args.out_dir,f'{ftag}_subicular_cropped.nii.gz'))

dentate_cropped_img = nibabel.Nifti1Image(dentate_data, seg_img.affine)
nibabel.save(
    dentate_cropped_img, 
    os.path.join(args.out_dir,f'{ftag}_dentate_cropped.nii.gz'))

