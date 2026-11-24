#!/usr/bin/env bash

freeview \
    -nocursor \
    -v C2slice_t1.nii.gz \
    -v slicerois.nii.gz:colormap=lut:opacity=0.6 \
    -v lh_collsulc.nii.gz:colormap=binary:binary_color=red:opacity=0.6 \
    -v rh_collsulc.nii.gz:colormap=binary:binary_color=red:opacity=0.6 \
    -layout 1 -viewport coronal -zoom 4 -viewsize 800 400 \
    -ras $(get_com.py --roi_niigz slicerois.nii.gz --imgval -1) \
    -ss qcslice.png

freeview \
    -nocursor \
    -v rrnu.nii.gz \
    -v C2slice_mask.nii.gz:colormap=binary:binary_color=red \
    -v rraparc+aseg.nii.gz:colormap=lut:opacity=0.6:select_label=17,1007,1016 \
    -layout 1 -viewport sagittal -zoom 2 -viewsize 400 400 \
    -ras $(get_com.py --roi_niigz slicerois.nii.gz --imgval 17) \
    -ss lh_qc.png

freeview \
    -nocursor \
    -v rrnu.nii.gz \
    -v C2slice_mask.nii.gz:colormap=binary:binary_color=red \
    -v rraparc+aseg.nii.gz:colormap=lut:opacity=0.6:select_label=53,2007,2016 \
    -layout 1 -viewport sagittal -zoom 2 -viewsize 400 400 \
    -ras $(get_com.py --roi_niigz slicerois.nii.gz --imgval 53) \
    -ss rh_qc.png

thedate=$(date)

magick \( rh_qc.png lh_qc.png -bordercolor white -border 5 +append \) \
    \( qcslice.png -bordercolor white -border 5 \) \
    -gravity center -append page.png

convert \
    -size 1224x1584 xc:white \
    -gravity center \( page.png -resize 1194x1454 \) -geometry +0+0 -composite \
    -gravity NorthEast -pointsize 24 -annotate +20+50 "IHI C2 (radiol view)" \
    -gravity SouthEast -pointsize 24 -annotate +20+20 "${thedate}" \
    -gravity NorthWest -pointsize 24 -annotate +20+50 "${label_info}" \
    ihi-C2.pdf

