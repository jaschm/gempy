import check_tiff
import numpy as np
import csv
from rasterio.windows import from_bounds

# Load the DTM file and clip to the specified extent
dtm_file = "aineiston_kasittely\\input_data\\L3324D.tif"
output_clipped_dtm_file = "aineiston_kasittely\\output_data\\clipped_dtm.tif"

# Define the extent (in the coordinate system of the DTM)
x_min, x_max = 245669.143, 248835.393
y_min, y_max = 6708793.141, 6709714.023

with check_tiff.open(dtm_file) as src:
    # Create a window for the specified bounds
    window = from_bounds(x_min, y_min, x_max, y_max, src.transform)

    # Read the data within the window
    clipped_data = src.read(window=window)

    # Update transform for the clipped area
    transform = src.window_transform(window)

    # Profile for the new raster
    profile = src.profile
    profile.update({
        'height': clipped_data.shape[1],
        'width': clipped_data.shape[2],
        'transform': transform,
    })

    # Save the clipped DTM
    with check_tiff.open(output_clipped_dtm_file, 'w', **profile) as dst:
        dst.write(clipped_data)

print(f"Clipped DTM saved to {output_clipped_dtm_file}")

# Load the clipped DTM file and extract coordinates
with check_tiff.open(output_clipped_dtm_file) as src:
    dtm_data = src.read(1)  # Read the first band (elevation data)
    dtm_transform = src.transform  # Get geotransform info
    dtm_crs = src.crs  # Coordinate Reference System (CRS)
    nodata_value = src.nodata

print(f"DTM Shape: {dtm_data.shape}")

# Generate X, Y coordinates from raster indices
rows, cols = np.meshgrid(
    np.arange(dtm_data.shape[0]),
    np.arange(dtm_data.shape[1]),
    indexing="ij"
)

# Transform raster indices to coordinates
xs, ys = check_tiff.transform.xy(dtm_transform, rows, cols)
xs, ys = np.array(xs).flatten(), np.array(ys).flatten()
zs = dtm_data.flatten()

# Remove nodata values (e.g., -9999 or any other invalid value)
valid_mask = zs != nodata_value
xs, ys, zs = xs[valid_mask], ys[valid_mask], zs[valid_mask]

# Further filter points to only include those within the clipping bounds
bounds_mask = (xs >= x_min) & (xs <= x_max) & (ys >= y_min) & (ys <= y_max)
xs, ys, zs = xs[bounds_mask], ys[bounds_mask], zs[bounds_mask]

print(f"Number of valid points within bounds: {len(xs)}")

# Write filtered points to CSV
output_file = "aineiston_kasittely\\output_data\\extracted_dtm_coordinates.csv"

with open(output_file, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["X", "Y", "Z"])  # Header row
    writer.writerows(zip(xs, ys, zs))

print(f"Extracted coordinates saved to {output_file}")
