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
        --nearest \
        --o ${hemi}.hippomask.nii.gz

done

# Combine hemispheres
mri_concat \
    --i lh.hippomask.nii.gz rh.hippomask.nii.gz \
    --o hippomasks.nii.gz \
    --sum

# Get into RAS
mri_convert \
    --out_orientation RAS \
    hippomasks.nii.gz \
    hippomasks.nii.gz


# Rotate

# Long axis ends on AP, RL/IS are swapped. Note
# that mri_vol2vol rotates on voxel axes, not mm.
# Total rotations are
#   - Output of inertia.py applied in freesurfer order (??)
#   - Additional 90 in Y to get on different axes
# Lot of confusion here about axes - xyz mm for inertia computations, ijk for FS rotations
#rots=$(inertia.py --mask_niigz hippomasks.nii.gz)
#rots="-92 -70 91"


# Now data in file is stored RAS (LR/PA/IS). After rots,
# Principle axis 1 LR (x/i) ends up on y/j
# Principle axis 2 PA (y/j) ends up on x/i
# Principle axis 3 IS (z/k) ends up on z/k


rots="-92 -70 91"
rots="92 70 -91"
mri_vol2vol \
    --mov hippomasks.nii.gz \
    --targ hippomasks.nii.gz \
    --regheader \
    --rot $rots \
    --nearest \
    --o rot-test.nii.gz





rots="-92 0 0"
mri_vol2vol \
    --mov rot-test.nii.gz \
    --targ hippomasks.nii.gz \
    --regheader \
    --rot 0 90 0 \
    --nearest \
    --o rot-test2.nii.gz
