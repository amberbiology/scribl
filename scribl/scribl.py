#!/usr/bin/env python

__author__ = 'Amber Biology'

# this is a very basic example of a command interface file for managing a scribl graph database
# it illustrates how to use the GraphDBInstance features in your own Python code, to create,
# update, and examine a scribl DB

import sys, os, shutil
from pathlib import Path
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from io import StringIO

# insert the path to the python scribl package, computed from the current file
DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(DIR, '..'))

debug = False

from scribl import __version__ as version
from scribl.manage_graphdb import GraphDBInstance

# define a main() function so we can use as an entry_point for an installable script
def main(argv=sys.argv):

    parser = ArgumentParser(add_help=True,
                            description="""Read from, or generate a new, scribl graph database based on a Zotero input (either a file, or direct from a library). Optionally output graph in Cypher text or GraphML""",
                            formatter_class=ArgumentDefaultsHelpFormatter)

    gp_db = parser.add_argument_group('scribl database settings')
    gp_db.add_argument("-g", "--graphdb", help="path to scribl graph database", default=False, required=True)
    gp_db.add_argument("-n", "--namedb", help="Name of your database", default="", required=False)
    gp_db.add_argument("-c", "--curator", help="Person/group who curated your database", default="", required=False)
    gp_db.add_argument("-d", "--description", help="Description of your database", default="", required=False)

    gp_zotero = parser.add_argument_group('Mutually exclusive Zotero inputs')
    gp_zotero_xor = gp_zotero.add_mutually_exclusive_group() # (required=True)
    gp_zotero_xor.add_argument("-z", "--zoterofile", help="path to Zotero input file", default=None)
    gp_zotero_xor.add_argument("--zotero-library", metavar="LIBRARY_ID:TYPE",
                       help="Zotero library access in the format 'LIBRARY_ID:TYPE', where LIBRARY_ID is an integer and TYPE is (either 'group' or 'user')",
                       default=None)
    gp_zotero_api = parser.add_argument_group('Zotero library options. Only valid to use if --zotero-library also supplied')
    gp_zotero_api.add_argument("--zotero-api-key", metavar="ZOTERO_API_KEY", help="If accessing a private Zotero library, use this API_KEY. ", default=None)

    gp_outputs = parser.add_argument_group('Optional generated outputs')
    gp_outputs.add_argument("--cyphertextfile", help="optional path to Cypher text output file", default=None, required=False)
    gp_outputs.add_argument("--graphmlfile", help="optional path to GraphML output file", default=None, required=False)
    gp_outputs.add_argument("--networkx-fig", help="optional path to NetworkX generated figure with visualization of GraphML, must have an extension supported by matplotlib", default=None, required=False)

    gp_checks = parser.add_argument_group('Optional checks')
    gp_checks.add_argument('--check-synonyms', help='run synonym check', default=False, required=False)
    gp_checks.add_argument('--check-agentlabels', help='run agent label check', default=False, required=False)

    parser.add_argument("-v", "--verbose", help="output verbosity", action="store_true", default=False)
    parser.add_argument("--overwrite", help="overwrite any existing database", action="store_true", default=False)
    parser.add_argument("-V", "--version", action="version", version="%(prog)s {version}\n".format(version=version))

    args = parser.parse_args(argv[1:])

    # path to your scribl graph db
    scribl_graphdb_path = args.graphdb

    # metadata details for your scribl database here
    db_name = args.namedb # 'Name of your database'
    db_curator = args.curator # 'Person/group who curated your database'
    db_description = args.description # 'Description of your database'

    # path to the input Zotero file
    default_zotero_export_path = args.zoterofile

    # path to optional output files
    cyphertext_filename = args.cyphertextfile
    graphml_filename = args.graphmlfile
    networkx_fig = args.networkx_fig

    check_synonyms = args.check_synonyms
    check_agentlabels = args.check_agentlabels

    overwrite = args.overwrite
    verbosity = args.verbose

    if args.zotero_library:
        try:
            zotero_library_id, zotero_library_type = args.zotero_library.split(':')
            zotero_library_id = int(zotero_library_id) # ensure first item is an integer
            zotero_api_key = args.zotero_api_key
        except ValueError:
            parser.error("--zotero-library must contain an integer and either `group` or `user` separated by a colon, e.g. '5251557:group'")
    elif args.zotero_api_key and not args.zotero_library:
        parser.error("--zotero-api-key only valid if --zotero-library also supplied")
    else:
        zotero_library_id, zotero_library_type, zotero_api_key = None, None, None

    # end argument parsing

    # initialize (or read from existing) graph DB
    try:
        gdb = GraphDBInstance(scribl_graphdb_path, overwrite=overwrite, verbose=verbosity)
    except FileExistsError:
        print('directory "%s" exists, but is not a valid existing scribl database, so cannot be either read or overwritten, aborting' % scribl_graphdb_path)
        return

    gdb.set_metadata(db_name, db_curator, db_description)

    if default_zotero_export_path:
        # import locally supplied CSV
        gdb.import_zotero_csv(default_zotero_export_path, overwrite=overwrite, verbose=verbosity)
    elif zotero_library_id and zotero_library_type:
        # get CSV generated from remote library:
        gdb.import_zotero_library(zotero_library_id, zotero_library_type, zotero_api_key, overwrite=overwrite, verbose=verbosity)
    else:
        if verbosity:
            print("no Zotero provided, reading from existing database")

    # load graph DB (and report any warnings and errors)
    summary = gdb.load_zotero_csv(verbose=verbosity)
    if summary:
        print('warnings:', summary[0], 'errors:', summary[1])
    else:
        print('no previously loaded data found')
        return

    if check_synonyms:
        # run synonym check
        gdb.check_synonyms(verbose=verbosity)

    if check_agentlabels:
        # run agent label check
        gdb.check_agent_labels(verbose=verbosity)

    # inspect graph DB
    gdb.inspect_db(list_contents=[], contents_length = 5)

    # save graph DB snapshot
    gdb.save_db_snapshot(verbose=verbosity)

    # load graph DB snapshot
    gdb.load_db_snapshot(verbose=verbosity)

    # export cypher text file
    if cyphertext_filename:
        gdb.export_cypher_text(verbose=verbosity, filepath=cyphertext_filename)

        # export diff cypher text
        gdb.generate_db_diff(verbose=verbosity)

    # backup graph DB
    gdb.backup_db(verbose=verbosity)

    if graphml_filename:
        # generate GraphML representation (incomplete)
        graphml_text = gdb.export_graphml_text(verbose=verbosity, filepath=graphml_filename)

    if networkx_fig:
        # generate visualization using NetworkX
        gdb.export_graphml_figure(verbose=verbosity, filepath=networkx_fig)

if __name__ == '__main__':

    main()
