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
import scipy.ndimage


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


def get_region_extent_on_axis(seg_xyz, data, axis):
    keeps = data>0
    min_xyz = min(seg_xyz[keeps,axis])
    max_xyz = max(seg_xyz[keeps,axis])
    return min_xyz, max_xyz


def compute_angle_from_xz(xz):
    center = xz.mean(axis=0)
    _, _, vh = numpy.linalg.svd(xz - center, full_matrices=False)
    direction = vh[0]
    angle = numpy.degrees(numpy.arctan2(direction[1], direction[0]))
    return angle


# Main number crunching
if __name__ == '__main__':

    # The seg image should be sampled on the same grid we're going to extract
    # a slice from - e.g. the post-resampling rotated grid that aligns with the
    # hippocampal longitudinal axis.
    parser = argparse.ArgumentParser()
    parser.add_argument('--seg_niigz', required=True)
    parser.add_argument('--cs_dist_voxels', default=3)
    parser.add_argument('--out_dir', required=True)
    args = parser.parse_args()

    # Filename tag
    ftag = os.path.basename(args.seg_niigz).strip('.nii.gz')

    # Load the Freesurfer aseg. We need nifti format
    # for the affines to work out correctly.
    seg_img = nibabel.load(args.seg_niigz)
    seg_ijk, seg_xyz = get_voxmm(seg_img)
    
    # Following code assumes RAS data order (should be forced by 
    # nibabel.as_closest_canonical when the seg file is created)
    if nibabel.aff2axcodes(seg_img.affine) != ('R', 'A', 'S'):
        raise Exception(f'Non-RAS data ordering in {args.seg_niigz}')
    else:
        print(f'Confirmed RAS data ordering in {args.seg_niigz}')

    # Relevant bits of FreeSurferColorLUT
    #
    #      17    Left-Hippocampus
    #    1007    ctx-lh-fusiform
    #    1016    ctx-lh-parahippocampal 
    #
    #      53    Right-Hippocampus
    #    2007    ctx-rh-fusiform
    #    2016    ctx-rh-parahippocampal

    # C2: Anterior and posterior extent of parahippocampus
    # If we're going to use ijk coords to pull a slice, we need to know which axis is AP
    # in the ijk coord system. For RAS data ordering, it's axis 1 of [0, 1, 2], and lower 
    # values are more posterior.
    lh_parahipp_data = extract_region(seg_img, 1016)
    lh_parahipp_post, lh_parahipp_ant = get_region_extent_on_axis(seg_ijk, lh_parahipp_data, 1)
    rh_parahipp_data = extract_region(seg_img, 2016)
    rh_parahipp_post, rh_parahipp_ant = get_region_extent_on_axis(seg_ijk, rh_parahipp_data, 1)
    
    # C2: voxel index of coronal slice to measure in. Mean A/P center of L and R parahippocampus
    C2slice = int(numpy.round(numpy.mean([
        lh_parahipp_post,
        lh_parahipp_ant,
        rh_parahipp_post,
        rh_parahipp_ant,
        ])))
    
    # C2: reduce the problem to 2D, single slice
    C2slice_img = seg_img.slicer[:, C2slice:C2slice+1, :]
    C2slice_ijk = seg_ijk[:, C2slice:C2slice+1, :]
    C2slice_xyz = seg_xyz[:, C2slice:C2slice+1, :]
    nibabel.save(C2slice_img, os.path.join(args.out_dir, 'C2slice_seg.nii.gz'))
    
    # In the slice, compute distance transform for parahipp and fusiform
    C2slice_data = C2slice_img.get_fdata()

    lh_fus_dist = scipy.ndimage.distance_transform_edt(C2slice_data!=1007)
    lh_fus_dist_img = nibabel.Nifti1Image(lh_fus_dist, C2slice_img.affine)
    nibabel.save(lh_fus_dist_img, os.path.join(args.out_dir, 'lh_fus_dist.nii.gz'))

    lh_parahipp_dist = scipy.ndimage.distance_transform_edt(C2slice_data!=1016)
    lh_parahipp_dist_img = nibabel.Nifti1Image(lh_parahipp_dist, C2slice_img.affine)
    nibabel.save(lh_parahipp_dist_img, os.path.join(args.out_dir, 'lh_parahipp_dist.nii.gz'))
    
    rh_fus_dist = scipy.ndimage.distance_transform_edt(C2slice_data!=2007)
    rh_fus_dist_img = nibabel.Nifti1Image(rh_fus_dist, C2slice_img.affine)
    nibabel.save(rh_fus_dist_img, os.path.join(args.out_dir, 'rh_fus_dist.nii.gz'))

    rh_parahipp_dist = scipy.ndimage.distance_transform_edt(C2slice_data!=2016)
    rh_parahipp_dist_img = nibabel.Nifti1Image(rh_parahipp_dist, C2slice_img.affine)
    nibabel.save(rh_parahipp_dist_img, os.path.join(args.out_dir, 'rh_parahipp_dist.nii.gz'))

    # Collateral sulcus is all voxels near both structures. Drop white matter overlap
    lh_collsulc = numpy.maximum(lh_fus_dist, lh_parahipp_dist) <= args.cs_dist_voxels
    lh_collsulc[C2slice_data==2] = False
    lh_collsulc_img = nibabel.Nifti1Image(lh_collsulc.astype(numpy.int16), C2slice_img.affine)
    nibabel.save(lh_collsulc_img, os.path.join(args.out_dir, 'lh_collsulc.nii.gz'))
    
    rh_collsulc = numpy.maximum(rh_fus_dist, rh_parahipp_dist) <= args.cs_dist_voxels
    rh_collsulc[C2slice_data==41] = False
    rh_collsulc_img = nibabel.Nifti1Image(rh_collsulc.astype(numpy.int16), C2slice_img.affine)
    nibabel.save(rh_collsulc_img, os.path.join(args.out_dir, 'rh_collsulc.nii.gz'))
    
    # Find collateral sulcus mm coordinates and do SVD line fits.
    # Angle from X axis is negative for L hemisphere for RAS data ordering
    lh_collsulc_xz = C2slice_xyz[lh_collsulc][:, [0, 2]]
    lh_collsulc_angle = -compute_angle_from_xz(lh_collsulc_xz)

    rh_collsulc_xz = C2slice_xyz[rh_collsulc][:, [0, 2]]
    rh_collsulc_angle = compute_angle_from_xz(rh_collsulc_xz)

    # Collateral sulcus lateral extent
    lh_collsulc_extent_lat = numpy.min(lh_collsulc_xz[:, 0])
    lh_collsulc_extent_med = numpy.max(lh_collsulc_xz[:, 0])
    rh_collsulc_extent_lat = numpy.max(rh_collsulc_xz[:, 0])
    rh_collsulc_extent_med = numpy.min(rh_collsulc_xz[:, 0])
    
    # Hippocampus lateral extent
    lh_hipp_extent_lat = numpy.min(C2slice_xyz[C2slice_data==17, 0])
    lh_hipp_extent_med = numpy.max(C2slice_xyz[C2slice_data==17, 0])
    rh_hipp_extent_lat = numpy.max(C2slice_xyz[C2slice_data==53, 0])
    rh_hipp_extent_med = numpy.min(C2slice_xyz[C2slice_data==53, 0])

    # Position of collateral sulcus laterally (positive = lateral of hippocampus)
    lh_cs_metric = - lh_collsulc_extent_lat + lh_hipp_extent_lat
    rh_cs_metric = + rh_collsulc_extent_lat - rh_hipp_extent_lat
    
    print(f'lh cs angle degrees  {lh_collsulc_angle}')
    print(f'rh cs angle degrees  {rh_collsulc_angle}')
    print(f'lh cs mm past hippocampus  {lh_cs_metric}')
    print(f'rh cs mm past hippocampus  {rh_cs_metric}')
    
    
    import sys; sys.exit(0)


    # FIXME we are here

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

