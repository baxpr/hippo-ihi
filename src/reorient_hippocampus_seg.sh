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


# Apply Tal transform
for hemi in 'lh' 'rh'; do

    mri_vol2vol \
        --mov ${hemi}.nu.nii.gz \
        --targ ${hemi}.nu.nii.gz \
        --xfm "${subj_dir}"/mri/transforms/talairach.xfm \
        --regheader \
        --no-resample \
        --o tal-${hemi}.nu.nii.gz

    mri_vol2vol \
        --mov "${subj_dir}"/mri/${hemi}.hippoAmygLabels.mgz \
        --targ ${hemi}.nu.nii.gz \
        --xfm "${subj_dir}"/mri/transforms/talairach.xfm \
        --regheader \
        --no-resample \
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
        --no-resample \
        --o rot-tal-${hemi}.nu.nii.gz    

    mri_vol2vol \
        --mov tal-${hemi}.hippoAmygLabels.nii.gz \
        --targ ${hemi}.nu.nii.gz \
        --rot ${rotdeg} 0 0 \
        --regheader \
        --no-resample \
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

