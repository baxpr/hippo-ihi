#!/usr/bin/env bash

# How do we get freeview to show us in the right alignment?
# fsleyes does it fine.

# Show an atlas image first to force freeview into atlas space
# alignment, so it won't pick up the voxel grid of the rotated
# subject nu instead.
freeview \
    -v "${FREESURFER_HOME}"/subjects/cvs_avg35_inMNI152/mri/nu.mgz:opacity=0 \
    -v rnu.nii.gz:resample=trilinear:smoothed=true \
    -v rrh.hippoAmygLabels_hippocampus.nii.gz:colormap=binary:binary_color=red:opacity=0.2 \
    -v rrh.hippoAmygLabels_subicular_cropped.nii.gz:colormap=binary:binary_color=yellow \
    -v rrh.hippoAmygLabels_dentate_cropped.nii.gz:colormap=binary:binary_color=blue \
    -v rrh.hippoAmygLabels_sampleslice.nii.gz:colormap=binary:binary_color=blue:opacity=0.4
