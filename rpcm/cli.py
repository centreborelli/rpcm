import argparse
import numpy as np

import rpcm


def main():
    """
    Command line interface for rpcm.
    """
    parser = argparse.ArgumentParser(description=('RPC model toolkit'))
    subparsers = parser.add_subparsers(dest='cmd', help='projection, localization or crop',
                                       metavar='{projection, localization, crop}')
    subparsers.required = True

    # parser for the "projection" command
    parser_proj = subparsers.add_parser('projection',
                                        help='conversion of geographic to image'
                                             ' coordinates')
    parser_proj.add_argument('--img', required=True,
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
    parser_loc.add_argument('--img', required=True,
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
    parser_crop.add_argument('--img', required=True,
                             help=('path to a GeoTIFF image file with RPC metadata'))
    parser_crop.add_argument('--lon', type=float, required=True,
                             help=('longitude of the crop center'))
    parser_crop.add_argument('--lat', type=float, required=True,
                             help=('latitude of the crop center'))
    parser_crop.add_argument('-z', type=float,
                             help=('altitude of the crop center'))
    parser_crop.add_argument('-w', type=int, required=True,
                             help=('crop width (pixels)'))
    parser_crop.add_argument('-l', type=int, required=True,
                             help=('crop height (pixels)'))
    parser_crop.add_argument('-o', required=True,
                             help=('path to the output cropped tif image'))

    args = parser.parse_args()

    if args.cmd == 'projection':
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
            rpcm.localization(args.img, args.x, args.y, args.z
                              crop_path=args.crop, verbose=True)

    elif args.cmd == 'crop':
        rpcm.crop(args.o, args.img, args.lon, args.lat, args.z, args.w, args.l)


if __name__ == '__main__':
    main()
