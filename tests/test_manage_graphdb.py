from __future__ import annotations

__author__ = "Amber Biology"


import os
import time
from pathlib import Path
from xml.etree import ElementTree as ET  # for GraphML checking

import pytest

from scribl.manage_graphdb import GraphDBInstance

test_data_dir = Path("tests") / "test_data"
test_data_file = "zotero_export_1.csv"
updated_test_data_file = "zotero_export_2.csv"
zotero_csv_data = test_data_dir / test_data_file
updated_csv_data = test_data_dir / updated_test_data_file


# fixture function to create unique sandbox directories
@pytest.fixture
def sandbox_paths(tmpdir_factory):
    test_sandbox_dir = tmpdir_factory.mktemp("scribl_sandbox")
    test_db_dir = Path(test_sandbox_dir) / "test_graphdb"
    return test_sandbox_dir, test_db_dir


def test_graphdb_initialization(sandbox_paths):
    print("Testing graph DB initialization ...")
    test_sandbox_dir, test_db_dir = sandbox_paths
    GraphDBInstance(test_db_dir)
    assert Path.exists(test_db_dir)
    for folder in ["backup", "config", "db_snapshots", "zotero_csv_exports"]:
        folder_path = test_db_dir / folder
        assert Path.exists(folder_path)


def test_graphdb_metadata(sandbox_paths):
    print("Testing graph DB metadata ...")
    test_sandbox_dir, test_db_dir = sandbox_paths
    gdb = GraphDBInstance(test_db_dir)
    db_name = "Systems Biology Literature DB for testing"
    curator = "Amber Biology (info@amberbiology.com)"
    description = "A systems biology literature DB built by Amber Biology for testing"
    gdb.set_metadata(db_name, curator, description)
    folder_path = test_db_dir / "config"
    metadata_file = folder_path / "metadata.txt"
    annotations_file = folder_path / "annotations.txt"
    assert Path.exists(metadata_file)
    assert Path.exists(annotations_file)
    gdb.add_annotation("Bill Lumbergh", "Hey Peter. What's up?")
    gdb.add_annotation("Michael Scott", "That's what she said")
    with open(metadata_file) as mfile:
        lines = mfile.readlines()
    assert lines[0][0:9] == "Created: "
    assert lines[1].strip() == "Curator: Amber Biology (info@amberbiology.com)"
    assert lines[2].strip() == "DB Name: Systems Biology Literature DB for testing"
    assert (
        lines[3].strip()
        == "Summary: A systems biology literature DB built by Amber Biology for testing"
    )
    with open(annotations_file) as a_file:
        lines = a_file.readlines()
    assert lines[0][0:13] == "Initialized: "
    assert lines[1][0:15] == "Bill Lumbergh: "
    assert lines[1][36:].strip() == "Hey Peter. What's up?"
    assert lines[2][0:15] == "Michael Scott: "
    assert lines[2][36:].strip() == "That's what she said"
    assert len(gdb.generate_metadata_cypher()) == 653


def test_graphdb_import(sandbox_paths):
    print("Testing graph DB import ...")
    test_sandbox_dir, test_db_dir = sandbox_paths
    gdb = GraphDBInstance(test_db_dir)
    db_name = "Systems Biology Literature DB for testing"
    curator = "Amber Biology (info@amberbiology.com)"
    description = "A systems biology literature DB built by Amber Biology for testing"
    gdb.set_metadata(db_name, curator, description)
    folder_path = test_db_dir / "zotero_csv_exports"
    # clear exports folder
    for csvfile in os.listdir(folder_path):
        rmfilepath = folder_path / csvfile
        os.remove(rmfilepath)
    assert len(os.listdir(folder_path)) == 0
    gdb.import_zotero_csv(zotero_csv_data)
    assert len(os.listdir(folder_path)) == 1
    time.sleep(1.1)
    gdb.import_zotero_csv(updated_csv_data)
    assert len(os.listdir(folder_path)) == 2
    importpath = folder_path / sorted(os.listdir(folder_path))[-1]
    gdb.load_zotero_csv()
    assert gdb.current_zotero_csv == importpath
    assert len(gdb.graphdb.db["article"]) == 13


