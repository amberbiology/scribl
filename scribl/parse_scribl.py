__author__ = 'Amber Biology'

import scribl
from pyparsing import *

class ScriblParser:

    header = oneOf(scribl.statements).setResultsName('header')
    labels = oneOf(scribl.agents).setResultsName('labels', listAllMatches=True)
    reserved_words = oneOf(scribl.relationships)
    name_word = ~reserved_words + Word(alphanums, printables, excludeChars=scribl.prefix+',')
    name= Group(OneOrMore(name_word))
    relationship_header = oneOf(scribl.relationships)
    relationships = (relationship_header + name).setResultsName('relationships', listAllMatches=True)
    url_header = Literal(scribl.fields['url'])
    url_start = Literal('http://') | Literal('https://')
    url_address = Combine(url_start + Word(printables)).setResultsName('url', listAllMatches=True)
    url = (url_header + url_address)
    tags_header = Literal(scribl.fields['tag'])
    tag_list = delimitedList(name).setResultsName('tags', listAllMatches=True)
    tags = tags_header + tag_list
    notes_header = Literal(scribl.fields['txt'])
    notes = notes_header + name.setResultsName('notes', listAllMatches=True)
    synonyms_header = Literal(scribl.fields['syn'])
    synonyms = synonyms_header + delimitedList(name).setResultsName('synonyms', listAllMatches=True)
    #synonyms = synonyms_header + name.setResultsName('synonyms', listAllMatches=True)
    optional_items = labels | url | relationships | notes | synonyms | tags
    statement = header + name.setResultsName('name') + ZeroOrMore(optional_items)

    # initiate parser (optionally with scribl_code text block)
    def __init__(self, scribl_text=None):
        self.reset()
        if not scribl_text == None:
            self.parse(scribl_text)

    def reset(self):
        self.data = {}
        for field in scribl.statements:
            self.data[field] = {}
        self.data['errors'] = []
        self.data['warnings'] = []

    def parse(self, scribl_text, split_text=None):
        if not split_text == None:
            scribl_text = scribl_text.split(split_text)
        for nline in range(0, len(scribl_text)):
            line = scribl_text[nline].strip()
            if len(line) == 0:
                continue
            # warn if statement is longer than max. allowed for Zotero syncing
            if len(line) > scribl.zotero_tag_max:
                warning = 'Line: {:d} Statement length exceeds max. for Zotero syncing: {}'.format(nline, line)
                self.data['warnings'].append(warning)
            try:
                parse_data = ScriblParser.statement.parseString(line)
            except:
                error = 'Line: {:d} Unable to parse statment [{}]'.format(nline, line)
                self.data['errors'].append(error)
                continue
            item_type = parse_data.header
            item_name = ' '.join(parse_data.name)
            # parse urls
            item_urls = parse_data.url
            #parse labels
            item_labels = parse_data.labels
            # parse tags
            item_tags = []
            for field in parse_data.tags:
                for item in field:
                    item_tags.append(' '.join(item))
            # parse synonyms
            item_synonyms = []
            for field in parse_data.synonyms:
                for item in field:
                    item_synonyms.append(' '.join(item))
            # parse notes
            item_notes = []
            for note_field in parse_data.notes:
                note = ' '.join(note_field)
                item_notes.append(note)
            # parse relationships
            item_relationships = []
            for field in parse_data.relationships:
                rtype = field[0]
                partner = ' '.join(field[1])
                relation = (rtype, partner)
                item_relationships.append(relation)
            if not item_name in self.data[item_type]:
                self.data[item_type][item_name] = {}
                for field in ['urls', 'labels', 'tags', 'notes', 'relationships', 'synonyms']:
                    self.data[item_type][item_name][field] = []
            # process general fields
            for url in item_urls:
                if not url in self.data[item_type][item_name]['urls']:
                    self.data[item_type][item_name]['urls'].append(url)
            for tag in item_tags:
                if not tag in self.data[item_type][item_name]['tags']:
                    self.data[item_type][item_name]['tags'].append(tag)
            for note in item_notes:
                if not note in self.data[item_type][item_name]['notes']:
                    self.data[item_type][item_name]['notes'].append(note)
            # process agent
            if not item_type == '::agent':
                for item_field in [item_labels, item_synonyms]:
                    if len(item_field) > 0:
                        warning = 'Line: {:d} Agent fields ignored in non-agent statement [{}]'.format(nline, line)
                        self.data['warnings'].append(warning)
            else:
                for synonym in item_synonyms:
                    if not synonym in self.data[item_type][item_name]['synonyms']:
                        self.data[item_type][item_name]['synonyms'].append(synonym)
                for label in item_labels:
                    if not label in self.data[item_type][item_name]['labels']:
                        self.data[item_type][item_name]['labels'].append(label)
            # process relationships
            for relation in item_relationships:
                rtype = relation[0]
                if not scribl.valid_relationships[rtype][0] == item_type:
                    error = 'Line: {:d} Invalid relationship "{} {}" for "{}" ignored [{}]'.format(nline, rtype, relation[1], item_type, line)
                    self.data['errors'].append(error)
                else:
                    if not relation in self.data[item_type][item_name]['relationships']:
                        self.data[item_type][item_name]['relationships'].append(relation)
        self.validate_relationships()
        return

    def validate_relationships(self):
        exclude_types = ['errors', 'warnings']
        for item_type in self.data:
            if item_type in exclude_types:
                continue
            for item_name in self.data[item_type]:
                for relation in self.data[item_type][item_name]['relationships']:
                    rtype = relation[0]
                    partner = relation[1]
                    partner_type= scribl.valid_relationships[rtype][1]
                    if not partner in self.data[partner_type]:
                        error = 'Unrecognized entity "{}" in relationship: {} {} ... {} {}'.format(partner, item_type, item_name, rtype, partner)
                        self.data['errors'].append(error)
                        self.data[item_type][item_name]['relationships'].remove(relation)
        return

    def get(self, item_type, item_name):
        try:
            return self.data[item_type][item_name]
        except:
            return None

    def catalog(self, item_type):
        try:
            return list(self.data[item_type].keys())
        except:
            return []

    def parse_summary(self):
        result = {}
        for item_type in self.data:
            result[item_type] = len(self.data[item_type])
        return result
