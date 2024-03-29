#!/usr/bin/env bash

# Affine transform hipposeg to Tal space without losing resolution
mri_vol2vol \
    --mov SUBJECT/mri/lh.hippoAmygLabels.mgz \
    --targ "${FREESURFER_HOME}"/average/mni305.cor.mgz \
    --xfm SUBJECT/mri/transforms/talairach.xfm \
    --no-resample \
    --o r_lh.hippoAmygLabels.mgz

mri_convert SUBJECT/mri/lh.hippoAmygLabels.mgz lh.hippoAmygLabels.nii.gz


# Rotate an MNI brain to check best angle to align hippocampus on A/P axis
rotdeg=-40
mri_vol2vol \
    --mov "${FREESURFER_HOME}"/subjects/cvs_avg35_inMNI152/mri/orig/001.mgz \
    --targ "${FREESURFER_HOME}"/subjects/cvs_avg35_inMNI152/mri/orig/001.mgz \
    --regheader \
    --rot $rotdeg 0 0 \
    --no-resample \
    --o rotated_atlas_${rotdeg}.mgz


# Rotate subject segmentation a fixed amount around left/right axis
mri_vol2vol \
    --mov r_lh.hippoAmygLabels.mgz \
    --targ "${FREESURFER_HOME}"/subjects/cvs_avg35_inMNI152/mri/orig/001.mgz  \
    --regheader \
    --rot ${rotdeg} 0 0 \
    --no-resample \
    --o rr_lh.hippoAmygLabels.mgz

