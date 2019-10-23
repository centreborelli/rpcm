import os

import pytest

from rpcm import RPCModel
from rpcm.rpc_file_readers import read_rpc_ikonos
from rpcm.rpc_model import MaxLocalizationIterationsError

here = os.path.abspath(os.path.dirname(__file__))
files_dir = os.path.join(here, "test_rpc_files")


def test_localization_break():
    """
    The localization of the top-left corner of the image with the
    Skysat L1A RPC included in the test data folder doesn't converge
    with an altitude of 70m, but it does with an altitude of 90m,
    so we test both behaviors
    """
    path = os.path.join(files_dir, "20191015_073816_ssc1d3_0011_basic_l1a_panchromatic_dn_RPC.TXT")
    with open(path) as f:
        rpc = RPCModel(read_rpc_ikonos(f.read()))

    with pytest.raises(MaxLocalizationIterationsError):
        rpc.localization(0, 0, 70)

    rpc.localization(0, 0, 90)
