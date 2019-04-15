# RPCM - Rational Polynomial Camera Model

Python implementation of the Rational Polynomial Camera (RPC) model for optical satellite images.

[Carlo de Franchis](mailto:carlo.de-franchis@ens-cachan.fr), Gabriele Facciolo, Enric Meinhardt-Llopis
(CMLA, ENS Cachan, Université Paris-Saclay) 2013-19

`rpcm` is a Python library and command line tool for geolocating satellite images
with RPCs. Its main source code repository is https://github.com/cmla/rpcm.


# Installation

To install `rpcm` from PyPI:

    pip install rpcm

Alternatively, to install `rpcm` from sources:

    git clone https://github.com/cmla/rpcm.git
    cd rpcm
    pip install -e .


# Usage

`rpcm` is a Python library that can be imported into other applications. A
Jupyter notebook tutorial covering the main features of the library is included (TODO).

`rpcm` also comes with a Command Line Interface (CLI). The `rpcm` CLI has an
extensive help that can be printed with the `-h` and `--help` switches.

    $ rpcm -h
    usage: rpcm [-h] {projection, localization} ...

There are two subcommands, `projection` and `localization`, each of which has its own help.


# Common issues

_Warning_: A `rasterio` issue on Ubuntu causes the need for this environment
variable (more info on [rasterio's
github](https://github.com/mapbox/rasterio/issues/942)):

    export CURL_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
