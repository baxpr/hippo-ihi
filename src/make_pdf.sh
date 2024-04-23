#!/usr/bin/env bash

# How do we get freeview to show us in the right alignment?
# fsleyes does it fine.

# Show an atlas image first to force freeview into atlas space
# alignment, so it won't pick up the voxel grid of the rotated
# subject nu instead.
#
# Sampleslice is not aligned with voxels, so looks not great.

for hemi in lh rh; do

freeview \
    -v "${FREESURFER_HOME}"/subjects/cvs_avg35_inMNI152/mri/nu.mgz:opacity=0 \
    -v rnu.nii.gz:resample=trilinear:smoothed=true \
    -v r${hemi}.${hatag}_sampleslice.nii.gz:colormap=binary:binary_color=yellow:opacity=0.4 \
    -layout 1 -viewport sagittal -zoom 4 -viewsize 400 400 \
    -ras $(get_com.py --roi_niigz r${hemi}.${hatag}_hippocampus.nii.gz --imgval -1) \
    -ss ${hemi}_sag_plain.png

freeview \
    -v "${FREESURFER_HOME}"/subjects/cvs_avg35_inMNI152/mri/nu.mgz:opacity=0 \
    -v rnu.nii.gz:resample=trilinear:smoothed=true \
    -v r${hemi}.${hatag}.nii.gz:colormap=lut \
    -v r${hemi}.${hatag}_sampleslice.nii.gz:colormap=binary:binary_color=yellow:opacity=0.4 \
    -layout 1 -viewport sagittal -zoom 4 -viewsize 400 400 \
    -ras $(get_com.py --roi_niigz r${hemi}.${hatag}_hippocampus.nii.gz --imgval -1) \
    -ss ${hemi}_sag.png

freeview \
    -v "${FREESURFER_HOME}"/subjects/cvs_avg35_inMNI152/mri/nu.mgz:opacity=0 \
    -v rnu.nii.gz:resample=trilinear:smoothed=true \
    -v r${hemi}.${hatag}_subicular_marker.nii.gz:colormap=binary:binary_color=yellow:opacity=0.2 \
    -v r${hemi}.${hatag}_dentate_marker.nii.gz:colormap=binary:binary_color=blue:opacity=0.2 \
    -layout 1 -viewport coronal -zoom 4 -viewsize 400 400 \
    -ras $(get_com.py --roi_niigz r${hemi}.${hatag}_dentate_cropped.nii.gz --imgval -1) \
    -ss ${hemi}_cor_plain.png

freeview \
    -v "${FREESURFER_HOME}"/subjects/cvs_avg35_inMNI152/mri/nu.mgz:opacity=0 \
    -v rnu.nii.gz:resample=trilinear:smoothed=true \
    -v r${hemi}.${hatag}_subicular_cropped.nii.gz:colormap=binary:binary_color=yellow \
    -v r${hemi}.${hatag}_subicular_marker.nii.gz:colormap=binary:binary_color=yellow:opacity=0.2 \
    -v r${hemi}.${hatag}_dentate_cropped.nii.gz:colormap=binary:binary_color=blue \
    -v r${hemi}.${hatag}_dentate_marker.nii.gz:colormap=binary:binary_color=blue:opacity=0.2 \
    -layout 1 -viewport coronal -zoom 4 -viewsize 400 400 \
    -ras $(get_com.py --roi_niigz r${hemi}.${hatag}_dentate_cropped.nii.gz --imgval -1) \
    -ss ${hemi}_cor.png

done

thedate=$(date)

montage -mode concatenate \
    lh_sag_plain.png lh_sag.png lh_cor_plain.png lh_cor.png \
    -tile 2x2 -quality 100 -background white -gravity center \
    -trim -border 10 -bordercolor white -resize 600x page_lh.png
montage -mode concatenate \
    rh_sag_plain.png rh_sag.png rh_cor_plain.png rh_cor.png \
    -tile 2x2 -quality 100 -background white -gravity center \
    -trim -border 10 -bordercolor white -resize 600x page_rh.png

convert \
    -size 1224x1584 xc:white \
    -gravity center \( page_lh.png -resize 1194x1454 \) -geometry +0+0 -composite \
    -gravity NorthEast -pointsize 24 -annotate +20+50 "Left hippocampus IHI" \
    -gravity SouthEast -pointsize 24 -annotate +20+20 "${thedate}" \
    -gravity NorthWest -pointsize 24 -annotate +20+50 "${label_info}" \
    page_lh.png
convert \
    -size 1224x1584 xc:white \
    -gravity center \( page_rh.png -resize 1194x1454 \) -geometry +0+0 -composite \
    -gravity NorthEast -pointsize 24 -annotate +20+50 "Right hippocampus IHI" \
    -gravity SouthEast -pointsize 24 -annotate +20+20 "${thedate}" \
    -gravity NorthWest -pointsize 24 -annotate +20+50 "${label_info}" \
    page_rh.png

# PDF
convert page_lh.png page_rh.png hippo-ihi.pdf

