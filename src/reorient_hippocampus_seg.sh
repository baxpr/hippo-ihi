#!/usr/bin/env bash
#
# Use freesurfer Tal transform to reorient hippocampal segmentations
# so the long axis of hippocampus is approximately aligned with the
# A/P axis.

subj_dir=../INPUTS/SUBJECT
out_dir=../INPUTS


# Work in out_dir
cd "${out_dir}"


# Resample nu to hippo atlas
for hemi in 'lh' 'rh'; do

    mri_convert \
        "${subj_dir}"/mri/${hemi}.hippoAmygLabels.mgz \
        ${hemi}.hippoAmygLabels.nii.gz
    
    mri_vol2vol \
        --mov "${subj_dir}"/mri/nu.mgz \
        --targ ${hemi}.hippoAmygLabels.nii.gz \
        --regheader \
        --o "${out_dir}"/${hemi}.nu.nii.gz    

done


# Apply Tal transform. Resampling here is
#   1 - needed to get qforms/sforms sensible
#   2 - bad because it causes inappropriate cropping.
#
# Image is getting cropped to the targ volume, which
# isn't currently aligned with anything useful.
# Make a template and/or use mri_convert --crop, --cropsize, --upsample?
#
# All this is just to make things line up in freeview - fsleyes is ok
# and python/nibabel processing seems ok too. Freeview uses qform
# https://github.com/freesurfer/freesurfer/issues/1025#issuecomment-1320429995
for hemi in 'lh' 'rh'; do

    mri_vol2vol \
        --mov ${hemi}.nu.nii.gz \
        --targ ${hemi}.nu.nii.gz \
        --xfm "${subj_dir}"/mri/transforms/talairach.xfm \
        --regheader \
        --o tal-${hemi}.nu.nii.gz

    mri_vol2vol \
        --mov "${subj_dir}"/mri/${hemi}.hippoAmygLabels.mgz \
        --targ ${hemi}.nu.nii.gz \
        --xfm "${subj_dir}"/mri/transforms/talairach.xfm \
        --regheader \
        --nearest \
        --o tal-${hemi}.hippoAmygLabels.nii.gz

done


# Apply additional rotation I axis to align hippocampus longitudinal axis
# with image Y axis
#
# Rotation matrix for -40 deg on I axis:
#  1.00000   0.00000   0.00000   0.00000;
#  0.00000   0.76604   0.64279   0.00000;
#  0.00000  -0.64279   0.76604   0.00000;
#  0.00000   0.00000   0.00000   1.00000;

rotdeg=-40

for hemi in 'lh' 'rh'; do

    mri_vol2vol \
        --mov tal-${hemi}.nu.nii.gz \
        --targ ${hemi}.nu.nii.gz \
        --rot ${rotdeg} 0 0 \
        --regheader \
        --o rot-tal-${hemi}.nu.nii.gz    

    mri_vol2vol \
        --mov tal-${hemi}.hippoAmygLabels.nii.gz \
        --targ ${hemi}.nu.nii.gz \
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

