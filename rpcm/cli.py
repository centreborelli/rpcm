import argparse
import numpy as np
import geojson

import rpcm


def valid_geojson(filepath):
    """
    Check if a file contains valid geojson.
    """
    with open(filepath, 'r') as f:
        geo = geojson.load(f)
    if type(geo) == geojson.geometry.Polygon:
        return geo
    if type(geo) == geojson.feature.FeatureCollection:
        p = geo['features'][0]['geometry']
        if type(p) == geojson.geometry.Polygon:
            return p
    raise argparse.ArgumentTypeError('Invalid geojson: only polygons are supported')


def main():
    """
    Command line interface for rpcm.
    """
    parser = argparse.ArgumentParser(description=('RPC model toolkit'))
    subparsers = parser.add_subparsers(dest='cmd', help='projection, localization, crop or footprint',
                                       metavar='{projection, localization, crop, footprint}')
    subparsers.required = True

    # parser for the "footprint" command
    parser_footprint = subparsers.add_parser('footprint',
                                        help='print the image footprint as a '
                                             '(lon, lat) polygon')
    parser_footprint.add_argument('img', help=('path or url to a GeoTIFF image '
                                               'file with RPC metadata'))
    parser_footprint.add_argument('-z', type=float, help=('altitude, in meters'))

    # parser for the "projection" command
    parser_proj = subparsers.add_parser('projection',
                                        help='conversion of geographic to image'
                                             ' coordinates')
    parser_proj.add_argument('img',
                             help=('path or url to a GeoTIFF image file with RPC metadata'))
    parser_proj.add_argument('--lon', type=float, help=('longitude'))
    parser_proj.add_argument('--lat', type=float, help=('latitude'))
    parser_proj.add_argument('-z', type=float, help=('altitude, in meters'))
    parser_proj.add_argument('--points',
                             help=('path to a 2/3 columns txt file: lon lat [z]'))
    parser_proj.add_argument('--crop', type=str,
                             help=('path to a tif crop previously produced by rpcm. '
                                   'Image coordinates are computed with respect '
                                   'to this crop.'))
    parser_proj.add_argument('--svg', type=str,
                             help=('path to an svg file where to plot '
                                   'projected points.'))

    # parser for the "localization" command
    parser_loc = subparsers.add_parser('localization',
                                        help='conversion of image to geographic'
                                             ' coordinates')
    parser_loc.add_argument('img',
                            help=('path or url to a GeoTIFF image file with RPC metadata'))
    parser_loc.add_argument('-x', type=float, help=('horizontal pixel coordinate (i.e. column index)'))
    parser_loc.add_argument('-y', type=float, help=('vertical pixel coordinate (i.e. row index)'))
    parser_loc.add_argument('-z', type=float, help=('altitude, in meters'))
    parser_loc.add_argument('--points',
                            help=('path to a 3 columns txt file: x y z'))
    parser_loc.add_argument('--crop', type=str,
                            help=('path to a tif crop previously produced by rpcm. '
                                  'Image coordinates are interpreted with respect '
                                  'to this crop.'))

    # parser for the "crop" command
    parser_crop = subparsers.add_parser('crop',
                                        help='crop a polygon defined with geographic coordinates')
    parser_crop.add_argument('img',
                             help=('path to a GeoTIFF image file with RPC metadata'))
    parser_crop.add_argument('aoi', type=valid_geojson,
                             help=('path to geojson file defining the area of interest (AOI)'))
    parser_crop.add_argument('-z', type=float,
                             help=('altitude of the crop center'))
    parser_crop.add_argument('crop',
                             help=('path to the output cropped tif image'))

    # parser for the "angle" command
    parser_angle = subparsers.add_parser('angle',
                                         help='compute the view angle difference between two (stereo) images')
    parser_angle.add_argument('img1',
                              help=('path to a GeoTIFF image file with RPC metadata'))
    parser_angle.add_argument('img2',
                              help=('path to a GeoTIFF image file with RPC metadata'))
    parser_angle.add_argument('--lon', type=float, help=('longitude'))
    parser_angle.add_argument('--lat', type=float, help=('latitude'))
    parser_angle.add_argument('-z', type=float, help=('altitude'))

    args = parser.parse_args()

    if args.cmd == 'footprint':
        rpcm.image_footprint(args.img, args.z, verbose=True)

    elif args.cmd == 'projection':
        if args.points and (args.lat or args.lon):
            parser.error('--points and {--lat, --lon} are mutually exclusive')
        if not args.points and not (args.lon and args.lat):
            parser.error('either --points or {--lat, --lon} must be defined')
        if args.points:
            rpcm.projection(args.img, *np.loadtxt(args.points).T,
                            crop_path=args.crop, svg_path=args.svg,
                            verbose=True)
        else:
            rpcm.projection(args.img, args.lon, args.lat, args.z,
                            crop_path=args.crop, svg_path=args.svg,
                            verbose=True)

    elif args.cmd == 'localization':
        if args.points and (args.x or args.y or args.z):
            parser.error('--points and {-x, -y, -z} are mutually exclusive')
        if not args.points and not (args.x and args.y and args.z):
            parser.error('either --points or {-x, -y, -z} must be defined')
        if args.points:
            rpcm.localization(args.img, *np.loadtxt(args.points).T,
                              crop_path=args.crop, verbose=True)
        else:
            rpcm.localization(args.img, args.x, args.y, args.z,
                              crop_path=args.crop, verbose=True)

    elif args.cmd == 'crop':
        rpcm.crop(args.crop, args.img, args.aoi, args.z)

    elif args.cmd == 'angle':
        rpcm.angle_between_views(args.img1, args.img2, args.lon, args.lat,
                                 args.z, verbose=True)


if __name__ == '__main__':
    main()
