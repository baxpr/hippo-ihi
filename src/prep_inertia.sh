#!/usr/bin/env bash
#
# Rotate principal inertial axes of bilateral hippocampus ROI
# to align with XYZ axes in image mm space.
#
# Working, but FIXME how to apply to the actual segmentations?

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
        --nearest \
        --o ${hemi}.hippomask.nii.gz

done

# Combine hemispheres
mri_concat \
    --i lh.hippomask.nii.gz rh.hippomask.nii.gz \
    --o hippomasks.nii.gz \
    --sum

# Get mask into RAS
mri_convert \
    --out_orientation RAS \
    hippomasks.nii.gz \
    hippomasks.nii.gz

# Estimate and apply rotations
rots=$(inertia.py --mask_niigz hippomasks.nii.gz)
mri_vol2vol \
    --mov hippomasks.nii.gz \
    --targ hippomasks.nii.gz \
    --regheader \
    --rot $rots \
    --nearest \
    --o rhippomasks.nii.gz

mri_vol2vol \
    --mov rhippomasks.nii.gz \
    --targ hippomasks.nii.gz \
    --regheader \
    --rot 0 90 0 \
    --nearest \
    --o rhippomasks.nii.gz
