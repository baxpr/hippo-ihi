#!/usr/bin/env bash
#
# Use freesurfer Tal transform to reorient hippocampal segmentations
# so the long axis of hippocampus is approximately aligned with the
# A/P axis.

subj_dir=../INPUTS/SUBJECT
out_dir=../INPUTS

regtgt="${FREESURFER_HOME}"/subjects/cvs_avg35_inMNI152/mri/orig/001.mgz

for hemi in 'lh' 'rh'; do

    # Transform to Tal space without resampling. (Alternatively, we could
    # resample at this stage to use the Tal orientation rather than the axis
    # aligned orientation produced below.)
    mri_vol2vol \
        --mov "${subj_dir}"/mri/${hemi}.hippoAmygLabels.mgz \
        --targ "${regtgt}" \
        --xfm "${subj_dir}"/mri/transforms/talairach.xfm \
        --no-resample \
        --o "${out_dir}"/r${hemi}.hippoAmygLabels.mgz

    # Rotate to align long axis with Y, resampling this time. This reduces
    # spatial resolution to whatever the atlas is.
    rotdeg=-40
    mri_vol2vol \
        --mov "${out_dir}"/r${hemi}.hippoAmygLabels.mgz \
        --targ "${FREESURFER_HOME}"/subjects/cvs_avg35_inMNI152/mri/orig/001.mgz  \
        --regheader \
        --rot ${rotdeg} 0 0 \
        --nearest \
        --o "${out_dir}"/rr${hemi}.hippoAmygLabels.nii.gz

done
