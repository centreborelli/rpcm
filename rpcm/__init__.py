from __future__ import  print_function
import warnings

import geojson
import numpy as np
import rasterio
import srtm4

from rpcm import rpc_model
from rpcm import utils
from rpcm.rpc_model import RPCModel
from rpcm.rpc_model import rpc_from_geotiff
from rpcm.rpc_model import rpc_from_rpc_file
from rpcm.__about__ import __version__


warnings.filterwarnings("ignore",
                        category=rasterio.errors.NotGeoreferencedWarning)


def projection(img_path, lon, lat, z=None, crop_path=None, svg_path=None,
               verbose=False):
    """
    Conversion of geographic coordinates to image coordinates.

    Args:
        img_path (str): path or url to a GeoTIFF image with RPC metadata
        lon (float or list): longitude(s) of the input points
        lat (float or list): latitude(s) of the input points
        z (float or list): altitude(s) of the input points
        crop_path (str): path or url to an image crop produced by rpcm.
            Projected image coordinates are computed wrt this crop.
        svg_path (str): path to an svg file where to plot the projected image
            point(s)

    Returns:
        float or list: x pixel coordinate(s) of the projected point(s)
        float or list: y pixel coordinate(s) of the projected point(s)
    """
    rpc = rpc_from_geotiff(img_path)
    if z is None:
        z = srtm4.srtm4(lon, lat)

    x, y = rpc.projection(lon, lat, z)

    if crop_path:  # load and apply crop transformation matrix
        with rasterio.open(crop_path, 'r') as src:
            tags = src.tags()

        C = list(map(float, tags['CROP_TRANSFORM'].split()))
        C = np.array(C).reshape(3, 3)
        h = np.row_stack((x, y, x**0))  # homogeneous coordinates
        x, y = np.dot(C, h).squeeze()[:2]

    if svg_path:  #TODO
        pass

    if verbose:
        for p in zip(np.atleast_1d(x), np.atleast_1d(y)):
            print('{:.4f} {:.4f}'.format(*p))

    return x, y


def localization(img_path, x, y, z, crop_path=None, verbose=False):
    """
    Conversion of image coordinates to geographic coordinates.

    Args:
        img_path (str): path or url to a GeoTIFF image with RPC metadata
        x (float or list): x coordinate(s) of the input points
        y (float or list): y coordinate(s) of the input points
        z (float or list): altitude(s) of the input points
        crop_path (str): path or url to an image crop produced by rpcm.
            Input image coordinates are interpreted wrt this crop.

    Returns:
        float or list: longitude(s) of the localised point(s)
        float or list: latitude(s) of the localised point(s)
    """
    if crop_path:  # load and apply crop transformation matrix
        with rasterio.open(crop_path, 'r') as src:
            tags = src.tags()

        C = list(map(float, tags['CROP_TRANSFORM'].split()))
        C = np.array(C).reshape(3, 3)
        h = np.row_stack((x, y, x**0))  # homogeneous coordinates
        x, y = np.dot(np.linalg.inv(C), h).squeeze()[:2]

    rpc = rpc_from_geotiff(img_path)
    lon, lat = rpc.localization(x, y, z)

    if verbose:
        for p in zip(np.atleast_1d(lon), np.atleast_1d(lat)):
            print('{:.8f} {:.8f}'.format(*p))

    return lon, lat


def crop(output_crop_path, input_geotiff_path, aoi, z=None):
    """
    Crop an area of interest (AOI) defined with geographic coordinates.

    Args:
        output_crop_path (str): path to the output crop file
        input_img_path (str): path or url to a GeoTIFF image with RPC metadata
        aoi (geojson.Polygon): longitude, latitude vertices of the polygon
            defining the AOI.
        z (float): altitude of the AOI center with respect to the WGS84
            ellipsoid.
    """
    if z is None:  # read z from srtm
        lons, lats = np.asarray(aoi['coordinates']).squeeze().T
        z = srtm4.srtm4(np.mean(lons[:-1]), np.mean(lats[:-1]))

    # do the crop
    crop, x, y = utils.crop_aoi(input_geotiff_path, aoi, z)

    # crop transform to be stored in the tiff header
    T = np.eye(3)
    T[0, 2] = -x
    T[1, 2] = -y
    # TODO update the RPC coefficients to account for the crop

    # write file
    tags = {'CROP_TRANSFORM': ' '.join(str(t) for t in T.flatten()),
            'SOFTWARE': 'produced with rpcm {}'.format(__version__)}
    utils.rasterio_write(output_crop_path, crop, tags=tags)


def image_footprint(geotiff_path, z=None, verbose=False):
    """
    Compute the longitude, latitude footprint of an image using its RPC model.

    Args:
        geotiff_path (str): path or url to a GeoTIFF file
        z (float): altitude (in meters above the WGS84 ellipsoid) used to
            convert the image corners pixel coordinates into longitude, latitude

    Returns:
        geojson.Polygon object containing the image footprint polygon
    """
    with rasterio.open(geotiff_path, 'r') as src:
        rpc_dict = src.tags(ns='RPC')
        h, w = src.shape

    rpc = rpc_model.RPCModel(rpc_dict)
    if z is None:
        z = srtm4.srtm4(rpc.lon_offset, rpc.lat_offset)

    lons, lats = rpc.localization([0, 0, w, w, 0],
                                  [0, h, h, 0, 0],
                                  [z, z, z, z, z])
    footprint = geojson.Polygon([list(zip(lons,  lats))])

    if verbose:
        print(geojson.dumps(footprint))

    return footprint


def angle_between_views(geotiff_path_1, geotiff_path_2, lon=None, lat=None,
                        z=None, verbose=False):
    """
    Compute the view angle difference between two (stereo) images.

    Args:
        geotiff_path_1 (str): path or url to a GeoTIFF file
        geotiff_path_2 (str): path or url to a GeoTIFF file
        lon, lat, z (floats): longitude, latitude, altitude of the 3D point
            where to compute the angle

    Returns:
        float: angle between the views, in degrees
    """
    rpc1 = rpc_from_geotiff(geotiff_path_1)
    rpc2 = rpc_from_geotiff(geotiff_path_2)

    if lon is None:
        lon = rpc1.lon_offset
    if lat is None:
        lat = rpc1.lat_offset
    if z is None:
        z = srtm4.srtm4(lon, lat)

    a = utils.viewing_direction(*rpc1.incidence_angles(lon, lat, z))
    b = utils.viewing_direction(*rpc2.incidence_angles(lon, lat, z))
    angle = np.degrees(np.arccos(np.dot(a, b)))

    if verbose:
        print('{:.3f}'.format(angle))

    return angle
