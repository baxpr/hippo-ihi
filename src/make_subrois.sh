#!/usr/bin/env bash

# Reference ${FREESURFER_HOME}/FreeSurferColorLUT.txt

# FIXME need to get correct sets of subregions

# FIXME need to limit to single coronal slice. Let's do this in python
# - just edit compute_extents.py to do the whole job, given the three
# mask images.

subj_dir=SUBJECT
seg=${subj_dir}/mri/lh.hippoAmygLabels.mgz


# Hippocampal head
#    203 parasubiculum
#   233  presubiculum-head
#   235  subiculum-head
#   237  CA1-head
#   239  CA3-head
#   241  CA4-head
#   243  GC-ML-DG-head
#   245  molecular_layer_HP-head
mri_binarize --i ${seg} --o hipphead.mgz \
    --match 203 233 235 237 239 241 243 245

# subicular complex
#   234  presubiculum-body
#   236  subiculum-body
#   238  CA1-body
mri_binarize --i ${seg} --o subicular.mgz \
    --match 234 236 238

# dentate gyrus
#   242  CA4-body
#   244  GC-ML-DG-body
#   246  molecular_layer_HP-body
mri_binarize --i ${seg} --o dentate.mgz \
    --match 242 244 246

# Transform to Tal space without resampling
for img in hipphead.mgz subicular.mgz dentate.mgz; do
    mri_vol2vol \
        --mov ${img} \
        --targ "${FREESURFER_HOME}"/subjects/cvs_avg35_inMNI152/mri/orig/001.mgz \
        --xfm ${subj_dir}/mri/transforms/talairach.xfm \
        --no-resample \
        --o r${img}
done

# Rotate to align long axis with Y, resampling this time. This reduces
# spatial resolution to whatever the atlas is.
rotdeg=-40
for img in rhipphead.mgz rsubicular.mgz rdentate.mgz; do
    mri_vol2vol \
        --mov ${img} \
        --targ "${FREESURFER_HOME}"/subjects/cvs_avg35_inMNI152/mri/orig/001.mgz  \
        --regheader \
        --rot ${rotdeg} 0 0 \
        --nearest \
        --o r${img}
done

# Posterior-most extent of hippocampal head
ext_head=($(compute_extents.py hipphead.mgz))
head_posterior_coord=${ext_head[2]}

# Move back 2mm more and find a 5mm slice
coronal_max=$((head_posterior_coord-2))
coronal_min=$((head_posterior_coord-5))
