#!/usr/bin/env bash

# Defaults
expirt subj_dir=/INPUTS/SUBJECT/SUBJECT
export out_dir=/OUTPUTS
export hatag=hippoAmygLabels-T1.v21
export slice_min_delta=2
export slice_max_delta=6

while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in      
        --subj_dir)          export subj_dir="$2";          shift; shift ;;
        --out_dir)           export out_dir="$2";           shift; shift ;;
        --hatag)             export hatag="$2";             shift; shift ;;
        --slice_min_delta)   export slice_min_delta="$2";   shift; shift ;;
        --slice_max_delta)   export slice_max_delta="$2";   shift; shift ;;
        *) echo "Input ${1} not recognized"; shift ;;
    esac
done

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
        --slice_min_delta ${slice_min_delta} \
        --slice_max_delta ${slice_max_delta} \
        --out_dir "${out_dir}"
done

# Make QC PDF
make_pdf.sh
