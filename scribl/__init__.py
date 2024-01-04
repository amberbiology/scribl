__author__ = 'Amber Biology'

__pkgname__ = 'scribl'
__version_scheme__ = 'post-release'

try:
    import importlib.metadata as metadata_lib # look for built-in
except (ModuleNotFoundError, ImportError):
    import importlib_metadata as metadata_lib  # otherwise need the backport

try:
    __version__ = metadata_lib.version(__pkgname__) # use the installed version first
except metadata_lib.PackageNotFoundError:
    from setuptools_scm import get_version
    __version__ = get_version(version_scheme=__version_scheme__, root="../..", relative_to=__file__)  # next try the version in repo


ZOTERO_EXPORT = 0
DB_EXPORT = 1

prefix = ':'
statement_prefix = '{}{}'.format(prefix, prefix)
field_prefix = prefix
tag_delimiter = ';'
zotero_tag_max = 255
zotero_scribl_field = 'Manual Tags'
edit_diff_item_prefix = '---'

def generate_statement(item):
    return '{}{}'.format(statement_prefix, item)

def generate_field(item):
    return '{}{}'.format(field_prefix, item)

statement_types = ['category', 'agent', 'process', 'resource']
statements = []
for item in statement_types:
    statements.append(generate_statement(item))

agent_types = ['protein', 'gene', 'dna', 'rna', 'mrna', 'complex', 'organelle', 'biomarker']
agents = []
for item in agent_types:
    agents.append(generate_field(item))

field_types = ['url', 'tag', 'syn', 'txt']
fields = {}
for item in field_types:
    fields[item] = generate_field(item)

relationship_types = {'>':'ACTIVATES', '<':'INHIBITS', '=':'REGULATES','@':'INVOLVES', '|':'BINDS',
                      '~':'MODIFIES', '+':'GENERATES', '-':'REMOVES', '&':'RESOURCE_DESCRIBES', '%':'RESOURCE_MENTIONS'}
relationships = []
for item in relationship_types:
    relationships.append(item)

valid_relationships = {}
valid_relationships['>'] = (generate_statement('process'), generate_statement('process'))
valid_relationships['<'] = (generate_statement('process'), generate_statement('process'))
valid_relationships['='] = (generate_statement('process'), generate_statement('process'))
valid_relationships['@'] = (generate_statement('process'), generate_statement('agent'))
valid_relationships['|'] = (generate_statement('agent'), generate_statement('agent'))
valid_relationships['~'] = (generate_statement('agent'), generate_statement('agent'))
valid_relationships['+'] = (generate_statement('process'), generate_statement('agent'))
valid_relationships['-'] = (generate_statement('process'), generate_statement('agent'))
valid_relationships['&'] = (generate_statement('resource'), generate_statement('process'))
valid_relationships['%'] = (generate_statement('resource'), generate_statement('agent'))

cypher_relationships = {}
cypher_relationships['RELATES'] = ('ARTICLE','CATEGORY')
cypher_relationships['DESCRIBES'] = ('ARTICLE','PROCESS')
cypher_relationships['MENTIONS'] = ('ARTICLE','AGENT')
cypher_relationships['REFERENCES'] = ('ARTICLE','RESOURCE')
cypher_relationships['ACTIVATES'] = ('PROCESS','PROCESS')
cypher_relationships['INHIBITS'] = ('PROCESS','PROCESS')
cypher_relationships['REGULATES'] = ('PROCESS','PROCESS')
cypher_relationships['INVOLVES'] = ('PROCESS','AGENT')
cypher_relationships['BINDS'] = ('AGENT','AGENT')
cypher_relationships['MODIFIES'] = ('AGENT','AGENT')
cypher_relationships['GENERATES'] = ('PROCESS','AGENT')
cypher_relationships['REMOVES'] = ('PROCESS','AGENT')
cypher_relationships['RESOURCE_DESCRIBES'] = ('RESOURCE','PROCESS')
cypher_relationships['RESOURCE_MENTIONS'] = ('RESOURCE','AGENT')

default_keymap = {}
default_keymap['zotero_keys'] = ['Key', 'Title', 'Url', 'Publication Year', 'Author', 'Publication Title', 'Journal Abbreviation', 'Abstract Note']
default_keymap['cypher_keys'] = ['zotero_key', 'title', 'url', 'year', 'author', 'journal_title', 'journal_abreviation', 'abstract']
