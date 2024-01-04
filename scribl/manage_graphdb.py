__author__ = 'Amber Biology'

import os
import datetime
import shutil
import tempfile
import networkx as nx
import matplotlib.pyplot as plt
from dateutil import parser as dateparser

import scribl
from scribl.process_graphdb_data import GraphDB
from scribl.process_zotero import zotero_library_to_csv

# utility function to generate timestamps
def generate_timestamp(text_format=False):
    now = datetime.datetime.now()
    if text_format:
        return now.strftime('%H:%M:%S %m-%d-%Y')
    else:
        return now.strftime('%Y_%m_%d_%H%M%S')


class GraphDBInstance:

    def __init__(self, db_folder_path, overwrite=False, verbose=False):
        self.zotero_keys = scribl.default_keymap['zotero_keys']
        self.cypher_keys = scribl.default_keymap['cypher_keys']
        self.db_folder_path = db_folder_path
        self.config_folder = os.path.join(self.db_folder_path, 'config')
        self.db_snapshots_folder = os.path.join(self.db_folder_path, 'db_snapshots')
        self.zotero_csv_exports_folder = os.path.join(self.db_folder_path, 'zotero_csv_exports')
        self.db_backup_folder = os.path.join(self.db_folder_path, 'backup')
        self.graphdb = None

        create_new = False

        if os.path.exists(self.db_folder_path):
            # first check for presence of 'metadata.txt' file see if this is an actual database
            if os.path.exists(os.path.join(self.db_folder_path, 'config', 'metadata.txt')):
                if overwrite:
                    print('Overwrite enabled - removing current version of graph DB in', self.db_folder_path)
                    shutil.rmtree(self.db_folder_path)
                    create_new = True
            else:  # path exists but does not contain a scribl database
                raise FileExistsError(self.db_folder_path + ' directory exists but does not contain a valid existing scribl database')
                return
        else:
            create_new = True

        if create_new:
            self.initialize_db()
            if verbose:
                print('Initializing graph DB at', self.db_folder_path)
                print('New graph DB created in ', self.db_folder_path)
        else:  # read from existing database
            if verbose:
                print('DB exists in %s and overwite not enabled, read from existing db' % self.db_folder_path)
            metadata_file = os.path.join(self.config_folder, 'metadata.txt')
            if os.path.exists(metadata_file):
                with open(metadata_file, 'r') as metafile:
                    metadata = metafile.readlines()
                    self.metadata = []
                    for line in metadata:
                        self.metadata.append(line.strip())

        return

    def initialize_db(self):
        os.mkdir(self.db_folder_path)
        os.mkdir(self.config_folder)
        os.mkdir(self.db_snapshots_folder)
        os.mkdir(self.zotero_csv_exports_folder)
        os.mkdir(self.db_backup_folder)

    def set_metadata(self, db_name, curator, description, overwrite=False):
        metadata_file = os.path.join(self.config_folder, 'metadata.txt')
        annotations_file = os.path.join(self.config_folder, 'annotations.txt')
        if os.path.exists(metadata_file) and overwrite == False:
            return
        now = generate_timestamp(text_format=True)
        with open(metadata_file, 'w') as metafile:
            metafile.write('Created: {}\n'.format(now))
            metafile.write('Curator: {}\n'.format(curator))
            metafile.write('DB Name: {}\n'.format(db_name))
            metafile.write('Summary: {}\n'.format(description))
        with open(annotations_file, 'w') as annofile:
            annofile.write('Initialized: {}\n'.format(now))
        return

    def add_annotation(self, your_name, note_text):
        annotations_file = os.path.join(self.config_folder, 'annotations.txt')
        now = generate_timestamp(text_format=True)
        note = '{}: {}: {}\n'.format(your_name, now, note_text)
        with open(annotations_file, 'a') as annofile:
            annofile.write(note)
        return

    def generate_metadata_cypher(self):
        cypher = []
        cypher.append('MATCH(m:METADATA)-[r:METADATA]-(a:METADATA) delete r;')
        cypher.append('MATCH(m:METADATA) delete m;')
        metadata_file = os.path.join(self.config_folder, 'metadata.txt')
        with open(metadata_file, 'r') as metafile:
            metadata = metafile.readlines()
        date = metadata[0][9:].strip()
        curator = metadata[1][9:].strip()
        title = metadata[2][9:].strip()
        summary = metadata[3][9:].strip()
        cypher.append("CREATE(:METADATA{{name:'metadata', initialized:'{}', curator:'{}', title:'{}', description:'{}'}});".format(date, curator, title, summary))
        annotations_file = os.path.join(self.config_folder, 'annotations.txt')
        with open(annotations_file, 'r') as annofile:
            notes = annofile.readlines()
        nc = notes[0].index(':')
        date = notes[0][nc:].strip()
        notes_list = []
        for note in notes[1:]:
            notes_list.append(note.strip())
        cypher.append("CREATE(:METADATA:ANNOTATIONS{{name:'annotations',initialized:'{}', annotations:{}}});".format(date, str(notes_list)))
        cypher.append("MATCH(m:METADATA{name:'metadata'}), (a:METADATA{name:'annotations'})")
        cypher.append('CREATE(m)-[:METADATA]->(a);')
        return '\n'.join(cypher)

    def import_zotero_csv(self, import_filepath, overwrite=False, verbose=False):

        if verbose:
            print('Importing Zotero CSV ', import_filepath)

        if os.path.exists(import_filepath):
            now = generate_timestamp()
            new_import_filename = '{}_zotero_data.csv'.format(now)

            if overwrite:
                # FIXME: this list is empty because the zotero export is removed upon overwriting the db
                try:
                    new_import_filename = self.get_zotero_csv_exports()[-1]
                except IndexError:
                    # revert to the original new import path defined above
                    pass

            new_import_filepath = os.path.join(self.zotero_csv_exports_folder, new_import_filename)
            shutil.copy(import_filepath, new_import_filepath)

            if verbose:
                print('{} added to Zotero exports folder'.format(new_import_filepath))

            return new_import_filepath
        else:
            if verbose:
                print('Cancelled! Zotero file not found at', import_filepath)
            return None

    def import_zotero_library(self, zotero_library_id, zotero_library_type, zotero_api_key=None, overwrite=False, verbose=False):
        # import directly from the zotero library, by querying the API
        # then generating an intermediate temporary CSV file for importing
        with tempfile.NamedTemporaryFile(suffix="zotero.csv") as zotero_csv:
            # populate the temporary files
            zotero_library_to_csv(zotero_library_id, zotero_library_type, zotero_api_key, zotero_csv_filename=zotero_csv.name, verbose=verbose)

            # now call import_zotero_csv() on the temporary file
            self.import_zotero_csv(zotero_csv.name, overwrite=overwrite, verbose=verbose)

    def get_zotero_csv_exports(self):
        exports = []
        for file in (os.listdir(self.zotero_csv_exports_folder)):
            if file.endswith('.csv'):
                exports.append(file)
        return sorted(exports)

    def load_zotero_csv(self, zotero_csv_filename=None, zotero_keys=None, cypher_keys=None, verbose=False):

        if verbose:
            print('Loading csv data into graph DB ...')

        exports = self.get_zotero_csv_exports()
        #print(exports)
        if zotero_csv_filename == None:
            if len(exports) > 0:  # at least one Zotero CSV file has been imported
                zotero_csv_filename = exports[-1]
            else:
                print('Cancelled! No saved Zotero CSV files')
                return
        else:
            if not os.path.exists(zotero_csv_filename):
                print('Cancelled! DB data not found at', zotero_csv_filename)
                return
        self.current_zotero_csv = os.path.join(self.zotero_csv_exports_folder, zotero_csv_filename)
        # load , process, and validate csv data
        self.graphdb = GraphDB(self.current_zotero_csv, zotero_keys=zotero_keys, cypher_keys=cypher_keys)

        # save summary
        summary = self.graphdb.db['warnings'], self.graphdb.db['errors']

        if verbose:
            print('{} loaded into graph DB'.format(os.path.basename(self.current_zotero_csv)))
            nwarning = 0
            nerror = 0
            for article_key_pair in summary[0]:
                article_key = article_key_pair[0]
                print('Warnings: Article {} [{}...]'.format(article_key, self.graphdb.db['article'][article_key]['title'][:60]))
                for warning in summary[0][article_key_pair]:
                    nwarning += 1
                    print(warning)
            for article_key_pair in summary[1]:
                article_key = article_key_pair[0]
                print('Errors: Article {} [{}...]'.format(article_key, self.graphdb.db['article'][article_key]['title'][:60]))
                for error in summary[1][article_key_pair]:
                    nerror += 1
                    print(error)
            print('Summary: number of warnings: {}, number of errors: {}'.format(nwarning, nerror))

        return(summary[0], summary[1])

    def get_current_timestamp(self):
        # FIXME: this is extremely fragile code - it shouldn't hardcode lengths
        slash = self.current_zotero_csv.find(os.path.sep + 'zotero_csv_exports' + os.path.sep) + 20
        current_timestamp = self.current_zotero_csv[slash:slash+17]
        return current_timestamp

    def save_db_snapshot(self, use_default_db_keys=True, verbose=False):
        if verbose:
            print('Saving graph DB snapshot ...')
        current_timestamp = self.get_current_timestamp()
        new_snapshot_filename = '{}_db_snapshot.dat'.format(current_timestamp)
        new_snapshot_filepath = os.path.join(self.db_snapshots_folder, new_snapshot_filename)
        self.graphdb.save_db(new_snapshot_filepath)

        if verbose:
            print('Graph DB snapshot saved to file: {}'.format(new_snapshot_filepath))
        return new_snapshot_filepath

    def get_db_snapshots(self):
        snapshots = []
        for file in (os.listdir(self.db_snapshots_folder)):
            if file.endswith('.dat'):
                snapshots.append(file)
        return sorted(snapshots)

    def load_db_snapshot(self, db_snapshot_filename=None, verbose=False):
        if verbose:
            print('Loading graph DB snapshot ...')

        if db_snapshot_filename == None:
            snapshots = self.get_db_snapshots()
            db_snapshot_filename = snapshots[-1]

        db_snapshot_path = os.path.join(self.db_snapshots_folder, db_snapshot_filename)
        db_snapshot = self.graphdb.load_db(db_snapshot_path)

        if verbose:
            print('Graph DB snapshot loaded from file: {}'.format(db_snapshot_path))

        return db_snapshot

    def export_cypher_text(self, diff=None, verbose=False, filepath=None):
        cypher = self.graphdb.generate_cypher(diff_db=diff)
        cypher_text = self.graphdb.export_cypher_text(cypher)

        if filepath:
            with open(filepath, 'w') as cypher_file:
                cypher_file.write(cypher_text)
        else:
            if verbose:
                print('\nExported Cypher Text -----\n')
                print(cypher_text)

        return cypher_text

    def backup_db(self, verbose=False):
        if verbose:
            print('Backing up graph DB ...')
        cypher_text = self.export_cypher_text()
        current = self.get_current_timestamp()
        db_backup_filename = '{}_db_backup.txt'.format(current)
        new_db_backup_filepath = os.path.join(self.db_backup_folder, db_backup_filename)
        self.graphdb.save_db(new_db_backup_filepath)
        if verbose:
            print('Graph DB backup saved to file: {}'.format(new_db_backup_filepath))

        return new_db_backup_filepath

    def generate_db_diff(self, db_snapshot_filename=None, verbose=False):
        if db_snapshot_filename == None:
            snapshots = self.get_db_snapshots()
            db_snapshot_filename = os.path.join(self.db_snapshots_folder, snapshots[-1])
        other_db = GraphDB(db_snapshot_filename, export_type=scribl.DB_EXPORT)
        db_diff = self.graphdb.generate_db_diff(other_db)

        if verbose:
            print('\nExported DB Diff Cypher Text -----\n')
            print(db_diff)

        return db_diff

    def inspect_db(self, list_contents=[], verbose=False, contents_length=5):
        result = {}
        show = {}
        for key in self.graphdb.db:
            if key in ['relationships']:
                continue
            result[key] = len(self.graphdb.db[key])
            if key in list_contents:
                show[key] = []
                for item in self.graphdb.db[key]:
                    show[key].append(item)
        for header in ['relationships']:
            result[header] = {}
            for key in self.graphdb.db[header]:
                result[header][key] = len(self.graphdb.db[header][key])
                if (header, key) in list_contents:
                    if not header in show:
                        show[header] = {}
                    show[header][key] = []
                    for item in self.graphdb.db[header][key]:
                        show[header][key].append(item)
        result['list_contents'] = show

        if verbose:
            level2 = ['relationships', 'list_contents']
            for item in result:
                if item in level2:
                    continue
                print('{:20} {:d}'.format(item, result[item]))
            for field in level2:
                print('---{}:'.format(field))
                for item in result[field]:
                    if field == 'relationships':
                        print('{:20} {:d}'.format(item, result[field][item]))
                    else:
                        for entity in result[field]:
                            nitem = 0
                            for name in result[field][entity]:
                                print(name, end=', ')
                                nitem += 1
                                if nitem == contents_length:
                                    print()
                                    nitem = 0

        return result

    def check_synonyms(self, verbose=False):
        syn_check = self.graphdb.check_synonyms()

        if verbose:
            check = 'synonym appears in different agents'
            print('\n{} ...'.format(check))
            for synonym in syn_check[check]:
                print('synonym: {}, agents: {}'.format(synonym, syn_check[check][synonym]))
            check = 'synonym appears as an agent'
            print('\n{} ...'.format(check))
            for synonym in syn_check[check]:
                print('synonym: {}'.format(synonym))
        return syn_check

    def check_agent_labels(self, verbose=False):

        label_check = self.graphdb.check_agent_labels()

        if verbose:
            print('Agents with no labels:')
            for name in label_check:
                print('::agent {}'.format(name))

        return label_check

    def export_graphml_text(self, diff=None, verbose=False, filepath=None):
        graphml = self.graphdb.generate_graphml(diff_db=diff)
        graphml_text = self.graphdb.export_graphml_text(graphml)

        if filepath:
            with open(filepath, 'w') as graphml_file:
                graphml_file.write(graphml_text)
        else:
            if verbose:
                print('\nExported GraphML XML -----\n')
                print(graphml_text)

        return graphml_text

    def export_graphml_figure(self, verbose=False, filepath=None):
        # read GraphML into NetworkX for visualization
        graphml_text = self.export_graphml_text(verbose=verbose)

        G = nx.parse_graphml(graphml_text, force_multigraph=True)

        # get info needed for labels and node colours
        new_node_labels = {}
        article_nodes = []
        category_nodes = []
        resource_nodes = []
        agent_nodes = []
        other_nodes = []
        for node in G.nodes.items():
            key, d = node
            wrapped_label = '\n'.join(key.split(' '))
            if d['desc'] == 'ARTICLE':
                # convert labels to be Author-Date, i.e. "Einstein (1912)"
                new_node_labels[key] = d['author'].split(';')[0].split(',')[0] + '\n(' + str(dateparser.parse(d['year']).year) + ')'
                article_nodes.append(key)
            elif d['desc'] == 'CATEGORY':
                # wrap lines at spaces
                new_node_labels[key] = wrapped_label
                category_nodes.append(key)
            elif d['desc'] == "RESOURCE":
                new_node_labels[key] = wrapped_label
                resource_nodes.append(key)
            elif d['desc'] == "AGENT":
                new_node_labels[key] = wrapped_label
                agent_nodes.append(key)
            else:
                new_node_labels[key] = wrapped_label
                other_nodes.append(key)

        # generate and save figure as a matplotlib figure
        pos = nx.spring_layout(G, seed=3113794652)

        node_size = 2000
        font_size = 8

        # do nodes first, categories in olive and articles in red
        nx.draw_networkx_nodes(G, pos, nodelist=category_nodes,  node_color="tab:olive", node_size=node_size)
        nx.draw_networkx_nodes(G, pos, nodelist=article_nodes, node_color="tab:red", node_size=node_size)
        nx.draw_networkx_nodes(G, pos, nodelist=resource_nodes, node_color="tab:green", node_size=node_size)
        nx.draw_networkx_nodes(G, pos, nodelist=agent_nodes, node_color="tab:blue", node_size=node_size)
        nx.draw_networkx_nodes(G, pos, nodelist=other_nodes, node_color="tab:purple", node_size=node_size)
        nx.draw_networkx_labels(G, pos, labels=new_node_labels, font_size=font_size)

        # now edges
        nx.draw_networkx_edges(G, pos, node_size=node_size, alpha=0.3, width=0.7)
        # can't use `get_edge_attributes()` for multiedge graphs
        # https://stackoverflow.com/questions/75810397/how-to-draw-edge-labels-when-there-are-multi-edges-in-networkx
        edge_labels = dict([((n1, n2), d['label']) for n1, n2, d in G.edges(data=True)])
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=font_size)

        plt.tight_layout()
        plt.axis("off")
        plt.savefig(filepath)
