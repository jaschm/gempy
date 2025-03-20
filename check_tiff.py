import rasterio

# Path to the TIFF file
tif_path = 'aineiston_kasittely/input_data/dtm_pieni.tif'

# Open the TIFF file and print its metadata
with rasterio.open(tif_path) as dataset:
    print("TIFF file metadata:")
    print(dataset.meta)
    
    # Get the bounds of the TIFF file
    bounds = dataset.bounds
    print(f"Bounds: {bounds}")

    # Get the min and max Z values
    band1 = dataset.read(1)
    z_min = band1.min()
    z_max = band1.max()
    print(f"Z range: {z_min} to {z_max}")