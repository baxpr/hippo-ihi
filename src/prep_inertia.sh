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

    # Resample to same grid. This is needed to combine lh/rh,
    # plus we will want them in register with some version of
    # nu image for viewing
    mri_vol2vol \
        --mov ${hemi}.hippomask.nii.gz \
        --targ "${subj_dir}"/mri/nu.mgz \
        --regheader \
        --nearest \
        --o ${hemi}.hippomask.nii.gz

    # Convert full seg to nifti
    mri_convert \
        "${subj_dir}"/mri/${hemi}.hippoAmygLabels.mgz \
        ${hemi}.hippoAmygLabels.nii.gz
    
done


# Combine hemispheres
mri_concat \
    --i lh.hippomask.nii.gz rh.hippomask.nii.gz \
    --o hippomasks.nii.gz \
    --sum


## So far, all images are aligned in fsleyes and freeview and
# show "Orientation : LIA" by mri_info but with differing FOV,
# voxel size, and vox2ras transforms.


# Test a 90 degree rotation without resampling. Doesn't work -
# I bet the rotation is happening around different centers based
# on FOVs - corner or center voxel. Orientation after rotation 
# looks the same, but position is different.
mri_vol2vol \
    --mov lh.hippomask.nii.gz \
    --targ lh.hippomask.nii.gz \
    --regheader \
    --rot 90 0 0 \
    --no-resample \
    --o rlh.hippomask.nii.gz

mri_vol2vol \
    --mov lh.hippoAmygLabels.nii.gz \
    --targ lh.hippoAmygLabels.nii.gz \
    --regheader \
    --rot 90 0 0 \
    --no-resample \
    --o rlh.hippoAmygLabels.nii.gz



# Get mask into RAS (not actually needed - same result without)
#mri_convert \
#    --out_orientation RAS \
#    hippomasks.nii.gz \
#    hippomasks.nii.gz

# Estimate and apply rotations
rots=$(inertia.py --mask_niigz hippomasks.nii.gz)
mri_vol2vol \
    --mov hippomasks.nii.gz \
    --targ hippomasks.nii.gz \
    --regheader \
    --rot $rots \
    --no-resample \
    --o rhippomasks.nii.gz

mri_vol2vol \
    --mov rhippomasks.nii.gz \
    --targ hippomasks.nii.gz \
    --regheader \
    --rot 0 90 0 \
    --nearest \
    --o rhippomasks.nii.gz


# Apply to hi res segs. Can't apply rots directly
# because accuracy is dependent on FOV
mri_vol2vol \
    --mov lh.hippoAmygLabels.nii.gz \
    --targ lh.hippoAmygLabels.nii.gz \
    --regheader \
    --rot $rots \
    --no-resample \
    --o rot-lh.hippoAmygLabels.nii.gz

mri_vol2vol \
    --mov rot-lh.hippoAmygLabels.nii.gz \
    --targ rot-lh.hippoAmygLabels.nii.gz \
    --regheader \
    --rot 0 90 0 \
    --no-resample \
    --o rot-lh.hippoAmygLabels.nii.gz
