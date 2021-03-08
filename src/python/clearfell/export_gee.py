import ee

ee.Initialize()


def export_s1_gee(date_from, date_to, coords, out_file_name, out_crs="EPSG:27700"):
    """
    Exports Sentinel1 temporal composite image to Google Drive

    Parameters:
        date_from (date): Start date of image composite (yyyy-MM-dd format)
        date_to (date): End date of image composite (yyyy-MM-dd format)
        coords (list): List of coords for export extent in xmin,ymin,xmax,ymax order in decimal degrees
        out_file_name (string): Name of geotiff exported into Google Drive
        out_crs (string): EPSG coordinate reference number for exported image

    Returns:
        None image exported to drive
    """
    extent = ee.Algorithms.GeometryConstructors.BBox(*coords)
    s1c = (
        ee.ImageCollection("COPERNICUS/S1_GRD")
        .filterBounds(extent)
        .filterDate(date_from, date_to)
        .filter(ee.Filter.eq("transmitterReceiverPolarisation", ["VV", "VH"]))
    )
    imgasc = (
        s1c.filter(ee.Filter.eq("orbitProperties_pass", "ASCENDING"))
        .median()
        .select(["VV", "VH"], ["VVasc", "VHasc"])
    )
    imgdesc = (
        s1c.filter(ee.Filter.eq("orbitProperties_pass", "DESCENDING"))
        .median()
        .select(["VV", "VH"], ["VVdesc", "VHdesc"])
    )
    imgasc = imgasc.addBands(
        imgasc.select("VVasc").subtract(imgasc.select("VHasc")).rename("Ratioasc")
    )
    imgdesc = imgdesc.addBands(
        imgdesc.select("VVdesc").subtract(imgdesc.select("VHdesc")).rename("Ratiodesc")
    )
    img = imgasc.addBands(imgdesc)
    img = img.select(
        ["VVdesc", "VHdesc", "Ratiodesc", "VVasc", "VHasc", "Ratioasc"]
    ).toFloat()

    task = ee.batch.Export.image.toDrive(
        image=img,
        folder="colab_data",
        description=out_file_name,
        region=extent,
        scale=10,
        crs=out_crs,
        maxPixels=10000000000,
    )
    task.start()
    print(f"exported {out_file_name} to gdrive")


if __name__ == "__main__":
    export_s1_gee(
        "2019-07-01", "2019-07-31", [-5.5059, 57.9483, -3.0066, 58.6612], "s1_july_2019"
    )
