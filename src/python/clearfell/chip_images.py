import gdal, os
import geopandas as gpd
import rasterio as rio
from shapely.geometry import Polygon
import numpy as np


def chip_image(input_file_path, output_path, pixel_dimensions=128, offset=64):
    print(f"chipping {input_file_path} to /{output_path}...")
    with rio.open(input_file_path) as f:
        img_x, img_y = f.width, f.height
    for i in range(0, img_x, offset):
        for v in range(img_y - pixel_dimensions, 0, -offset):
            gdal.Translate(
                destName=f"{output_path}/{input_file_path.split('/')[-1][:-4]}_{i}_{v}.tif",
                srcDS=input_file_path,
                srcWin=[i, v, pixel_dimensions, pixel_dimensions],
                format="GTiff",
            )
            # gdal_command = f"gdal_translate -of GTIFF -srcwin {i} {v} {pixel_dimensions} {pixel_dimensions} {input_file_path} {output_path}/{input_file_path.split('/')[-1][:-4]}_{i}_{v}.tif"
            # os.system(gdal_command)


def chip_extent_shp(input_path, output_path, output_file="chip_extents.shp"):
    file_list = [
        f"{input_path}/{x}" for x in os.listdir(input_path) if x.endswith(".tif")
    ]
    with open(f"{output_path}/list_chips.txt", "w") as f:
        for i in file_list:
            f.write(f"{i}\n")
    gdal_command = f"gdaltindex {output_path}/chip_extents.shp --optfile {output_path}/list_chips.txt"
    os.system(gdal_command)


def generate_grid_rasterfile(
    raster_file, dimensions_metres, interval_metres, output_path, output_file
):
    with rio.open(raster_file) as r:
        xmin, ymin, xmax, ymax = r.bounds
        crs = r.crs.to_string()
    xgrids = list(range(int(np.floor(xmin)), int(np.ceil(xmax)), interval_metres))
    ygrids = list(range(int(np.floor(ymin)), int(np.ceil(ymax)), interval_metres))
    xgrids = [x for x in xgrids if x + dimensions_metres < xmax]
    ygrids = [y for y in ygrids if y + dimensions_metres < ymax]
    grids = []
    ids = []
    for x in xgrids:
        for y in ygrids:
            grids.append(
                Polygon(
                    [
                        (x, y),
                        (x + dimensions_metres, y),
                        (x + dimensions_metres, y + dimensions_metres),
                        (x, y + dimensions_metres),
                    ]
                )
            )
            ids.append(
                f"{xgrids.index(x)*dimensions_metres}_{ygrids.index(y)*dimensions_metres}"
            )
    gdf = gpd.GeoDataFrame({"location": ids, "geometry": grids}, crs=crs)
    gdf["area"] = gdf["geometry"].area
    gdf.to_file(f"{output_path}/{output_file}")
    print(f"exported grids shp to {output_path}/{output_file}")