def test_graphdb_reimport(sandbox_paths):
    print("Testing graph DB re-import ...")
    test_sandbox_dir, test_db_dir = sandbox_paths
    gdb = GraphDBInstance(test_db_dir)
    db_name = "Systems Biology Literature DB for testing"
    curator = "Amber Biology (info@amberbiology.com)"
    description = "A systems biology literature DB built by Amber Biology for testing"
    gdb.set_metadata(db_name, curator, description)
    folder_path = test_db_dir / "zotero_csv_exports"
    # clear exports folder
    for csvfile in os.listdir(folder_path):
        rmfilepath = folder_path / csvfile
        os.remove(rmfilepath)
    assert len(os.listdir(folder_path)) == 0
    gdb.import_zotero_csv(zotero_csv_data)
    assert len(os.listdir(folder_path)) == 1
    imports = os.listdir(gdb.zotero_csv_exports_folder)
    gdb.import_zotero_csv(zotero_csv_data, overwrite=True)
    assert len(os.listdir(folder_path)) == 1
    assert os.listdir(gdb.zotero_csv_exports_folder) == imports


def test_graphdb_snapshots(sandbox_paths):
    print("Testing graph DB snapshots ...")
    test_sandbox_dir, test_db_dir = sandbox_paths
    gdb = GraphDBInstance(test_db_dir)
    db_name = "Systems Biology Literature DB for testing"
    curator = "Amber Biology (info@amberbiology.com)"
    description = "A systems biology literature DB built by Amber Biology for testing"
    gdb.set_metadata(db_name, curator, description)
    gdb.import_zotero_csv(zotero_csv_data)
    gdb.load_zotero_csv()
    folder_path = test_db_dir / "db_snapshots"
    assert len(os.listdir(folder_path)) == 0
    snapshotpath = gdb.save_db_snapshot()
    assert len(os.listdir(folder_path)) == 1
    assert gdb.get_current_timestamp() == gdb.current_zotero_csv.name[:17]
    # test load snapshot method
    loaded_db = gdb.load_db_snapshot(snapshotpath.name)
    assert loaded_db == gdb.graphdb.db


def test_cypher_generation(sandbox_paths):
    print("Testing cypher generation ...")
    test_sandbox_dir, test_db_dir = sandbox_paths
    gdb = GraphDBInstance(test_db_dir)
    db_name = "Systems Biology Literature DB for testing"
    curator = "Amber Biology (info@amberbiology.com)"
    description = "A systems biology literature DB built by Amber Biology for testing"
    gdb.set_metadata(db_name, curator, description)
    gdb.import_zotero_csv(zotero_csv_data)
    gdb.load_zotero_csv()
    cypher_text = gdb.export_cypher_text()
    assert len(cypher_text) == 81423
    assert (
        cypher_text[:100]
        == 'MERGE (:ARTICLE {key:"9JHZ54TS", zotero_key:"9JHZ54TS" , title:"Frontotemporal Dementias" , url:"htt'
    )
    assert (
        cypher_text[-100:]
        == "MATCH (a1:AGENT)-[r1:BINDS]->(a2:AGENT) WITH a1,a2 MATCH(a1:AGENT)<-[r2:BINDS]-(a2:AGENT) DELETE r2;"
    )


def test_graphml_generation(sandbox_paths):
    print("Testing GraphML generation ...")
    test_sandbox_dir, test_db_dir = sandbox_paths
    gdb = GraphDBInstance(test_db_dir)
    db_name = "Systems Biology Literature DB for testing"
    curator = "Amber Biology (info@amberbiology.com)"
    description = "A systems biology literature DB built by Amber Biology for testing"
    gdb.set_metadata(db_name, curator, description)
    gdb.import_zotero_csv(zotero_csv_data)
    gdb.load_zotero_csv()
    graphml_text = gdb.export_graphml_text()
    parsed_xml = ET.fromstring(graphml_text)
    ns = {"gml": "http://graphml.graphdrawing.org/xmlns"}  # define namespace

    assert type(parsed_xml) is ET.Element  # make sure XML is well-formed
    assert len(parsed_xml.findall("gml:graph/gml:node", ns)) == 154  # total nodes
    assert len(parsed_xml.findall("gml:graph/gml:edge", ns)) == 344  # total nodes


