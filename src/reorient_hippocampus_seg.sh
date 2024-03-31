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


# Make a high resolution template to use as target for resampling.
mri_convert \
    --upsample 3 \
    "${FREESURFER_HOME}"/subjects/cvs_avg35_inMNI152/mri/nu_noneck.mgz \
    template.nii.gz

# Cropping is critical and an issue at the Tal stage and the rotation
# stage. The crop box center and size are specified in voxels, at the output
# resolution.
#     --crop 384 480 366 \
#    --cropsize 300 300 300 \


# Resample to template.
# FIXME This should not use the Tal space as target if we resample - we need a high res
# target in the native space
mri_vol2vol \
    --mov "${subj_dir}"/mri/nu.mgz \
    --targ template.nii.gz \
    --regheader \
    --o "${out_dir}"/hnu.nii.gz  
for hemi in 'lh' 'rh'; do
    mri_convert \
        "${subj_dir}"/mri/${hemi}.hippoAmygLabels.mgz \
        ${hemi}.hippoAmygLabels.nii.gz
done


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
        --seg_niigz ${hemi}.hippoAmygLabels.nii.gz --out_dir "${out_dir}" \
        > ${hemi}.hippoAmygLabels-report.txt

    compute_ihi.py \
        --seg_niigz tal-${hemi}.hippoAmygLabels.nii.gz --out_dir "${out_dir}" \
        > tal-${hemi}.hippoAmygLabels-report.txt

    compute_ihi.py \
        --seg_niigz rot-tal-${hemi}.hippoAmygLabels.nii.gz --out_dir "${out_dir}" \
        > rot-tal-${hemi}.hippoAmygLabels-report.txt

done

