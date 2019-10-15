import os

import pytest

from rpcm import rpc_from_rpc_file

here = os.path.abspath(os.path.dirname(__file__))
files_dir = os.path.join(here, "test_rpc_files")


def rpc_files():
    """
    Fixture to the RPC files used for the tests
    """
    filenames = ["rpc_PLANET_L1{}.txt".format(a_b) for a_b in ["A", "B"]]
    return [[rpc_from_rpc_file(os.path.join(files_dir, filename)) for filename in filenames]]


@pytest.mark.parametrize("rpc1, rpc2", rpc_files())
def test_rpc_comparison(rpc1, rpc2):
    """
    This test is run on two RPCs coming from Planet Skysat images,
    which are equal except for their offset and scale coefficients
    (this is because the two images have the same RPC model,
    but different sizes)
    """
    assert rpc1 == rpc1
    assert rpc1 != rpc2
    assert not rpc1.equal_offsets(rpc2)
    assert not rpc1.equal_scales(rpc2)
    assert rpc1.equal_coeffs(rpc2)
