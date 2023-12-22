__author__ = 'Amber Biology'

import scribl, os
from scribl.process_zotero import ZoteroCSV

test_data_dir = 'tests/test_data'
test_data_file = '2022_01_03_171311_zotero_data.csv'
zotero_csv_data = os.path.join(test_data_dir, test_data_file)

def test_start():
    print('\n\nTesting Zotero csv data processing ...')

def test_zotero_csv_processing():
    print('Testing Zotero csv processing ...')
    zd = ZoteroCSV(zotero_csv_data)
    assert len(zd.data) == 120
    assert len(zd.data['FSEFS7AI']) == 87
    assert len(zd.data['98JSAHFS']) == 87
    ref = {'zotero_key': 'Key', 'title': 'Title', 'url': 'Url', 'year': 'Publication Year', 'author': 'Author',
           'journal_title': 'Publication Title', 'journal_abreviation': 'Journal Abbreviation', 'abstract': 'Abstract Note'}
    assert zd.keymap == ref
