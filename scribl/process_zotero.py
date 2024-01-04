__author__ = 'Amber Biology'

import re
import csv
import json
from io import StringIO
import pandas as pd
from pyzotero import zotero
import scribl

class ZoteroCSV:

    def __init__(self, filepath, newline='\n', delimiter=','):
        self.filepath = filepath
        self.newline = newline
        self.delimiter = delimiter
        self.data = {}
        self.keymap = None
        self.nrecords = 0
        self.errors = []
        with open(filepath, encoding='utf-8-sig') as csvfile:
            rows = []
            csvreader = csv.reader(csvfile, delimiter=self.delimiter)
            for row in csvreader:
                rows.append(row)
            self.keys = rows[0]
            for row in rows[1:]:
                this_key = row[0]
                self.data[this_key] = {'Key':this_key}
                self.nrecords += 0
                for n in range(1,len(row)):
                    if len(row[n]) > 0:
                        # remove any quotation marks
                        row[n] = row[n].replace('"', '')
                        self.data[this_key][self.keys[n]] = row[n]
                    else:
                        self.data[this_key][self.keys[n]] = 'none'
        self.map_keys(scribl.default_keymap['zotero_keys'], scribl.default_keymap['cypher_keys'])
        return

    def map_keys(self, zotero_keys, cypher_keys):
        # enforce essential index key mapping
        if not zotero_keys[0] == 'Key' and cypher_keys[0] == 'zotero_key':
            return
        if not zotero_keys[1] == 'Title' and cypher_keys[1] == 'title':
            return
        if not len(zotero_keys) == len(cypher_keys):
            return
        keymap = {}
        for n in range(0, len(zotero_keys)):
            if not zotero_keys[n] in self.keys:
                return
            else:
                keymap[cypher_keys[n]] = (zotero_keys[n])
        self.keymap = keymap
        return


def normalize_zotero_col_headers(x):
    # add spaces in between capital letters
    space_str = re.sub(r"([a-z0-9_])([A-Z])", r"\1 \2", x)
    # capitalize the first letter
    return space_str[0].upper() + space_str[1:]

def zotero_library_to_csv(library_id, library_type, api_key=None, zotero_csv_filename=None, verbose=False):

    zot = zotero.Zotero(library_id, library_type, api_key)
    items = zot.top() # top(limit=2)
    zotero_list = []

    for item in items:
        # flatten 'creators' into 'author' field
        item['data']['author'] = ';'.join([tag_item['name'] if 'name' in tag_item else tag_item['lastName']+', '+tag_item['firstName'] for tag_item in item['data']['creators']])
        # delete original 'creators'
        del item['data']['creators']

        # flatten tags
        item['data']['manualTags'] = '; '.join([tag_item['tag'] for tag_item in item['data']['tags']])
        # delete original 'tags'
        del item['data']['tags']

        # convert 'date' -> 'publicationYear'
        item['data']['publicationYear'] = item['data']['date']
        del item['data']['date']

        zotero_list.append(item['data'])

    json_zotero_output = json.dumps(zotero_list)
    zotero_df = pd.read_json(StringIO(json_zotero_output))
    zotero_df.columns = [normalize_zotero_col_headers(col) for col in zotero_df.columns]
    # if verbose:
    #    print(zotero_df.columns)

    # generate intermediate CSV file
    zotero_df.to_csv(zotero_csv_filename, encoding='utf-8', index=False)

    return
