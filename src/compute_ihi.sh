#!/usr/bin/env bash
#
# subj_dir
# out_dir
# slice_min_delta
# slice_max_delta
# hatag

# Filename tag of hipp segmentation
export hatag=hippoAmygLabels-T1.v21

# Work in output directory
cd "${out_dir}"

# Convert nu, hippocampal segs to nifti for nibabel
mri_convert \
    "${subj_dir}"/mri/nu.mgz \
    nu.nii.gz

for hemi in lh rh; do
    mri_convert \
        "${subj_dir}"/mri/${hemi}.${hatag}.mgz \
        ${hemi}.${hatag}.nii.gz
done

# Rotate to align principal axes of hippocampus with image axes
inertia_rotate.py --img_dir "${out_dir}" --hatag "${hatag}"

# Compute IHI metrics
for hemi in lh rh; do
    compute_ihi.py \
        --hemi ${hemi} \
        --seg_niigz r${hemi}.${hatag}.nii.gz \
        --out_dir "${out_dir}"
done

# Make QC PDF
make_pdf.sh
