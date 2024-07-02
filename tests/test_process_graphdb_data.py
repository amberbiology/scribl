__author__ = 'Amber Biology'

import scribl
import os
import shutil
import datetime
import pytest
from scribl.process_graphdb_data import GraphDB

test_data_dir = 'tests/test_data'
test_data_file = 'zotero_export_1.csv'
updated_test_data_file = 'zotero_export_2.csv'
error_data_file = 'zotero_errors.csv'
zotero_csv_data = os.path.join(test_data_dir, test_data_file)
updated_csv_data = os.path.join(test_data_dir, updated_test_data_file)
error_csv_data = os.path.join(test_data_dir, error_data_file)

# fixture function to create unique sandbox directories
@pytest.fixture(scope="function")
def sandbox_paths(tmpdir_factory):
    test_sandbox_dir = tmpdir_factory.mktemp("scribl_sandbox")
    test_db_dir = os.path.join(test_sandbox_dir, 'test_graphdb')
    return test_sandbox_dir, test_db_dir

# utility function to generate timestamps
def generate_timestamp(text_format=False):
    now = datetime.datetime.now()
    if text_format:
        return now.strftime('%H:%M:%S %m-%d-%Y')
    else:
        return now.strftime('%Y_%m_%d_%H%M%S')

def test_start():
    print('\n\nTesting scribl graph DB data processing ...')

def test_graphdb_processing():
    print('Testing graph DB processing ...')
    gdb = GraphDB(zotero_csv_data)
    assert len(gdb.db['article']) == 11
    assert len(gdb.db['category']) == 15
    assert len(gdb.db['agent']) == 79
    assert len(gdb.db['process']) == 49
    assert len(gdb.db['resource']) == 0
    assert len(gdb.db['warnings']) == 0
    assert len(gdb.db['errors']) == 0
    assert (list(gdb.db.keys())) == ['article', 'category', 'agent', 'process', 'resource', 'warnings', 'errors', 'relationships']
    # relationships
    assert len(gdb.db['relationships']['RELATES']) == 41
    assert len(gdb.db['relationships']['REFERENCES']) == 0
    assert len(gdb.db['relationships']['DESCRIBES']) == 53
    assert len(gdb.db['relationships']['MENTIONS']) == 97
    assert len(gdb.db['relationships']['ACTIVATES']) == 32
    assert len(gdb.db['relationships']['INHIBITS']) == 18
    assert len(gdb.db['relationships']['REGULATES']) == 2
    assert len(gdb.db['relationships']['INVOLVES']) == 53
    assert len(gdb.db['relationships']['BINDS']) == 34
    assert len(gdb.db['relationships']['MODIFIES']) == 7
    assert len(gdb.db['relationships']['GENERATES']) == 7
    assert len(gdb.db['relationships']['REMOVES']) == 0
    assert len(gdb.db['relationships']['RESOURCE_DESCRIBES']) == 0
    assert len(gdb.db['relationships']['RESOURCE_MENTIONS']) == 0

def test_generate_cypher():
    print('Testing generate cypher ...')
    gdb = GraphDB(zotero_csv_data)
    cypher = gdb.generate_cypher()
    assert len(cypher) == 499
    assert cypher[0][:115] == 'MERGE (:ARTICLE {key:"9JHZ54TS", zotero_key:"9JHZ54TS" , title:"Frontotemporal Dementias" , url:"https://journals.l'
    assert cypher[-2] == 'MATCH (p1:PROCESS {name:"ulk1 expression"}), (p2:AGENT {name:"ulk1"})\nMERGE (p1)-[:GENERATES]->(p2);'
    assert cypher[-1] == 'MATCH (a1:AGENT)-[r1:BINDS]->(a2:AGENT) WITH a1,a2 MATCH(a1:AGENT)<-[r2:BINDS]-(a2:AGENT) DELETE r2;'

def test_export_cypher_text():
    print('Testing export cypher ...')
    gdb = GraphDB(zotero_csv_data)
    cypher = gdb.generate_cypher()
    cypher_text = gdb.export_cypher_text(cypher)
    assert len(cypher_text) == 81423
    cypher_lines = cypher_text.split('\n')
    assert len(cypher_lines) == 1081

