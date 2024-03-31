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

    # Compute voxel coordinates
    m = numpy.meshgrid(range(dims[0]), range(dims[1]), range(dims[2]), indexing='ij')

    # Flatten for use with apply_affine
    ijk = numpy.vstack((m[0].flatten(), m[1].flatten(), m[2].flatten())).T

    # Compute mm coords
    xyz = nibabel.affines.apply_affine(seg_img.affine, ijk)

    # Unflatten to match the data array
    xyz = xyz.reshape(dims[0], dims[1], dims[2], 3)

    return xyz


def extract_region(seg_img, region_vals):
   data = numpy.zeros(seg_img.header['dim'][1:4])
   data[numpy.isin(seg_img.get_fdata(), region_vals)] = 1
   return data


def trim_region_on_axis(seg_img, data, axis, minval, maxval):
    xyz = get_voxmm(seg_img)
    data[xyz[:,:,:,axis]<minval] = 0
    data[xyz[:,:,:,axis]>maxval] = 0
    return data


def write_region(seg_img, data, out_file):
    img = nibabel.Nifti1Image(data, seg_img.affine)
    nibabel.save(img, out_file)


def get_region_extent_on_axis(seg_img, data, axis):
    xyz = get_voxmm(seg_img)
    keeps = data>0
    minval = min(xyz[keeps,axis])
    maxval = max(xyz[keeps,axis])
    return minval, maxval


# Main number crunching
if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--seg_niigz', required=True)
    parser.add_argument('--out_dir', required=True)
    args = parser.parse_args()

    # Filename tag
    ftag = os.path.basename(args.seg_niigz).strip('.nii.gz')

    # Load the Freesurfer hippocampus segmentations. We need nifti format
    # for the affines to work out correctly.
    seg_img = nibabel.load(args.seg_niigz)

    # Most posterior point of hippocampal head
    hipphead_vals = [203, 233, 235, 237, 239, 241, 243, 245]
    hipphead_data = extract_region(seg_img, hipphead_vals)
    write_region(seg_img, hipphead_data, 
        os.path.join(args.out_dir, f'{ftag}_hipphead.nii.gz'))
    hipphead_ymin, hipphead_ymax = get_region_extent_on_axis(seg_img, hipphead_data, 1)

    # Sampling slice
    ymax = hipphead_ymin - 2
    ymin = hipphead_ymin - 3

    # Subiculum
    subicular_vals = [234, 236, 238]
    subicular_data = extract_region(seg_img, subicular_vals)
    subicular_data = trim_region_on_axis(seg_img, subicular_data, 1, ymin, ymax)
    subicular_xmin, subicular_xmax = get_region_extent_on_axis(seg_img, subicular_data, 0)
    write_region(seg_img, subicular_data, 
        os.path.join(args.out_dir, f'{ftag}_subicular_cropped.nii.gz'))
    
    # Dentate
    dentate_vals = [242, 244, 246]
    dentate_data = extract_region(seg_img, dentate_vals)
    dentate_data = trim_region_on_axis(seg_img, dentate_data, 1, ymin, ymax)
    dentate_xmin, dentate_xmax = get_region_extent_on_axis(seg_img, dentate_data, 0)
    write_region(seg_img, dentate_data, 
        os.path.join(args.out_dir, f'{ftag}_dentate_cropped.nii.gz'))

    # Report
    print('In rotated Tal space:')
    print(f'  Posterior edge of hippocampal head is y = {hipphead_ymin:0.1f} mm')
    print(f'  Sampling range is y = {ymin:0.1f} mm to {ymax:0.1f} mm')
    print(f'  Subiculum is x = {subicular_xmin:0.1f} mm to {subicular_xmax:0.1f} mm  '
        f'(width {subicular_xmax-subicular_xmin:0.1f} mm)')
    print(f'  Dentate is x = {dentate_xmin:0.1f} mm to {dentate_xmax:0.1f} mm  '
        f'(width {dentate_xmax-dentate_xmin:0.1f} mm)')

