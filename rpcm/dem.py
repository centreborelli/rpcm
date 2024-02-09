import rasterio as rio

GCS_COPERNICUS_DEM_VRT = "gs://overstory-dtms/CopernicusDem30m/copernicus_dem/dem.vrt"

def get_copernicus_elevation(lon: float, lat: float):
    with rio.open(GCS_COPERNICUS_DEM_VRT) as src:
        assert src.crs == "EPSG:4326"
        elevation = list(src.sample([(lon, lat)]))[0]
    return elevation