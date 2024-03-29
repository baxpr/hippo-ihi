#!/usr/bin/env bash

# Reference ${FREESURFER_HOME}/FreeSurferColorLUT.txt

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
