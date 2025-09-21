import os

import pytest

from rpcm.rpc_model import rpc_from_rpc_file, RPCModel
from rpcm.rpc_file_readers import read_rpc_file

here = os.path.abspath(os.path.dirname(__file__))
files_dir = os.path.join(here, "test_rpc_files")


def supported_files():
    """
    List the files that should be correctly parsed by `rpc_from_rpc_file`.
    """
    filenames = [
        "rpc_IKONOS.txt",
        "rpc_PLEIADES.xml",
        "rpc_SPOT6.xml",
        "rpc_WV1.xml",
        "rpc_WV2.xml",
        "rpc_WV3.xml",
    ]

    return [os.path.join(files_dir, filename) for filename in filenames]


def supported_files_multi_model():
    """
    List the files that should be correctly parsed with multiple RPC models.
    """
    filenames = ["ENMAP01-____L1B-DT0000001011_20220609T081225Z_001_V010111_20230119T143357Z-METADATA.XML"]

    return [os.path.join(files_dir, filename) for filename in filenames]


def unsupported_files():
    """
    List the files that `rpc_from_rpc_file` should not be able to parse.
    """
    filenames = ["rpc_unsupported.xml"]

    return [os.path.join(files_dir, filename) for filename in filenames]


@pytest.mark.parametrize("filepath", supported_files())
def test_successful_rpc_file_parsing(filepath):
    """
    Check that filepath can be parsed without errors being raised
    """
    rpc_from_rpc_file(filepath)


@pytest.mark.parametrize("filepath", supported_files_multi_model())
def test_successful_rpc_file_parsing_multi_model(filepath):
    """
    Check that filepath can be parsed without errors being raised
    """
    rpc = read_rpc_file(filepath)
    assert len(rpc.keys()) > 1
    model = RPCModel(rpc["1"])


@pytest.mark.parametrize("filepath", unsupported_files())
def test_failing_rpc_file_parsing(filepath):
    """
    Check that filepath raises an error when being parsed
    """
    with pytest.raises(NotImplementedError):
        rpc_from_rpc_file(filepath)