def test_graphdb_backup(sandbox_paths):
    print("Testing graph DB backup ...")
    test_sandbox_dir, test_db_dir = sandbox_paths
    gdb = GraphDBInstance(test_db_dir)
    db_name = "Systems Biology Literature DB for testing"
    curator = "Amber Biology (info@amberbiology.com)"
    description = "A systems biology literature DB built by Amber Biology for testing"
    gdb.set_metadata(db_name, curator, description)
    gdb.import_zotero_csv(zotero_csv_data)
    gdb.load_zotero_csv()
    folder_path = test_db_dir / "backup"
    assert len(os.listdir(folder_path)) == 0
    backup_file = gdb.backup_db()
    assert os.listdir(folder_path)[0] == backup_file.name
    assert len(os.listdir(folder_path)) == 1
    gdb.save_db_snapshot()
    folder_path = test_db_dir / "db_snapshots"
    assert os.listdir(folder_path)[0][:17] == gdb.get_current_timestamp()


def test_cypher_diff(sandbox_paths):
    print("Testing generation of cypher diff text ...")
    test_sandbox_dir, test_db_dir = sandbox_paths
    gdb = GraphDBInstance(test_db_dir)
    db_name = "Systems Biology Literature DB for testing"
    curator = "Amber Biology (info@amberbiology.com)"
    description = "A systems biology literature DB built by Amber Biology for testing"
    gdb.set_metadata(db_name, curator, description)
    gdb.import_zotero_csv(zotero_csv_data)
    gdb.load_zotero_csv()
    snapshotpath = gdb.save_db_snapshot()
    gdb.import_zotero_csv(updated_csv_data)
    gdb.load_zotero_csv()
    diff_db = gdb.generate_db_diff(snapshotpath)
    diff_cypher = gdb.export_cypher_text(diff=diff_db)
    assert len(diff_cypher) == 13273
    assert (
        diff_cypher[:66]
        == 'MERGE (:ARTICLE {key:"255SUP2B", zotero_key:"255SUP2B" , title:"Co'
    )
    assert diff_cypher[-50:] == " MATCH(a1:AGENT)<-[r2:BINDS]-(a2:AGENT) DELETE r2;"


def test_inspect_db(sandbox_paths):
    print("Testing inspection of db contents ...")
    test_sandbox_dir, test_db_dir = sandbox_paths
    gdb = GraphDBInstance(test_db_dir)
    db_name = "Systems Biology Literature DB for testing"
    curator = "Amber Biology (info@amberbiology.com)"
    description = "A systems biology literature DB built by Amber Biology for testing"
    gdb.set_metadata(db_name, curator, description)
    gdb.import_zotero_csv(zotero_csv_data)
    gdb.load_zotero_csv()
    ref = {
        "article": 11,
        "category": 15,
        "agent": 79,
        "process": 49,
        "resource": 0,
        "warnings": 0,
        "errors": 0,
        "relationships": {
            "RELATES": 41,
            "REFERENCES": 0,
            "DESCRIBES": 53,
            "MENTIONS": 97,
            "ACTIVATES": 32,
            "INHIBITS": 18,
            "REGULATES": 2,
            "INVOLVES": 53,
            "BINDS": 34,
            "MODIFIES": 7,
            "GENERATES": 7,
            "REMOVES": 0,
            "RESOURCE_DESCRIBES": 0,
            "RESOURCE_MENTIONS": 0,
        },
        "list_contents": {},
    }
    assert gdb.inspect_db() == ref
    contents = gdb.inspect_db(
        list_contents=["agent", "process", ("relationships", "BINDS")]
    )
    assert len(contents["list_contents"]["agent"]) == 79
    assert len(contents["list_contents"]["process"]) == 49
    assert len(contents["list_contents"]["relationships"]["BINDS"]) == 34
