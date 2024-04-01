#!/usr/bin/env bash
#
# subj_dir
# out_dir

# Work in output directory
cd "${out_dir}"

# Convert hippocampal segs to nifti for nibabel
for hemi in lh rh; do
    mri_convert \
        "${subj_dir}"/mri/${hemi}.hippoAmygLabels.mgz \
        ${hemi}.hippoAmygLabels.nii.gz
done

# Rotate to align principal axes of hippocampus with image axes
inertia.py --img_dir "${out_dir}"

# Compute IHI metrics
for hemi in lh rh; do
    compute_ihi.py \
        --seg_niigz r${hemi}.hippoAmygLabels.nii.gz \
        --out_dir "${out_dir}" \
        > r${hemi}.hippoAmygLabels-info.txt
done
