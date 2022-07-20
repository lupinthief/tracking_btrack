# Development around the btrack package for the iceberg tracking use case

https://github.com/quantumjot/BayesianTracker

Based heavily on documentation and examples from btrack and assumes
btrack v>0.5.0 installed from branch 'visual-features' using Python 3.7

Icebergs_to_btrack provides some housekeeping to get example dataset into expected format

icebergs_to_btrack_subsets uses pre-cropped images to avoid needing fiona and rasterio which have dependency conflicts with btrack and napari in python 3.8+ which is required for the latest version of btrack in the visual features branch. 

Additional dependencies to btrack requirements:
fiona
rasterio
DP_Utils