def test_db_snapshots(sandbox_paths):
    print('Testing save and load DB snapshot ...')
    test_sandbox_dir, test_db_dir = sandbox_paths
    gdb = GraphDB(zotero_csv_data)
    now = generate_timestamp()
    snapshot_filename = '{}_db_snapshot.dat'.format(now)
    snapshot_filepath = os.path.join(test_sandbox_dir, snapshot_filename)
    gdb.save_db(snapshot_filepath)
    assert os.path.getsize(snapshot_filepath) == 35445
    loaded_snapshot = gdb.load_db(snapshot_filepath)
    assert loaded_snapshot == gdb.db

def test_db_diff(sandbox_paths):
    print('Testing generate DB diff ...')
    test_sandbox_dir, test_db_dir = sandbox_paths
    gdb = GraphDB(zotero_csv_data)
    now = generate_timestamp()
    snapshot_filename = '{}_db_snapshot.dat'.format(now)
    snapshot_filepath = os.path.join(test_sandbox_dir, snapshot_filename)
    gdb.save_db(snapshot_filepath)
    # create new graph db with snapshot
    odb = GraphDB(snapshot_filepath, export_type=scribl.DB_EXPORT)
    assert gdb.db == odb.db
    # no difference between current DB and snapshot so diff length should be zero
    diff_db = gdb.generate_db_diff(odb)
    for field in diff_db:
        if field == 'relationships':
            for rfield in diff_db['relationships']:
                assert len(diff_db[field][rfield]) == 0
        else:
            assert len(diff_db[field]) == 0
    # now load updated db to test actual diff
    ddb = GraphDB(updated_csv_data)
    assert len(ddb.db['article']) == 13
    assert len(ddb.db['category']) == 16
    assert len(ddb.db['agent']) == 85
    assert len(ddb.db['process']) == 58
    assert len(ddb.db['resource']) == 0
    assert len(ddb.db['warnings']) == 0
    assert len(ddb.db['errors']) == 0
    assert (list(ddb.db.keys())) == ['article', 'category', 'agent', 'process', 'resource', 'warnings', 'errors', 'relationships']
    # relationships
    assert len(ddb.db['relationships']['RELATES']) == 45
    assert len(ddb.db['relationships']['REFERENCES']) == 0
    assert len(ddb.db['relationships']['DESCRIBES']) == 66
    assert len(ddb.db['relationships']['MENTIONS']) == 109
    assert len(ddb.db['relationships']['ACTIVATES']) == 37
    assert len(ddb.db['relationships']['INHIBITS']) == 26
    assert len(ddb.db['relationships']['REGULATES']) == 3
    assert len(ddb.db['relationships']['INVOLVES']) == 58
    assert len(ddb.db['relationships']['BINDS']) == 34
    assert len(ddb.db['relationships']['MODIFIES']) == 7
    assert len(ddb.db['relationships']['GENERATES']) == 10
    assert len(ddb.db['relationships']['REMOVES']) == 0
    assert len(ddb.db['relationships']['RESOURCE_DESCRIBES']) == 0
    assert len(ddb.db['relationships']['RESOURCE_MENTIONS']) == 0
    # generate diff
    db_diff = ddb.generate_db_diff(gdb)
    assert len(db_diff['article']) == 2
    assert len(db_diff['category']) == 1
    assert len(db_diff['agent']) == 8
    assert len(db_diff['process']) == 9
    assert len(db_diff['resource']) == 0
    # relationships
    assert len(db_diff['relationships']['RELATES']) == 4
    assert len(db_diff['relationships']['REFERENCES']) == 0
    assert len(db_diff['relationships']['DESCRIBES']) == 13
    assert len(db_diff['relationships']['MENTIONS']) == 12
    assert len(db_diff['relationships']['ACTIVATES']) == 5
    assert len(db_diff['relationships']['INHIBITS']) == 8
    assert len(db_diff['relationships']['REGULATES']) == 1
    assert len(db_diff['relationships']['INVOLVES']) == 5
    assert len(db_diff['relationships']['BINDS']) == 0
    assert len(db_diff['relationships']['MODIFIES']) == 0
    assert len(db_diff['relationships']['GENERATES']) == 3
    assert len(db_diff['relationships']['REMOVES']) == 0
    assert len(db_diff['relationships']['RESOURCE_DESCRIBES']) == 0
    assert len(db_diff['relationships']['RESOURCE_MENTIONS']) == 0
    # generate diff cypher
    diff_cypher = ddb.generate_cypher(diff_db=db_diff)
    assert len(diff_cypher) == 72
    diff_cypher_text = ddb.export_cypher_text(diff_cypher)
    diff_cypher_lines = diff_cypher_text.split('\n')
    assert len(diff_cypher_lines) == 143
    assert diff_cypher_lines[0][:98] == 'MERGE (:ARTICLE {key:"255SUP2B", zotero_key:"255SUP2B" , title:"Comparative interactomics analysis'
    assert diff_cypher_lines[136] == 'MATCH (p1:PROCESS {name:"atp6v1g1 expression"}), (p2:AGENT {name:"atp6v1g1"})'
    assert diff_cypher_lines[138] == 'MATCH (p1:PROCESS {name:"chaperone-mediated folding of atp6v1g1"}), (p2:AGENT {name:"atp6v1g1"})'

