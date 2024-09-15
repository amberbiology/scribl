__author__ = 'Amber Biology'

import scribl
import os
import pytest
from scribl.scribl import main

# fixture function to create unique sandbox directories
@pytest.fixture(scope="function")
def sandbox_paths(tmpdir_factory):
    test_sandbox_dir = tmpdir_factory.mktemp("scribl_sandbox")
    return test_sandbox_dir

def test_pyzotero_network(sandbox_paths):
    test_sandbox_dir = sandbox_paths
    curr_dir = os.getcwd() # save current directory

    os.chdir(test_sandbox_dir) # change current directory
    main(["scribl", "-g", "new_graphdb", "--zotero-library", "5251557:group",
          "--networkx-fig", "graphdb-visual.png" ,"--graphmlfile", "graphdb.xml", "--cyphertextfile", "graphdb.cypher"])

    assert os.path.exists("graphdb-visual.png") == True
    assert os.path.exists("graphdb.xml") == True
    assert os.path.exists("graphdb.cypher") == True

    os.chdir(curr_dir)
