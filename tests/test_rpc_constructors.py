import os

from rpcm import RPCModel
from rpcm.rpc_file_readers import read_rpc_file

here = os.path.abspath(os.path.dirname(__file__))
files_dir = os.path.join(here, "test_rpc_files")


def test_rpc_constructors():
    """
    Test that the two constructors of the RPCModel class yield the same object.
    """
    filepath = os.path.join(files_dir, "rpc_IKONOS.txt")

    geotiff_dict = read_rpc_file(filepath)
    geotiff_rpc = RPCModel(geotiff_dict, dict_format="geotiff")

    rpcm_dict = geotiff_rpc.__dict__
    rpcm_rpc = RPCModel(rpcm_dict, dict_format="rpcm")

    assert geotiff_rpc == rpcm_rpc
