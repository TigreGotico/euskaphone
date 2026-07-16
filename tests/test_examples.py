"""Every example script runs without error (offline)."""
import glob
import os
import runpy

import pytest

_EXAMPLES = sorted(glob.glob(
    os.path.join(os.path.dirname(__file__), "..", "examples", "*.py")))


@pytest.mark.parametrize("path", _EXAMPLES,
                         ids=[os.path.basename(p) for p in _EXAMPLES])
def test_example_runs(path):
    runpy.run_path(path, run_name="__main__")
