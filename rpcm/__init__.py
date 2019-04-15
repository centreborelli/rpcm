import warnings
import numpy as np
import rasterio
import srtm4

from rpcm import rpc_model


warnings.filterwarnings("ignore",
                        category=rasterio.errors.NotGeoreferencedWarning)


def rpc_from_geotiff(geotiff_path):
    """
    Read the RPC coefficients from a GeoTIFF file and return a rpc_model object.

    Args:
        geotiff_path (str): path or url to a GeoTIFF file

    Returns:
        instance of the rpc_model.RPCModel class
    """
    with rasterio.open(geotiff_path, 'r') as src:
        rpc_dict = src.tags(ns='RPC')
    return rpc_model.RPCModel(rpc_dict)


def image_footprint(image, z=0):
    """
    Compute the longitude, latitude footprint of an image using its RPC model.

    Args:
        image (str): path or url to a GeoTIFF file
        z (float): altitude (in meters above the WGS84 ellipsoid) used to
            convert the image corners pixel coordinates into longitude, latitude

    Returns:
        geojson.Polygon object containing the image footprint polygon
    """
    rpc = rpc_from_geotiff(image)
    with rasterio.open(image, 'r') as src:
        h, w = src.shape
    coords = []
    for x, y, z in zip([0, w, w, 0], [0, 0, h, h], [z, z, z, z]):
        lon, lat = rpc.localization(x, y, z)
        coords.append([lon, lat])
    return geojson.Polygon([coords])  # TODO replace this by  a single call to rpc.localization with a list


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

    if crop_path:
        #TODO
        pass

    if svg_path:
        #TODO
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
    if crop_path:
        #TODO
        pass

    rpc = rpc_from_geotiff(img_path)
    lon, lat = rpc.localization(x, y, z)

    if verbose:
        for p in zip(np.atleast_1d(lon), np.atleast_1d(lat)):
            print('{:.8f} {:.8f}'.format(*p))

    return lon, lat


def crop(output_crop_path, input_img_path, lon, lat, z=None):
    """
    Crop a polygon defined with geographic coordinates.

    Args:
        output_crop_path (str): path to the output crop file
        input_img_path (str): path or url to a GeoTIFF image with RPC metadata
        lon (float): longitude of the crop center
        lat (float): latitude of the crop center
        z (float): altitude of the crop center
    """
    rpc = rpc_from_geotiff(input_img_path)

    if z is None:
        z = srtm4.srtm4(lon, lat)

    x, y = rpc.projection(lon, lat, z)

    #TODO make the crop
