#!/usr/bin/env bash
#
# Use freesurfer Tal transform to reorient hippocampal segmentations
# so the long axis of hippocampus is approximately aligned with the
# A/P axis.

subj_dir=../INPUTS/SUBJECT
out_dir=../INPUTS


# FIXME Main hassle right now is that mri_vol2vol will not upsample for us,
# but sets the voxel size based on the target template, and I don't have a clear
# way to make those.
#
# In native space we could use the hipp seg itself as a template for resampling
# the nu image, that's fine.
#
# In Tal space we can make a high res template from one of the FS atlases and
# mri_convert with --upsample, --crop, --cropsize.
#
# In the Tal+rotation space - what here?


# Work in out_dir
cd "${out_dir}"


#############################################################################
# Computation in native space. This will be affected by variability in
# head position.

for hemi in 'lh' 'rh'; do

    # For viewing, resample nu with the high res hipp seg as target.
    mri_vol2vol \
        --mov "${subj_dir}"/mri/nu.mgz \
        --targ "${subj_dir}"/mri/${hemi}.hippoAmygLabels.mgz \
        --regheader \
        --o "${out_dir}"/${hemi}.nu.nii.gz  

    # Convert hipp seg to nifti for compatibility with nibabel
    mri_convert \
        "${subj_dir}"/mri/${hemi}.hippoAmygLabels.mgz \
        ${hemi}.hippoAmygLabels.nii.gz

    # Compute metrics of interest
    compute_ihi.py \
        --seg_niigz ${hemi}.hippoAmygLabels.nii.gz --out_dir "${out_dir}" \
        > ${hemi}.hippoAmygLabels-report.txt

done


#############################################################################
# Computation in standard atlas space. Should be less affected by head 
# position, but image Y axis (thus measurement plane) is at ~40 degree angle
# to long axis of hippocampus.

# Rigid body registration of nu to template to get approximately
# atlas-consistent alignment of hippocampus. Mask is needed for this 
# to work.
#
#  Highly Accurate Inverse Consistent Registration: A Robust Approach
# M. Reuter, H.D. Rosas, B. Fischl.  NeuroImage 53(4):1181-1196, 2010.
# http://dx.doi.org/10.1016/j.neuroimage.2010.07.020
# http://reuter.mit.edu/papers/reuter-robreg10.pdf
mri_robust_register \
    --mov "${subj_dir}"/mri/nu.mgz \
    --maskmov "${subj_dir}"/mri/brainmask.mgz \
    --dst "${FREESURFER_HOME}"/subjects/cvs_avg35_inMNI152/mri/nu.mgz \
    --cost NMI \
    --mapmovhdr mni_nu.nii.gz \
    --lta subj_to_mni.lta

lta_convert --inlta subj_to_mni.lta --outmni subj_to_mni.xfm

# Make a high resolution nu to use as target for resampling.
mri_convert \
    --upsample 3 \
    mni_nu.nii.gz \
    h_mni_nu.nii.gz

mri_convert \
    --crop 384 480 366 \
    --cropsize 300 300 300 \
    h_mni_nu.nii.gz \
    ch_mni_nu.nii.gz

# Cropping is critical and an issue at the Tal stage and the rotation
# stage. The crop box center and size are specified in voxels, at the output
# resolution.
#     --crop 384 480 366 \
#    --cropsize 300 300 300 \



# Apply Tal transform
# FIXME Here the Tal space target from MNI image is appropriate
mri_vol2vol \
    --mov hnu.nii.gz \
    --targ template.nii.gz \
    --xfm "${subj_dir}"/mri/transforms/talairach.xfm \
    --regheader \
    --o tal-hnu.nii.gz

for hemi in 'lh' 'rh'; do
    mri_vol2vol \
        --mov "${subj_dir}"/mri/${hemi}.hippoAmygLabels.mgz \
        --targ template.nii.gz \
        --xfm "${subj_dir}"/mri/transforms/talairach.xfm \
        --regheader \
        --nearest \
        --o tal-${hemi}.hippoAmygLabels.nii.gz
done


# Apply additional rotation I axis to align hippocampus longitudinal axis
# with image Y axis
#
# FIXME: Again we need a suitable target template if we resample. Tal is
# not correctly placed
#
# Rotation matrix for -40 deg on I axis:
#  1.00000   0.00000   0.00000   0.00000;
#  0.00000   0.76604   0.64279   0.00000;
#  0.00000  -0.64279   0.76604   0.00000;
#  0.00000   0.00000   0.00000   1.00000;

rotdeg=-40

mri_vol2vol \
    --mov tal-hnu.nii.gz \
    --targ template.nii.gz \
    --rot ${rotdeg} 0 0 \
    --regheader \
    --o rot-tal-hnu.nii.gz 

for hemi in 'lh' 'rh'; do
    mri_vol2vol \
        --mov tal-${hemi}.hippoAmygLabels.nii.gz \
        --targ template.nii.gz \
        --rot ${rotdeg} 0 0 \
        --regheader \
        --nearest \
        --o rot-tal-${hemi}.hippoAmygLabels.nii.gz
done


# Compute metrics of interest
for hemi in 'lh' 'rh'; do


    compute_ihi.py \
        --seg_niigz tal-${hemi}.hippoAmygLabels.nii.gz --out_dir "${out_dir}" \
        > tal-${hemi}.hippoAmygLabels-report.txt

    compute_ihi.py \
        --seg_niigz rot-tal-${hemi}.hippoAmygLabels.nii.gz --out_dir "${out_dir}" \
        > rot-tal-${hemi}.hippoAmygLabels-report.txt

done

