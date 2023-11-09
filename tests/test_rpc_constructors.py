import os
import shutil
import numpy as np
import pytest
from rpcm import RPCModel, rpc_from_geotiff
from rpcm.utils import rasterio_write
from rpcm.rpc_file_readers import read_rpc_file

here = os.path.abspath(os.path.dirname(__file__))
files_dir = os.path.join(here, "test_rpc_files")


def _read_dict_from_file(filename="rpc_IKONOS.txt"):
    filepath = os.path.join(files_dir, filename)
    return read_rpc_file(filepath)


def test_rpc_constructors():
    """
    Test that the two constructors of the RPCModel class yield the same object.
    """
    geotiff_dict = _read_dict_from_file("rpc_IKONOS.txt")
    geotiff_rpc = RPCModel(geotiff_dict, dict_format="geotiff")

    rpcm_dict = geotiff_rpc.__dict__
    rpcm_rpc = RPCModel(rpcm_dict, dict_format="rpcm")

    assert geotiff_rpc == rpcm_rpc


@pytest.fixture
def tmp_geotiff(tmp_path):
    """
    provides a geotiff with some rpcs, stored in the tmp_path
    """
    data = np.ones([1, 10, 10], dtype=np.uint8)
    rpc = RPCModel(_read_dict_from_file())
    tags = dict(ns="RPC", **rpc.to_geotiff_dict())

    geotiff_path = os.fspath(tmp_path / "test_geo.tif")
    rasterio_write(geotiff_path, data, tags=tags)
    return geotiff_path


def _add_auxiliary_rpc_file(tif_path, rpc_filename="rpc_IKONOS.txt"):
    """
    Adds an RPC textfile {basename}_RPC.txt, next to the given `tif_path`
    (with filename {basename}.tif).
    GDAL recognizes such files, and automatically reads the information from
    them as if it was stored inside the tif tags.
    """
    src = os.path.join(files_dir, rpc_filename)
    dst = tif_path[:-len(".tif")] + "_RPC.txt"
    shutil.copyfile(src, dst)


def test_from_geotiff(tmp_geotiff, tmp_path):
    # Verify that RPCs read from a geotiff match the textual file
    txt_rpc = RPCModel(_read_dict_from_file())
    tif_rpc = rpc_from_geotiff(tmp_geotiff)
    assert tif_rpc == txt_rpc

    # verify that RPCs from geotiff work if there is an auxiliary file
    _add_auxiliary_rpc_file(tmp_geotiff)
    tif_rpc = rpc_from_geotiff(tmp_geotiff)
    assert tif_rpc == txt_rpc
