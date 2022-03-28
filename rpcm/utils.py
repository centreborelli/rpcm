import os
import warnings

import numpy as np
import rasterio

from rpcm import rpc_model


warnings.filterwarnings("ignore",
                        category=rasterio.errors.NotGeoreferencedWarning)


def viewing_direction(zenith, azimut):
    """
    Compute the unit 3D vector defined by zenith and azimut angles.

    Args:
        zenith (float): angle wrt the vertical direction, in degrees
        azimut (float): angle wrt the north direction, in degrees

    Return:
        3-tuple: 3D unit vector giving the corresponding direction
    """
    z = np.radians(zenith)
    a = np.radians(azimut)
    return np.sin(a)*np.sin(z), np.cos(a)*np.sin(z), np.cos(z)


def bounding_box2D(pts):
    """
    Rectangular bounding box for a list of 2D points.

    Args:
        pts (list): list of 2D points represented as 2-tuples or lists of length 2

    Returns:
        x, y, w, h (floats): coordinates of the top-left corner, width and
            height of the bounding box
    """
    dim = len(pts[0])  # should be 2
    bb_min = [min([t[i] for t in pts]) for i in range(dim)]
    bb_max = [max([t[i] for t in pts]) for i in range(dim)]
    return bb_min[0], bb_min[1], bb_max[0] - bb_min[0], bb_max[1] - bb_min[1]


def points_apply_homography(H, pts):
    """
    Applies an homography to a list of 2D points.

    Args:
        H (np.array): 3x3 homography matrix
        pts (list): list of 2D points, each point being a 2-tuple or a list
            with its x, y coordinates

    Returns:
        numpy array: list of transformed points, one per line
    """
    pts = np.asarray(pts)

    # convert the input points to homogeneous coordinates
    if len(pts[0]) < 2:
        print("""points_apply_homography: ERROR the input must be a numpy array
          of 2D points, one point per line""")
        return
    pts = np.hstack((pts[:, :2], np.ones(len(pts))))

    # apply the transformation
    Hpts = (np.dot(H, pts.T)).T

    # normalize the homogeneous result and trim the extra dimension
    Hpts = Hpts * (1.0 / np.tile( Hpts[:, 2], (3, 1)) ).T
    return Hpts[:, :2]


def bounding_box_of_projected_aoi(rpc, aoi, z=0, homography=None):
    """
    Return the x, y, w, h pixel bounding box of a projected AOI.

    Args:
        rpc (rpc_model.RPCModel): RPC camera model
        aoi (geojson.Polygon): GeoJSON polygon representing the AOI
        z (float): altitude of the AOI with respect to the WGS84 ellipsoid
        homography (2D array, optional): matrix of shape (3, 3) representing an
            homography to be applied to the projected points before computing
            their bounding box.

    Return:
        x, y (ints): pixel coordinates of the top-left corner of the bounding box
        w, h (ints): pixel dimensions of the bounding box
    """
    lons, lats = np.asarray(aoi['coordinates']).squeeze().T
    x, y = rpc.projection(lons, lats, z)
    pts = list(zip(x, y))
    if homography is not None:
        pts = points_apply_homography(homography, pts)
    return np.round(bounding_box2D(pts)).astype(int)


def crop_aoi(geotiff, aoi, z=0):
    """
    Crop a geographic AOI in a georeferenced image using its RPC functions.

    Args:
        geotiff (string): path or url to the input GeoTIFF image file
        aoi (geojson.Polygon): GeoJSON polygon representing the AOI
        z (float, optional): base altitude with respect to WGS84 ellipsoid (0
            by default)

    Return:
        crop (array): numpy array containing the cropped image
        x, y (ints): pixel coordinates of the top-left corner of the crop
    """
    x, y, w, h = bounding_box_of_projected_aoi(rpc_model.rpc_from_geotiff(geotiff),
                                               aoi, z)
    with rasterio.open(geotiff, 'r') as src:
        crop = src.read(window=((y, y + h), (x, x + w)), boundless=True).squeeze()
    return crop, x, y


def rasterio_write(path, array, profile={}, tags={}):
    """
    Write a numpy array in a tiff or png file with rasterio.

    Args:
        path (str): path to the output tiff/png file
        array (numpy array): 2D or 3D array containing the image to write
        profile (dict): rasterio profile (ie dictionary of metadata)
        tags (dict): dictionary with additional geotiff tags
    """
    # read image size and number of bands
    try:
        nbands, height, width = array.shape
    except ValueError:  # not enough values to unpack (expected 3, got 2)
        nbands = 1
        height, width = array.shape
        array = np.asarray([array])

    # define image metadata dict
    profile.update(driver=rasterio.driver_from_extension(path),
                   count=nbands,
                   width=width,
                   height=height,
                   dtype=array.dtype)

    # write to file
    with rasterio.open(path, 'w', **profile) as dst:
        dst.write(array)
        dst.update_tags(**tags)
