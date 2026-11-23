# Freesurfer-derived measurement of incomplete hippocampal inversion

Following the general framework for manual scoring described in

Cury C, Toro R, Cohen F, Fischer C, Mhaya A, Samper-González J, Hasboun D, Mangin JF, Banaschewski T, Bokde AL, Bromberg U, Buechel C, Cattrell A, Conrod P, Flor H, Gallinat J, Garavan H, Gowland P, Heinz A, Ittermann B, Lemaitre H, Martinot JL, Nees F, Paillère Martinot ML, Orfanos DP, Paus T, Poustka L, Smolka MN, Walter H, Whelan R, Frouin V, Schumann G, Glaunès JA, Colliot O; IMAGEN Consortium. Incomplete Hippocampal Inversion: A Comprehensive MRI Study of Over 2000 Subjects. Front Neuroanat. 2015 Dec 22;9:160. doi: 10.3389/fnana.2015.00160. PMID: 26733822; PMCID: PMC4686650.

https://pmc.ncbi.nlm.nih.gov/articles/PMC4686650/


## Criterion 3 using high-resolution subfield segmentation of hippocampus

These are the `hires_C3` scripts. The entrypoint is `compute_ihi_hires_C3.sh`.

1. Rotate to align principal axes of hippocampus with image axes

1. Identify a coronal slice 2-6 mm behind the posterior edge of hippocampal head

1. Identify most medial and lateral voxels of subicular complex

1. Identify most medial and lateral voxels of dentate gyrus

1. Final IHI metric will be subiculum width minus dentate width in the selected slice
