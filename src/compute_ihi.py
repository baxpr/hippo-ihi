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

import argparse
import nibabel
import numpy
import pandas
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
    parser.add_argument('--hemi', required=True)
    parser.add_argument('--seg_niigz', required=True)
    parser.add_argument('--out_dir', required=True)
    parser.add_argument('--hipphead_vals', default=[203, 233, 235, 237, 239, 241, 243, 245])
    parser.add_argument('--subicular_vals', default=[234])
    parser.add_argument('--dentate_vals', default=[242, 244])
    parser.add_argument('--slice_min_delta', default=2, type=float)
    parser.add_argument('--slice_max_delta', default=6, type=float)
    args = parser.parse_args()

    # Filename tag
    ftag = os.path.basename(args.seg_niigz).strip('.nii.gz')

    # Load the Freesurfer hippocampus segmentations. We need nifti format
    # for the affines to work out correctly.
    seg_img = nibabel.load(args.seg_niigz)

    # Most posterior point of hippocampal head
    hipphead_data = extract_region(seg_img, args.hipphead_vals)
    write_region(seg_img, hipphead_data, 
        os.path.join(args.out_dir, f'{ftag}_hipphead.nii.gz'))
    hipphead_ymin, hipphead_ymax = get_region_extent_on_axis(seg_img, hipphead_data, 1)

    # Sampling slice
    ymax = hipphead_ymin - args.slice_min_delta
    ymin = hipphead_ymin - args.slice_max_delta
    slice_data = numpy.ones(seg_img.header['dim'][1:4])
    slice_data = trim_region_on_axis(seg_img, slice_data, 1, ymin, ymax)
    write_region(seg_img, slice_data, 
        os.path.join(args.out_dir, f'{ftag}_sampleslice.nii.gz'))

    # Whole hippocampus
    hipp_data = extract_region(seg_img, range(1,1000))
    write_region(seg_img, hipp_data, 
        os.path.join(args.out_dir, f'{ftag}_hippocampus.nii.gz'))

    # Subiculum
    subicular_data = extract_region(seg_img, args.subicular_vals)
    subicular_data = trim_region_on_axis(seg_img, subicular_data, 1, ymin, ymax)
    subicular_xmin, subicular_xmax = get_region_extent_on_axis(seg_img, subicular_data, 0)
    write_region(seg_img, subicular_data, 
        os.path.join(args.out_dir, f'{ftag}_subicular_cropped.nii.gz'))
    
    # Subiculum marker volume
    slice_data = numpy.ones(seg_img.header['dim'][1:4])
    slice_data = trim_region_on_axis(seg_img, slice_data, 0, subicular_xmin, subicular_xmax)
    write_region(seg_img, slice_data, 
        os.path.join(args.out_dir, f'{ftag}_subicular_marker.nii.gz'))

    # Dentate
    dentate_data = extract_region(seg_img, args.dentate_vals)
    dentate_data = trim_region_on_axis(seg_img, dentate_data, 1, ymin, ymax)
    dentate_xmin, dentate_xmax = get_region_extent_on_axis(seg_img, dentate_data, 0)
    write_region(seg_img, dentate_data, 
        os.path.join(args.out_dir, f'{ftag}_dentate_cropped.nii.gz'))

    # Dentate marker volume
    slice_data = numpy.ones(seg_img.header['dim'][1:4])
    slice_data = trim_region_on_axis(seg_img, slice_data, 0, dentate_xmin, dentate_xmax)
    write_region(seg_img, slice_data, 
        os.path.join(args.out_dir, f'{ftag}_dentate_marker.nii.gz'))

    # IHI stat
    ihi = (subicular_xmax-subicular_xmin) - (dentate_xmax-dentate_xmin)

    # Output csv
    stats = [{
        'hemisphere': args.hemi,
        'source_file': args.seg_niigz,
        'head_posterior_edge_mm': hipphead_ymin,
        'slice_ymin_mm': ymin,
        'slice_ymax_mm': ymax,
        'subic_xmin_mm': subicular_xmin,
        'subic_xmax_mm': subicular_xmax,
        'dentate_xmin_mm': dentate_xmin,
        'dentate_xmax_mm': dentate_xmax,
        'ihi_stat': ihi,
    }]
    statdf = pandas.DataFrame.from_dict(stats)
    stats_dir = os.path.join(args.out_dir, 'STATS')
    os.makedirs(stats_dir, exist_ok=True)
    statdf.to_csv(os.path.join(stats_dir, f'{args.hemi}-hippo-ihi.csv'), index=False)

