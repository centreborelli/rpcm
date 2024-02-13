import os

import pyproj
import rasterio as rio

pyproj.network.set_network_enabled(active=True)
os.environ["PROJ_UNSAFE_SSL"] = "TRUE"  # Required by pyproj to download external datum information

SRTM_VRT = "gs://overstory-dtms/srtm_v41_90m/index.vrt"


def get_srtm_elevations(lons: list[float], lats: list[float], convert_ellipsoidal: bool) -> list[float]:
    with rio.open(SRTM_VRT) as src:
        assert src.crs == "EPSG:4326"
        elevations = [float(e[0]) for e in src.sample([(lon, lat) for lon, lat in zip(lons, lats)])]
        # Convert nodata
        elevations = [e if e != src.nodata else float("nan") for e in elevations]
    # Convert to ellipsoidal heights
    if convert_ellipsoidal:
        return to_ellipsoid(lons, lats, elevations)
    return elevations


def to_ellipsoid(lons: list[float], lats: list[float], elevations: list[float]) -> list[float]:
    """
    Convert geoidal heights to ellipsoidal heights.
    """
    # WGS84 with ellipsoid height as vertical axis
    ellipsoid = pyproj.CRS.from_epsg(4979)
    # WGS84 with Gravity-related height (EGM96)
    geoid = pyproj.CRS("EPSG:4326+5773")

    trf = pyproj.Transformer.from_crs(geoid, ellipsoid)
    new_elevations = trf.transform(lats, lons, elevations, errcheck=True)[-1]

    return [round(new_alt, 2) for new_alt in new_elevations]
