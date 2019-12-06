import copy
import os

import pytest

from rpcm import rpc_from_rpc_file

here = os.path.abspath(os.path.dirname(__file__))
files_dir = os.path.join(here, "test_rpc_files")


@pytest.fixture()
def rpc1():
    """
    Planet L1A RPC fixture
    """
    filename = "rpc_PLANET_L1A.txt"
    return rpc_from_rpc_file(os.path.join(files_dir, filename))


@pytest.fixture()
def rpc2():
    """
    Planet L1B RPC fixture
    """
    filename = "rpc_PLANET_L1B.txt"
    return rpc_from_rpc_file(os.path.join(files_dir, filename))


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
    assert rpc1.equal_projection(rpc2)


@pytest.mark.parametrize("shift, equal", [(1e-8, True), (1e-3, False)])
def test_rpc_close_comparison(rpc1, shift, equal):
    rpc2 = copy.deepcopy(rpc1)
    rpc2.col_num = [coeff + shift for coeff in rpc2.col_num]
    if equal:
        assert rpc2 == rpc1
    else:
        assert rpc2 != rpc1