def test_db_errors():
    print('Testing DB error handling ...')
    ddb = GraphDB(error_csv_data)
    assert len(ddb.db['article']) == 13
    assert len(ddb.db['category']) == 16
    assert len(ddb.db['agent']) == 85
    assert len(ddb.db['process']) == 58
    assert len(ddb.db['resource']) == 0
    assert len(ddb.db['warnings']) == 0
    assert len(ddb.db['errors']) == 3
    ref = {('GAKQTWWR', 'Exosome secretion is a key pathway for clearance o'): ['Line: 0 Unable to parse statment [::category ::category ::agent :protein]'],
           ('NP7Q3SDK', 'Dynamic Modeling of the Interaction Between Autoph'): ['Unrecognized entity "diddly squat" in relationship: ::agent atg1-atg13 complex ... | diddly squat'],
           ('5PJEZC9C', 'A C9ORF72/SMCR8-containing complex regulates ULK1 '): ['Line: 21 Invalid relationship "~ ulk1" for "::process" ignored [::process autophagy @ ulk1 complex ~ ulk1]']}
    assert ddb.db['errors'] == ref

def test_db_tools():
    print('Testing DB tools ...')
    gdb = GraphDB(updated_csv_data)
    assert len(gdb.catalog('process')) == 58
    assert len(gdb.catalog('BINDS', relationship=True)) == 34
    ref = {'urls': ['https://www.uniprot.org/uniprot/O75385'], 'tags': [], 'notes': ['ulk1 is phosphorylated by mtor'],
           'labels': [':protein'], 'synonyms': ['ulk1', 'atg1']}
    assert gdb.get('agent', 'ulk1') == ref
    rel_ulk1 = gdb.show_relationships('agent', 'ulk1')
    assert len(rel_ulk1) == 15
    assert rel_ulk1['search'] == ('agent', 'ulk1')
    assert rel_ulk1['INVOLVES'][0] == ('formation of atg1-atg13 complex', 'ulk1')
    assert rel_ulk1['INVOLVES'][-1] == ('ulk1 phosphorylation', 'ulk1')
    assert len(rel_ulk1['INVOLVES']) == 4
    print(rel_ulk1)

def test_synonym_checking():
    print('Testing synonym checking ...')
    gdb = GraphDB(updated_csv_data)
    syn_check = gdb.check_synonyms()
    assert syn_check['synonym appears in different agents'] ==  {'dup_sym': ['ambra', 'caspase-1']}
    assert syn_check['synonym appears as an agent'] == []

def test_agent_label_checking():
    print('Testing agent label checking ...')
    gdb = GraphDB(updated_csv_data)
    label_check = gdb.check_agent_labels()
    assert label_check == ['ca2+', 'rapamycin']
