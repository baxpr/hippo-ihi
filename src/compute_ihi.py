#!/usr/bin/env python3
#
# Works with the "world" space coordinate axes per the transform 
# (affine) in the nifti header. Limits to a slice in Y just posterior
# of the hippocampal head, then finds the extent in X of subicular
# and dentate regions as defined below from Freesurfer high resolution
# hippocampus segmentation. 

# REFERENCE: To get mm coords for a list of voxels
# https://neurostars.org/t/extract-voxel-coordinates/7282
# data = img.get_fdata()  # get image data as a numpy array
#idx = numpy.where(data)  # find voxels that are not zeroes
#ijk = numpy.vstack(idx).T  # list of arrays to (voxels, 3) array
#xyz = nibabel.affines.apply_affine(img.affine, ijk)  # get mm coords

# FIXME need to get correct sets of subregions
# Reference ${FREESURFER_HOME}/FreeSurferColorLUT.txt

import argparse
import nibabel
import numpy
import os

def get_voxmm(img):
    dims = img.header['dim'][1:4]
    x = numpy.zeros(dims, dtype=numpy.int16)
    y = numpy.zeros(dims, dtype=numpy.int16)
    z = numpy.zeros(dims, dtype=numpy.int16)
    for i in range(dims[0]):
        for j in range(dims[1]):
            for k in range(dims[2]):
                xyz = nibabel.affines.apply_affine(seg_img.affine, [i, j, k])
                x[i, j, k] = xyz[0]
                y[i, j, k] = xyz[1]
                z[i, j, k] = xyz[2]
    return x, y, z

def region_extent(seg_img, region_vals, ymin, ymax, out_file):

    x, y, z = get_voxmm(seg_img)

    # Create ROI binary mask image
    data = numpy.zeros(seg_img.header['dim'][1:4])
    data[numpy.isin(seg_img.get_fdata(), region_vals)] = 1

    # Zero out ex-slice voxels
    data[y<ymin] = 0
    data[y>ymax] = 0

    # Get min, max x values
    keeps = data>0
    xmin = min(x[keeps])
    xmax = max(x[keeps])

    # Save mask to file
    img = nibabel.Nifti1Image(data, seg_img.affine)
    nibabel.save(img, out_file)
    
    return xmin, xmax


parser = argparse.ArgumentParser()
parser.add_argument('--seg_niigz', required=True)
parser.add_argument('--out_dir', required=True)
args = parser.parse_args()

# Filename tag
ftag = os.path.basename(args.seg_niigz).strip('.nii.gz')

# Load the Freesurfer hippocampus segmentations. We need nifti format
# for the affines to work out correctly.
seg_img = nibabel.load(args.seg_niigz)

# Grab the sets of subregions we need
hipphead_vals = [203, 233, 235, 237, 239, 241, 243, 245]
hipphead_data = numpy.zeros(seg_img.header['dim'][1:4])
hipphead_data[numpy.isin(seg_img.get_fdata(), hipphead_vals)] = 1
hipphead_img = nibabel.Nifti1Image(hipphead_data, seg_img.affine)
nibabel.save(hipphead_img, os.path.join(args.out_dir, f'{ftag}_hipphead.nii.gz'))

hipphead_idx = numpy.where(hipphead_data)
hipphead_ijk = numpy.vstack(hipphead_idx).T
hipphead_xyz = nibabel.affines.apply_affine(seg_img.affine, hipphead_ijk)

# Most posterior point of hippocampal head
headmin = min(hipphead_xyz[:,1])

# Sampling slice
ymax = headmin - 2
ymin = headmin - 3

# Subiculum
subicular_xmin, subicular_xmax = region_extent(
    seg_img, 
    [234, 236, 238], 
    ymin, 
    ymax, 
    os.path.join(args.out_dir, f'{ftag}_subicular.nii.gz')
    )

# Dentate
dentate_xmin, dentate_xmax = region_extent(
    seg_img, 
    [242, 244, 246],
    ymin, 
    ymax, 
    os.path.join(args.out_dir, f'{ftag}_dentate.nii.gz')
    )

# Report
print('In rotated Tal space:')
print(f'  Posterior edge of hippocampal head is y = {headmin:0.2f} mm')
print(f'  Sampling range is y = {ymin:0.2f} mm to {ymax:0.2f} mm')
print(f'  Subiculum is x = {subicular_xmin:0.2f} mm to {subicular_xmax:0.2f} mm')
print(f'  Dentate is x = {dentate_xmin:0.2f} mm to {dentate_xmax:0.2f} mm')

