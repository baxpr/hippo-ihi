#!/usr/bin/env bash

# Reference ${FREESURFER_HOME}/FreeSurferColorLUT.txt

# FIXME need to get correct sets of subregions

# FIXME need to limit to single coronal slice

# Hippocampal head
#    203 parasubiculum
#   233  presubiculum-head
#   235  subiculum-head
#   237  CA1-head
#   239  CA3-head
#   241  CA4-head
#   243  GC-ML-DG-head
#   245  molecular_layer_HP-head
mri_binarize --i rr_lh.hippoAmygLabels.mgz --o hipphead.mgz \
    --match 203 233 235 237 239 241 243 245

# Posterior-most extent of hippocampal head
ext_head=($(compute_extents.py hipphead.mgz))
head_posterior_coord=${ext_head[2]}

# Move back 2mm more
coronal_coord=$((head_posterior_coord-2))

# Now we either need to resample so we have a true coronal slice,
# then use compute_extents.py again; or, have some way of finding 
# the subicular and DG extents at the coronal_coord exactly

# Resampling is easy but what target vol should we use? Do we need
# to retain the high spatial resolution?


# subicular complex
#   234  presubiculum-body
#   236  subiculum-body
#   238  CA1-body
mri_binarize --i rr_lh.hippoAmygLabels.mgz --o subicular.mgz \
    --match 234 236 238

# dentate gyrus
#   242  CA4-body
#   244  GC-ML-DG-body
#   246  molecular_layer_HP-body
mri_binarize --i rr_lh.hippoAmygLabels.mgz --o dentate.mgz \
    --match 242 244 246
