import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import gempy as gp
import gempy_viewer as gpv
import matplotlib.pyplot as plt
import pyvista as pv

from main import main
# from gempy_model.create_geomodel import create_geomodel
from topography import set_topography

def gempy_main():
    x_min, x_max, y_min, y_max, z_min, z_max = main()

    geo_model = gp.create_geomodel(
        project_name='OffsetModel',
        extent=[x_min, x_max, y_min, y_max, z_min, z_max],
        resolution=[8, 8, 8],
        importer_helper=gp.data.ImporterHelper(
        path_to_orientations='aineiston_kasittely/output_data/orientation_offset.csv',
        path_to_surface_points='aineiston_kasittely/output_data/offset_data.csv'
    )

    )
    hex_colormap = {
        'Sa': '#92d2fe',
        'Mr': '#daad30',
        'Hk': '#f0ea52',
        'Ka': '#ffff00',
        'Si': '#ff00ff',
        'Sr': '#71db71',
        'Srmr': '#daad30',
        'basement': '#b3b3b3'
    }

    for elem in geo_model.structural_frame.structural_elements:
        if elem.name in hex_colormap:
            elem.color = hex_colormap[elem.name]
            
    gp.set_section_grid(
        grid=geo_model.grid,
        section_dict={
            'section1': ([x_min, y_min], [x_max, y_max], [1, 50])
        }
    )

    set_topography(geo_model, x_min, x_max, y_min, y_max, z_min)

    gp.map_stack_to_surfaces(
        gempy_model=geo_model,
        mapping_object={
            "Strat_Series": ('Sa', 'Mr', 'Ka')
        }
    )

    geo_model.grid
    print("GeoModel Grid:")
    for g_type in geo_model.grid.GridTypes:
        try:
            grid_active = getattr(geo_model.grid, f"{g_type.name.lower()}_grid_active")
            grid_points = len(getattr(geo_model.grid, f"{g_type.name.lower()}_grid").values)
            print(f"{g_type.name} (active: {grid_active}): {grid_points} points")
        except AttributeError:
            print(f"{g_type.name} grid does not have an active attribute")

    geo_model.structural_frame

    geo_model.structural_frame.structural_elements

    gpv.plot_2d(geo_model, ve=1, show_topography=True, show_lith=True)
    # gpv.plot_2d(geo_model, ve=1, direction='x')
    # gpv.plot_3d(geo_model, show_surfaces=True, show_lith=False, image=False, ve=1)
    # gpv.plot_3d(geo_model, show_surfaces=True, show_lith=True, image=False, ve=1)
    # gpv.plot_3d(geo_model, show_lith=True, show_data=True, show_boundaries=True)

    pv.global_theme.allow_empty_mesh = True
    gp.compute_model(geo_model)
    gpv.plot_3d(geo_model, ve=1, show_topography=True, show_lith=True)


    plt.show()

if __name__ == "__main__":
    gempy_main()