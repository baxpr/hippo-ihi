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
    ijk = ijk.reshape(dims[0], dims[1], dims[2], 3)
    xyz = xyz.reshape(dims[0], dims[1], dims[2], 3)

    return ijk, xyz


def extract_region(seg_img, region_vals):
   data = numpy.zeros(seg_img.header['dim'][1:4])
   data[numpy.isin(seg_img.get_fdata(), region_vals)] = 1
   return data


def trim_region_on_axis(seg_xyz, data, axis, minval, maxval):
    data[seg_xyz[:,:,:,axis]<minval] = 0
    data[seg_xyz[:,:,:,axis]>maxval] = 0
    return data


def write_region(seg_img, data, out_file):
    img = nibabel.Nifti1Image(data, seg_img.affine)
    nibabel.save(img, out_file)


def get_xyz_region_extent_on_axis(seg_xyz, data, axis):
    keeps = data>0
    min_xyz = min(seg_xyz[keeps,axis])
    max_xyz = max(seg_xyz[keeps,axis])
    return min_xyz, max_xyz


# Main number crunching
if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--seg_niigz', required=True)
    parser.add_argument('--out_dir', required=True)
    args = parser.parse_args()

    # Filename tag
    ftag = os.path.basename(args.seg_niigz).strip('.nii.gz')

    # Load the Freesurfer aseg. We need nifti format
    # for the affines to work out correctly.
    seg_img = nibabel.load(args.seg_niigz)
    seg_ijk, seg_xyz = get_voxmm(seg_img)
    print(nibabel.aff2axcodes(seg_img.affine))

    # Relevant bits of FreeSurferColorLUT
    #   17    Left-Hippocampus
    #   53    Right-Hippocampus
    # 1007    ctx-lh-fusiform
    # 2007    ctx-rh-fusiform
    # 1016    ctx-lh-parahippocampal 
    # 2016    ctx-rh-parahippocampal

    # Medial and lateral extent of hippocampus in 3d (NOT USED)
    lh_hipp_data = extract_region(seg_img, 17)
    lh_hipp_lat_xyz, lh_hipp_med_xyz = get_xyz_region_extent_on_axis(seg_xyz, lh_hipp_data, 0)
    rh_hipp_data = extract_region(seg_img, 53)
    rh_hipp_med_xyz, rh_hipp_lat_xyz = get_xyz_region_extent_on_axis(seg_xyz, rh_hipp_data, 0)
    print(f'L hipp lat xyz {lh_hipp_lat_xyz}')
    print(f'L hipp med xyz {lh_hipp_med_xyz}')
    print(f'R hipp lat xyz {rh_hipp_lat_xyz}')
    print(f'R hipp med xyz {rh_hipp_med_xyz}')
        
    import sys; sys.exit(0)
    
    # FIXME make parahipp method match the above
    # Anterior and posterior extent of parahippocampus
    # If we're going to use ijk coords to pull a slice, we need to figure out which axis is AP
    # in the ijk coord system
    lh_parahipp_data = extract_region(seg_img, 1016)
    lh_parahipp_post, lh_parahipp_ant = get_region_extent_on_axis(seg_xyz, lh_parahipp_data, 1)
    rh_parahipp_data = extract_region(seg_img, 2016)
    rh_parahipp_post, rh_parahipp_ant = get_region_extent_on_axis(seg_xyz, rh_parahipp_data, 1)
    print(f'L parahipp ant {lh_parahipp_ant}')
    print(f'L parahipp post {lh_parahipp_post}')
    print(f'R parahipp ant {rh_parahipp_ant}')
    print(f'R parahipp post {rh_parahipp_post}')
    
    # Coronal slice to measure C2
    # FIXME are ijk coords consistent in the nifti? We need a slice index from the mm value
    # Then e.g. slice_img = img.slicer[:, :, k:k+1] to get a 2D nifti
    # relevant: nibabel.aff2axcodes
    coronal_slice_C2_ymm = numpy.mean([
        lh_parahipp_post,
        lh_parahipp_ant,
        rh_parahipp_post,
        rh_parahipp_ant,
        ])
    print(coronal_slice_C2_ymm)
    
    # FIXME We are here
    # Find collateral sulcus: voxels within ~2mm of both a parahipp and a fusiform voxel
    # And within ~1mm of the C2 measuring slice
    # Make a collateral sulcus image for review
    # We can use the distance transform in 2D if we resample to a hippocampus-oriented
    # grid (or do the processing in the original grid, but that adds positioning variability)
    # nilearn.image.resample_img with target_affine as computed by the inertia code?
    
    



    # Sampling slice
    ymax = hipphead_ymin - args.slice_min_delta
    ymin = hipphead_ymin - args.slice_max_delta
    slice_data = numpy.ones(seg_img.header['dim'][1:4])
    slice_data = trim_region_on_axis(seg_img, slice_data, 1, ymin, ymax)
    write_region(seg_img, slice_data, 
        os.path.join(args.out_dir, f'{ftag}_sampleslice.nii.gz'))




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
    statdf.to_csv(os.path.join(stats_dir, f'{args.hemi}-hippo-ihi-hires-C3.csv'), index=False)

