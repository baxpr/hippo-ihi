#!/usr/bin/env bash
#
# Use freesurfer Tal transform to reorient hippocampal segmentations
# so the long axis of hippocampus is approximately aligned with the
# A/P axis.

subj_dir=../INPUTS/SUBJECT
out_dir=../INPUTS

regtgt="${FREESURFER_HOME}"/subjects/cvs_avg35_inMNI152/mri/orig/001.mgz

rotdeg=-40

# Make resample target from atlas
#mri_vol2vol \
#    --mov "${regtgt}" \
#    --targ "${regtgt}"  \
#    --regheader \
#    --rot ${rotdeg} 0 0 \
#    --no-resample \
#    --o "${out_dir}"/rAtlasT1.nii.gz
#mri_convert \
#    --crop 0 0 -10 -vs 0.3 0.3 0.3 \
#    "${out_dir}"/rAtlasT1.nii.gz \
#    "${out_dir}"/crAtlasT1.nii.gz

# Reorient/resample the hippocampus segmentation
for hemi in 'lh' 'rh'; do

    # Transform to Tal space without resampling. (Alternatively, we could
    # resample at this stage to use the Tal orientation rather than the axis
    # aligned orientation produced below.)
    mri_vol2vol \
        --mov "${subj_dir}"/mri/${hemi}.hippoAmygLabels.mgz \
        --targ "${regtgt}" \
        --xfm "${subj_dir}"/mri/transforms/talairach.xfm \
        --no-resample \
        --o "${out_dir}"/r${hemi}.hippoAmygLabels.nii.gz

    # Rotate to align long axis with Y, resampling this time. This reduces
    # spatial resolution to whatever the atlas is.
    # Resample with --nearest, or not with --no-resample
    mri_vol2vol \
        --mov "${out_dir}"/r${hemi}.hippoAmygLabels.nii.gz \
        --targ "${FREESURFER_HOME}"/subjects/cvs_avg35_inMNI152/mri/orig/001.mgz  \
        --regheader \
        --rot ${rotdeg} 0 0 \
        --no-resample \
        --o "${out_dir}"/rr${hemi}.hippoAmygLabels.nii.gz

done
