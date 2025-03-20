import gempy as gp

def create_geomodel(project_name, extent, resolution, path_to_orientations, path_to_surface_points):
    geo_model = gp.create_geomodel(
        project_name=project_name,
        extent=extent,
        resolution=resolution,
        importer_helper=gp.data.ImporterHelper(
            path_to_orientations=path_to_orientations,
            path_to_surface_points=path_to_surface_points
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

    return geo_model
