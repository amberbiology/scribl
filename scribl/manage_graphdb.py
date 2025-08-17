from __future__ import annotations

__author__ = "Amber Biology"

import datetime
import os
import shutil
import tempfile
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # must come before pyplot import

import matplotlib.pyplot as plt
import networkx as nx
from dateutil import parser as dateparser

import scribl
from scribl.process_graphdb_data import GraphDB
from scribl.process_zotero import zotero_library_to_csv


# utility function to generate timestamps
def generate_timestamp(text_format=False):
    now = datetime.datetime.now()
    if text_format:
        return now.strftime("%H:%M:%S %m-%d-%Y")
    return now.strftime("%Y_%m_%d_%H%M%S")


class GraphDBInstance:
    def __init__(self, db_folder_path, overwrite=False, verbose=False):
        self.zotero_keys = scribl.default_keymap["zotero_keys"]
        self.cypher_keys = scribl.default_keymap["cypher_keys"]
        self.db_folder_path = Path(db_folder_path)
        # self.config_folder = os.path.join(self.db_folder_path, "config")
        self.config_folder = self.db_folder_path / "config"
        self.db_snapshots_folder = self.db_folder_path / "db_snapshots"
        self.zotero_csv_exports_folder = self.db_folder_path / "zotero_csv_exports"

        self.db_backup_folder = self.db_folder_path / "backup"
        self.graphdb = None

        create_new = False

        if Path.exists(self.db_folder_path):
            # first check for presence of 'metadata.txt' file see if this is an actual database
            if Path.exists(self.db_folder_path / "config" / "metadata.txt"):
                if overwrite:
                    print(
                        "Overwrite enabled - removing current version of graph DB in",
                        self.db_folder_path,
                    )
                    shutil.rmtree(self.db_folder_path)
                    create_new = True
            else:  # path exists but does not contain a scribl database
                raise FileExistsError(
                    self.db_folder_path
                    + " directory exists but does not contain a valid existing scribl database"
                )
                return
        else:
            create_new = True

        if create_new:
            self.initialize_db()
            if verbose:
                print("Initializing graph DB at", self.db_folder_path)
                print("New graph DB created in ", self.db_folder_path)
        else:  # read from existing database
            if verbose:
                print(
                    f"DB exists {self.db_folder_path} and overwrite not enabled, read from existing db"
                )
            metadata_file = self.config_folder / "metadata.txt"
            if Path.exists(metadata_file):
                with open(metadata_file) as metafile:
                    metadata = metafile.readlines()
                    self.metadata = []
                    for line in metadata:
                        self.metadata.append(line.strip())

        return

    def initialize_db(self):
        Path.mkdir(self.db_folder_path)
        Path.mkdir(self.config_folder)
        Path.mkdir(self.db_snapshots_folder)
        Path.mkdir(self.zotero_csv_exports_folder)
        Path.mkdir(self.db_backup_folder)

    def set_metadata(self, db_name, curator, description, overwrite=False):
        metadata_file = self.config_folder / "metadata.txt"
        annotations_file = self.config_folder / "annotations.txt"
        if Path.exists(metadata_file) and not overwrite:
            return
        now = generate_timestamp(text_format=True)
        with open(metadata_file, "w") as metafile:
            metafile.write(f"Created: {now}\n")
            metafile.write(f"Curator: {curator}\n")
            metafile.write(f"DB Name: {db_name}\n")
            metafile.write(f"Summary: {description}\n")
        with open(annotations_file, "w") as annofile:
            annofile.write(f"Initialized: {now}\n")
        return

    def add_annotation(self, your_name, note_text):
        annotations_file = self.config_folder / "annotations.txt"
        now = generate_timestamp(text_format=True)
        note = f"{your_name}: {now}: {note_text}\n"
        with open(annotations_file, "a") as annofile:
            annofile.write(note)

    def generate_metadata_cypher(self):
        cypher = []
        cypher.append("MATCH(m:METADATA)-[r:METADATA]-(a:METADATA) delete r;")
        cypher.append("MATCH(m:METADATA) delete m;")
        metadata_file = self.config_folder / "metadata.txt"
        with open(metadata_file) as metafile:
            metadata = metafile.readlines()
        date = metadata[0][9:].strip()
        curator = metadata[1][9:].strip()
        title = metadata[2][9:].strip()
        summary = metadata[3][9:].strip()
        cypher.append(
            f"CREATE(:METADATA{{name:'metadata', initialized:'{date}', curator:'{curator}', title:'{title}', description:'{summary}'}});"
        )
        annotations_file = self.config_folder / "annotations.txt"
        with open(annotations_file) as annofile:
            notes = annofile.readlines()
        nc = notes[0].index(":")
        date = notes[0][nc:].strip()
        notes_list = []
        for note in notes[1:]:
            notes_list.append(note.strip())
        cypher.append(
            f"CREATE(:METADATA:ANNOTATIONS{{name:'annotations',initialized:'{date}', annotations:{notes_list!s}}});"
        )
        cypher.append(
            "MATCH(m:METADATA{name:'metadata'}), (a:METADATA{name:'annotations'})"
        )
        cypher.append("CREATE(m)-[:METADATA]->(a);")
        return "\n".join(cypher)

    def import_zotero_csv(self, import_filepath, overwrite=False, verbose=False):
        import_filepath = Path(import_filepath)
        if verbose:
            print("Importing Zotero CSV ", import_filepath)

        if Path.exists(import_filepath):
            now = generate_timestamp()
            new_import_filename = f"{now}_zotero_data.csv"

            if overwrite:
                # FIXME: this list is empty because the zotero export is removed upon overwriting the db
                exports = self.get_zotero_csv_exports()
                if exports:
                    new_import_filename = exports[-1]

            new_import_filepath = self.zotero_csv_exports_folder / new_import_filename
            shutil.copy(import_filepath, new_import_filepath)

            if verbose:
                print(f"{new_import_filepath} added to Zotero exports folder")

            return new_import_filepath
        if verbose:
            print("Cancelled! Zotero file not found at", import_filepath)
        return None

    def import_zotero_library(
        self,
        zotero_library_id,
        zotero_library_type,
        zotero_api_key=None,
        overwrite=False,
        verbose=False,
    ):
        # import directly from the zotero library, by querying the API
        # then generating an intermediate temporary CSV file for importing
        with tempfile.NamedTemporaryFile(
            suffix="zotero.csv", delete=False
        ) as zotero_csv:
            # populate the temporary files
            zotero_library_to_csv(
                zotero_library_id,
                zotero_library_type,
                zotero_api_key,
                zotero_csv_filename=zotero_csv.name,
                verbose=verbose,
            )

            # now call import_zotero_csv() on the temporary file
            self.import_zotero_csv(
                zotero_csv.name, overwrite=overwrite, verbose=verbose
            )
            # FIXME: close and then delete manually, needed on Windows as per
            # https://stackoverflow.com/a/43283261
            zotero_csv.close()
            os.remove(zotero_csv.name)

    def get_zotero_csv_exports(self):
        exports = []
        for file in os.listdir(self.zotero_csv_exports_folder):
            if file.endswith(".csv"):
                exports.append(file)
        return sorted(exports)

    def load_zotero_csv(
        self,
        zotero_csv_filename=None,
        zotero_keys=None,
        cypher_keys=None,
        verbose=False,
    ):
        if verbose:
            print("Loading csv data into graph DB ...")

        exports = self.get_zotero_csv_exports()
        # print(exports)
        if zotero_csv_filename is None:
            if len(exports) > 0:  # at least one Zotero CSV file has been imported
                zotero_csv_filename = exports[-1]
            else:
                print("Cancelled! No saved Zotero CSV files")
                return None
        elif not Path.exists(zotero_csv_filename):
            print("Cancelled! DB data not found at", zotero_csv_filename)
            return None
        self.current_zotero_csv = self.zotero_csv_exports_folder / zotero_csv_filename
        # load , process, and validate csv data
        self.graphdb = GraphDB(
            self.current_zotero_csv, zotero_keys=zotero_keys, cypher_keys=cypher_keys
        )

        # save summary
        summary = self.graphdb.db["warnings"], self.graphdb.db["errors"]

        if verbose:
            print(f"{self.current_zotero_csv.name} loaded into graph DB")
            nwarning = 0
            nerror = 0
            for article_key_pair in summary[0]:
                article_key = article_key_pair[0]
                print(
                    "Warnings: Article {} [{}...]".format(
                        article_key,
                        self.graphdb.db["article"][article_key]["title"][:60],
                    )
                )
                for warning in summary[0][article_key_pair]:
                    nwarning += 1
                    print(warning)
            for article_key_pair in summary[1]:
                article_key = article_key_pair[0]
                print(
                    "Errors: Article {} [{}...]".format(
                        article_key,
                        self.graphdb.db["article"][article_key]["title"][:60],
                    )
                )
                for error in summary[1][article_key_pair]:
                    nerror += 1
                    print(error)
            print(
                f"Summary: number of warnings: {nwarning}, number of errors: {nerror}"
            )

        return (summary[0], summary[1])

    def get_current_timestamp(self):
        # Extract the filename from the path
        filename = self.current_zotero_csv.name
        # Remove the '_zotero_data.csv' suffix to get the timestamp
        if filename.endswith("_zotero_data.csv"):
            return filename[: -len("_zotero_data.csv")]
        error_message = (
            "Filename does not follow the expected format '_zotero_data.csv'"
        )
        raise ValueError(error_message)

    def save_db_snapshot(self, verbose=False):
        if verbose:
            print("Saving graph DB snapshot ...")
        current_timestamp = self.get_current_timestamp()
        new_snapshot_filename = f"{current_timestamp}_db_snapshot.dat"
        new_snapshot_filepath = self.db_snapshots_folder / new_snapshot_filename
        self.graphdb.save_db(new_snapshot_filepath)

        if verbose:
            print(f"Graph DB snapshot saved to file: {new_snapshot_filepath}")
        return new_snapshot_filepath

    def get_db_snapshots(self):
        snapshots = []
        for file in os.listdir(self.db_snapshots_folder):
            if file.endswith(".dat"):
                snapshots.append(file)
        return sorted(snapshots)

    def load_db_snapshot(self, db_snapshot_filename=None, verbose=False):
        if verbose:
            print("Loading graph DB snapshot ...")

        if db_snapshot_filename is None:
            snapshots = self.get_db_snapshots()
            db_snapshot_filename = snapshots[-1]

        db_snapshot_path = self.db_snapshots_folder / db_snapshot_filename
        db_snapshot = self.graphdb.load_db(db_snapshot_path)

        if verbose:
            print(f"Graph DB snapshot loaded from file: {db_snapshot_path}")

        return db_snapshot

    def export_cypher_text(self, diff=None, verbose=False, filepath=None):
        cypher = self.graphdb.generate_cypher(diff_db=diff)
        cypher_text = self.graphdb.export_cypher_text(cypher)

        if filepath:
            with open(filepath, "w") as cypher_file:
                cypher_file.write(cypher_text)
        elif verbose:
            print("\nExported Cypher Text -----\n")
            print(cypher_text)

        return cypher_text

    def backup_db(self, verbose=False):
        if verbose:
            print("Backing up graph DB ...")
        self.export_cypher_text()
        current = self.get_current_timestamp()
        db_backup_filename = f"{current}_db_backup.txt"
        new_db_backup_filepath = self.db_backup_folder / db_backup_filename
        self.graphdb.save_db(new_db_backup_filepath)
        if verbose:
            print(f"Graph DB backup saved to file: {new_db_backup_filepath}")

        return new_db_backup_filepath

    def generate_db_diff(self, db_snapshot_filename=None, verbose=False):
        if db_snapshot_filename is None:
            snapshots = self.get_db_snapshots()
            db_snapshot_filename = self.db_snapshots_folder / snapshots[-1]
        other_db = GraphDB(db_snapshot_filename, export_type=scribl.DB_EXPORT)
        db_diff = self.graphdb.generate_db_diff(other_db)

        if verbose:
            print("\nExported DB Diff Cypher Text -----\n")
            print(db_diff)

        return db_diff

    def inspect_db(self, list_contents=None, verbose=False, contents_length=5):
        list_contents = list_contents or []
        result = {}
        show = {}
        for key in self.graphdb.db:
            if key in ["relationships"]:
                continue
            result[key] = len(self.graphdb.db[key])
            if key in list_contents:
                show[key] = []
                for item in self.graphdb.db[key]:
                    show[key].append(item)
        for header in ["relationships"]:
            result[header] = {}
            for key in self.graphdb.db[header]:
                result[header][key] = len(self.graphdb.db[header][key])
                if (header, key) in list_contents:
                    if header not in show:
                        show[header] = {}
                    show[header][key] = []
                    for item in self.graphdb.db[header][key]:
                        show[header][key].append(item)
        result["list_contents"] = show

        if verbose:
            level2 = ["relationships", "list_contents"]
            for key, value in result.items():
                if key in level2:
                    continue
                print(f"{key:20} {value:d}")
            for field in level2:
                print(f"---{field}:")
                for item in result[field]:
                    if field == "relationships":
                        print(f"{item:20} {result[field][item]:d}")
                    else:
                        for entity in result[field]:
                            nitem = 0
                            for name in result[field][entity]:
                                print(name, end=", ")
                                nitem += 1
                                if nitem == contents_length:
                                    print()
                                    nitem = 0

        return result

    def check_synonyms(self, verbose=False):
        syn_check = self.graphdb.check_synonyms()

        if verbose:
            check = "synonym appears in different agents"
            print(f"\n{check} ...")
            for synonym in syn_check[check]:
                print(f"synonym: {synonym}, agents: {syn_check[check][synonym]}")
            check = "synonym appears as an agent"
            print(f"\n{check} ...")
            for synonym in syn_check[check]:
                print(f"synonym: {synonym}")
        return syn_check

    def check_agent_labels(self, verbose=False):
        label_check = self.graphdb.check_agent_labels()

        if verbose:
            print("Agents with no labels:")
            for name in label_check:
                print(f"::agent {name}")

        return label_check

    def export_graphml_text(self, verbose=False, filepath=None):
        graphml = self.graphdb.generate_graphml()
        graphml_text = self.graphdb.export_graphml_text(graphml)

        if filepath:
            with open(filepath, "w") as graphml_file:
                graphml_file.write(graphml_text)
        elif verbose:
            print("\nExported GraphML XML -----\n")
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
            wrapped_label = "\n".join(key.split(" "))
            if d["desc"] == "ARTICLE":
                # convert labels to be Author-Date, i.e. "Einstein (1912)"
                new_node_labels[key] = (
                    d["author"].split(";")[0].split(",")[0]
                    + "\n("
                    + str(dateparser.parse(d["year"]).year)
                    + ")"
                )
                article_nodes.append(key)
            elif d["desc"] == "CATEGORY":
                # wrap lines at spaces
                new_node_labels[key] = wrapped_label
                category_nodes.append(key)
            elif d["desc"] == "RESOURCE":
                new_node_labels[key] = wrapped_label
                resource_nodes.append(key)
            elif d["desc"] == "AGENT":
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
        nx.draw_networkx_nodes(
            G, pos, nodelist=category_nodes, node_color="tab:olive", node_size=node_size
        )
        nx.draw_networkx_nodes(
            G, pos, nodelist=article_nodes, node_color="tab:red", node_size=node_size
        )
        nx.draw_networkx_nodes(
            G, pos, nodelist=resource_nodes, node_color="tab:green", node_size=node_size
        )
        nx.draw_networkx_nodes(
            G, pos, nodelist=agent_nodes, node_color="tab:blue", node_size=node_size
        )
        nx.draw_networkx_nodes(
            G, pos, nodelist=other_nodes, node_color="tab:purple", node_size=node_size
        )
        nx.draw_networkx_labels(G, pos, labels=new_node_labels, font_size=font_size)

        # now edges
        nx.draw_networkx_edges(G, pos, node_size=node_size, alpha=0.3, width=0.7)
        # can't use `get_edge_attributes()` for multiedge graphs
        # https://stackoverflow.com/questions/75810397/how-to-draw-edge-labels-when-there-are-multi-edges-in-networkx
        edge_labels = {(n1, n2): d["label"] for n1, n2, d in G.edges(data=True)}

        nx.draw_networkx_edge_labels(
            G, pos, edge_labels=edge_labels, font_size=font_size
        )

        plt.tight_layout()
        plt.axis("off")
        plt.savefig(filepath)
