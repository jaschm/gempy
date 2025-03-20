import rasterio
import gempy as gp  # Import the gp module

def set_topography(geo_model, x_min, x_max, y_min, y_max, z_min):
    with rasterio.open('aineiston_kasittely/input_data/dtm_8.3.2025_2.tif') as dataset:
        band1 = dataset.read(1)
        nodata = dataset.nodata  # Define the nodata variable
        band1[band1 == nodata] = z_min  # Replace nodata values with z_min

        with rasterio.open(
            'aineiston_kasittely/input_data/L3324D_2_no_nodata.tif',
            'w',
            driver='GTiff',
            height=band1.shape[0],
            width=band1.shape[1],
            count=1,
            dtype=band1.dtype,
            crs=dataset.crs,
            transform=dataset.transform,
        ) as dst:
            dst.write(band1, 1)

    print(f"Setting topography with crop_to_extent: [{x_min}, {x_max}, {y_min}, {y_max}]")
    gp.set_topography_from_file(
        grid=geo_model.grid,
        filepath='aineiston_kasittely/input_data/L3324D_2_no_nodata.tif',
        crop_to_extent=[x_min, x_max, y_min, y_max]
    )
