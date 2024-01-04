__author__ = 'Amber Biology'

import scribl

def test_start():
    print('\n\nTesting scribl_code package setup ...')

def test_agent_labels():
    print('Testing scribl_code agent labels ...')
    assert scribl.agent_types == ['protein', 'gene', 'dna', 'rna', 'mrna', 'complex', 'organelle', 'biomarker']
    assert scribl.agents == [':protein', ':gene', ':dna', ':rna', ':mrna', ':complex', ':organelle', ':biomarker']

def test_statements():
    print('Testing scribl_code statements ...')
    assert scribl.statements == ['::category', '::agent', '::process', '::resource']
    assert scribl.fields == {'url': ':url', 'tag': ':tag', 'syn': ':syn', 'txt': ':txt'}

def test_relation_lookup():
    print('Testing relation lookup ...')
    assert scribl.relationships == ['>', '<', '=', '@', '|', '~', '+', '-', '&', '%']
    ref = {'>': ('::process', '::process'), '<': ('::process', '::process'), '=': ('::process', '::process'),
     '@': ('::process', '::agent'), '|': ('::agent', '::agent'), '~': ('::agent', '::agent'),
     '+': ('::process', '::agent'), '-': ('::process', '::agent'), '&': ('::resource', '::process'),
     '%': ('::resource', '::agent')}
    assert scribl.valid_relationships == ref
    ref = {'RELATES': ('ARTICLE', 'CATEGORY'), 'DESCRIBES': ('ARTICLE', 'PROCESS'), 'MENTIONS': ('ARTICLE', 'AGENT'),
           'REFERENCES': ('ARTICLE', 'RESOURCE'), 'ACTIVATES': ('PROCESS', 'PROCESS'), 'INHIBITS': ('PROCESS', 'PROCESS'),
           'REGULATES': ('PROCESS', 'PROCESS'), 'INVOLVES': ('PROCESS', 'AGENT'), 'BINDS': ('AGENT', 'AGENT'),
           'MODIFIES': ('AGENT', 'AGENT'), 'GENERATES': ('PROCESS', 'AGENT'), 'REMOVES': ('PROCESS', 'AGENT'),
           'RESOURCE_DESCRIBES': ('RESOURCE', 'PROCESS'), 'RESOURCE_MENTIONS': ('RESOURCE', 'AGENT')}
    assert scribl.cypher_relationships == ref

def test_default_keymap():
    print('Testing default_keymap ...')
    ref = {'zotero_keys': ['Key', 'Title', 'Url', 'Publication Year', 'Author', 'Publication Title', 'Journal Abbreviation', 'Abstract Note'],
           'cypher_keys': ['zotero_key', 'title', 'url', 'year', 'author', 'journal_title', 'journal_abreviation', 'abstract']}
    assert scribl.default_keymap == ref
