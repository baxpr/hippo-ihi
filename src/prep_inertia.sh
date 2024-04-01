#!/usr/bin/env


for hemi in lh rh; do

    # Threshold to hippocampus only
    mri_binarize \
        --i "${subj_dir}"/mri/${hemi}.hippoAmygLabels.mgz \
        --min 1 --max 1000 \
        --o ${hemi}.hippomask.nii.gz

    # Resample to lower res nu grid
    mri_vol2vol \
        --mov ${hemi}.hippomask.nii.gz \
        --targ "${subj_dir}"/mri/nu.mgz \
        --regheader \
        --o ${hemi}.hippomask.nii.gz

done

# Combine hemispheres
mri_concat \
    --i lh.hippomask.nii.gz rh.hippomask.nii.gz \
    --o hippomasks.nii.gz \
    --sum

