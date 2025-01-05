from __future__ import annotations

__author__ = "Amber Biology"

import os
from pathlib import Path

import pytest

from scribl.scribl import main


# fixture function to create unique sandbox directories
@pytest.fixture
def sandbox_paths(tmpdir_factory):
    return tmpdir_factory.mktemp("scribl_sandbox")


def test_pyzotero_network(sandbox_paths):
    test_sandbox_dir = sandbox_paths
    curr_dir = Path.cwd()  # save current directory

    os.chdir(test_sandbox_dir)  # change current directory
    ret_val = main(
        [
            "scribl",
            "-g",
            "new_graphdb",
            "--zotero-library",
            "5251557:group",
            "--networkx-fig",
            "graphdb-visual.png",
            "--graphmlfile",
            "graphdb.xml",
            "--cyphertextfile",
            "graphdb.cypher",
        ]
    )

    assert ret_val == 0
    # check generated files
    assert Path("graphdb-visual.png").exists()
    assert Path("graphdb.xml").exists()
    assert Path("graphdb.cypher").exists()

    os.chdir(curr_dir)
