# RPCM - Rational Polynomial Camera Model

Python implementation of the Rational Polynomial Camera (RPC) model for optical satellite images.

[Carlo de Franchis](mailto:carlo.de-franchis@ens-paris-saclay.fr), Gabriele Facciolo, Enric Meinhardt-Llopis
(Centre Borelli, ENS Paris-Saclay, Université Paris-Saclay) 2013-21

`rpcm` is a Python library and command line tool for geolocating satellite images
with RPCs. Its main source code repository is https://github.com/centreborelli/rpcm.


# Installation

To install `rpcm` from PyPI:

    pip install rpcm

Alternatively, to install `rpcm` from sources:

    git clone https://github.com/centreborelli/rpcm.git
    cd rpcm
    pip install -e .


# Usage

`rpcm` is a Python library that can be imported into other applications. A
Jupyter notebook tutorial covering the main features of the library is included (TODO).

`rpcm` also comes with a Command Line Interface (CLI). The `rpcm` CLI has an
extensive help that can be printed with the `-h` and `--help` switches.

    $ rpcm -h
    usage: rpcm [-h] {projection, localization, crop, footprint, angle} ...

Some CLI usage examples can be found in `tests/tests.sh`.

There are several subcommands, `projection`, `localization`, `crop`,
`footprint`, `angle`, each of which has its own help.


## Projection

    $ rpcm projection -h
    usage: rpcm projection [-h] [--lon LON] [--lat LAT] [-z Z] [--points POINTS]
                           [--crop CROP] [--svg SVG]
                           img

    positional arguments:
      img              path or url to a GeoTIFF image file with RPC metadata

    optional arguments:
      -h, --help       show this help message and exit
      --lon LON        longitude
      --lat LAT        latitude
      -z Z             altitude, in meters
      --points POINTS  path to a 2/3 columns txt file: lon lat [z]
      --crop CROP      path to a tif crop previously produced by rpcm. Image
                       coordinates are computed with respect to this crop.
      --svg SVG        path to an svg file where to plot projected points.


## Localization

    $ rpcm localization -h
    usage: rpcm localization [-h] [-x X] [-y Y] [-z Z] [--points POINTS]
                         [--crop CROP]
                         img

    positional arguments:
      img              path or url to a GeoTIFF image file with RPC metadata

    optional arguments:
      -h, --help       show this help message and exit
      -x X             horizontal pixel coordinate (i.e. column index)
      -y Y             vertical pixel coordinate (i.e. row index)
      -z Z             altitude, in meters
      --points POINTS  path to a 3 columns txt file: x y z
      --crop CROP      path to a tif crop previously produced by rpcm. Image
                       coordinates are interpreted with respect to this crop.


## Crop

    $ rpcm crop -h
    usage: rpcm crop [-h] [-z Z] img aoi crop

    positional arguments:
      img         path to a GeoTIFF image file with RPC metadata
      aoi         path to geojson file defining the area of interest (AOI)
      crop        path to the output cropped tif image

    optional arguments:
      -h, --help  show this help message and exit
      -z Z        altitude of the crop center


## Footprint

    $ rpcm footprint -h
    usage: rpcm footprint [-h] [-z Z] img

    positional arguments:
      img         path or url to a GeoTIFF image file with RPC metadata

    optional arguments:
      -h, --help  show this help message and exit
      -z Z        altitude, in meters


## Angle

    $ rpcm angle -h
    usage: rpcm angle [-h] [--lon LON] [--lat LAT] [-z Z] img1 img2

    positional arguments:
      img1        path to a GeoTIFF image file with RPC metadata
      img2        path to a GeoTIFF image file with RPC metadata

    optional arguments:
      -h, --help  show this help message and exit
      --lon LON   longitude
      --lat LAT   latitude
      -z Z        altitude


# Common issues

_Warning_: A `rasterio` issue on Ubuntu causes the need for this environment
variable (more info on [rasterio's
github](https://github.com/mapbox/rasterio/issues/942)):

    export CURL_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
