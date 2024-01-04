__author__ = 'Amber Biology'

from xml.sax.saxutils import escape
import scribl, copy, pickle
from scribl.process_zotero import ZoteroCSV
from scribl.parse_scribl import ScriblParser

class GraphDB:

    def __init__(self, db_data_filepath, export_type=scribl.ZOTERO_EXPORT, scribl_field=scribl.zotero_scribl_field, zotero_keys=None, cypher_keys=None):
        if zotero_keys == None:
            zotero_keys = scribl.default_keymap['zotero_keys']
        if cypher_keys == None:
            cypher_keys = scribl.default_keymap['cypher_keys']
        if export_type == scribl.DB_EXPORT:
            self.db = self.load_db(db_data_filepath)
            return
        self.db = {}
        self.db['article'] = {}
        for field in scribl.statement_types:
            self.db[field] = {}
        self.db['warnings'] = {}
        self.db['errors'] = {}
        self.db['relationships'] = {'RELATES':[], 'REFERENCES':[], 'DESCRIBES':[], 'MENTIONS':[], }
        for relationship_type in scribl.relationship_types:
            relationship_label = scribl.relationship_types[relationship_type]
            self.db['relationships'][relationship_label] = []
        resource_key = scribl.generate_statement('resource')
        category_key = scribl.generate_statement('category')
        process_key = scribl.generate_statement('process')
        agent_key = scribl.generate_statement('agent')
        # process a Zotero DB csv export
        if export_type == scribl.ZOTERO_EXPORT:
            self.zotero_db = ZoteroCSV(db_data_filepath)
            self.zotero_db.map_keys(zotero_keys, cypher_keys)
        # process scribl_code tags in exported articles
        parser = ScriblParser()
        for article_key in self.zotero_db.data:
            parser.reset()
            scribl_text = self.zotero_db.data[article_key][scribl_field]
            parser.parse(scribl_text, split_text=scribl.tag_delimiter)
            # capture article with mapped keys
            self.db['article'][article_key] = {}
            for cypher_key in self.zotero_db.keymap:
                zotero_key = self.zotero_db.keymap[cypher_key]
                self.db['article'][article_key][cypher_key] = self.zotero_db.data[article_key][zotero_key]
            # capture warnings and errors
            wekey = (article_key, self.db['article'][article_key]['title'][:50])
            if len(parser.data['warnings']) > 0:
                self.db['warnings'][wekey] = copy.copy(parser.data['warnings'])
            if len(parser.data['errors']) > 0:
                self.db['errors'][wekey] = copy.copy(parser.data['errors'])
            # capture categories and resources
            doing = {category_key:'RELATES', resource_key:'REFERENCES'}
            for item_type in doing:
                item_key = item_type[len(scribl.statement_prefix):]
                for item in parser.data[item_type]:
                    if not item in self.db[item_key]:
                        self.db[item_key][item] = {'urls':[], 'tags':[], 'notes':[]}
                    for field in ['urls', 'tags', 'notes']:
                        for field_item in parser.data[item_type][item][field]:
                            if not field_item in self.db[item_key][item][field]:
                                self.db[item_key][item][field].append(field_item)
                    # add article relationship
                    relationship_label = doing[item_type]
                    relation = (article_key, item)
                    if not relation in self.db['relationships'][relationship_label]:
                        self.db['relationships'][relationship_label].append(relation)
            # capture agents
            for agent in parser.data[agent_key]:
                if not agent in self.db['agent']:
                    self.db['agent'][agent] = {'urls':[], 'tags':[], 'notes':[], 'labels':[], 'synonyms':[agent]}
                for field in ['urls', 'tags', 'notes', 'labels', 'synonyms']:
                    for field_item in parser.data[agent_key][agent][field]:
                        if not field_item in self.db['agent'][agent][field]:
                            self.db['agent'][agent][field].append(field_item)
                relation = (article_key, agent)
                if not relation in self.db['relationships']['MENTIONS']:
                    self.db['relationships']['MENTIONS'].append(relation)
            # capture processes
            for process in parser.data[process_key]:
                if not process in self.db['process']:
                    self.db['process'][process] = {'urls':[], 'tags':[], 'notes':[]}
                for field in ['urls', 'tags', 'notes']:
                    for field_item in parser.data[process_key][process][field]:
                        if not field_item in self.db['process'][process][field]:
                            self.db['process'][process][field].append(field_item)
                relation = (article_key, process)
                if not relation in self.db['relationships']['DESCRIBES']:
                    self.db['relationships']['DESCRIBES'].append(relation)
            # capture defined relationships
            for item_type in [resource_key, agent_key, process_key]:
                for item in parser.data[item_type]:
                    for relationship in parser.data[item_type][item]['relationships']:
                        rtype = relationship[0]
                        relation_label = scribl.relationship_types[rtype]
                        partner1 = item
                        partner2 = relationship[1]
                        relation = (partner1, partner2)
                        if not relation in self.db['relationships'][relation_label]:
                            self.db['relationships'][relation_label].append(relation)
            # modifies implies binds so add binds relationship to all modifies relationships
            for relation in self.db['relationships']['MODIFIES']:
                bind_relation = (relation[0], relation[1])
                if not bind_relation in self.db['relationships']['BINDS']:
                    self.db['relationships']['BINDS'].append(bind_relation)
        return

    def catalog(self, item_type, relationship=False):
        if relationship:
            catalog = self.db['relationships'][item_type]
        else:
            catalog = list(self.db[item_type].keys())
        return sorted(catalog)

    def get(self, item_type, item_name):
        return self.db[item_type][item_name]

    def show_relationships(self, item_type, item_name):
        try:
            exists = self.db[item_type][item_name]
        except:
            return {}
        result = {'search':(item_type, item_name)}
        for rtype in self.db['relationships']:
            result[rtype] = []
            for relation in self.db['relationships'][rtype]:
                if item_name in relation:
                    result[rtype].append(relation)
        return result

    def save_db(self, filepath):
        with open(filepath, 'wb') as dbfile:
            pickle.dump(self.db, dbfile)
        return

    def load_db(self, filepath):
        with open(filepath, 'rb') as dbfile:
            loaded_db = pickle.load(dbfile)
        return loaded_db

    def generate_db_diff(self, other):
        db_diff = {}
        for item_type in self.db:
            if item_type in ['relationships', 'warnings', 'errors']:
                continue
            db_diff[item_type] = {}
            for item in self.db[item_type]:
                if not item in other.db[item_type]:
                    db_diff[item_type][item] = copy.copy(self.db[item_type][item])
                    continue
                else:
                    diff_found = False
                    current_item = copy.copy(self.db[item_type][item])
                    for field in self.db[item_type][item]:
                        current_item[field] = []
                        for value in self.db[item_type][item][field]:
                            if not value in other.db[item_type][item][field]:
                                diff_found = True
                                current_item[field].append(value)
                    if diff_found:
                        edit_item = '{}{}'.format(scribl.edit_diff_item_prefix, item)
                        db_diff[item_type][edit_item] = current_item
            # compile relationship diffs
            db_diff['relationships'] = {}
            for rtype in self.db['relationships']:
                db_diff['relationships'][rtype] = []
                for relation in self.db['relationships'][rtype]:
                    if not relation in other.db['relationships'][rtype]:
                        db_diff['relationships'][rtype].append(relation)
        return db_diff

    def generate_cypher(self, diff_db=None):
        if diff_db == None:
            use_db = self.db
        else:
            use_db = diff_db
        cypher = []
        # export articles
        for article_key in use_db['article']:
            edit = self.edit_only(article_key)
            name = edit['name']
            cypher_list = ["""MERGE (:ARTICLE {{key:"{}", """.format(name)]
            for field in use_db['article'][article_key]:
                value = use_db['article'][article_key][field]
                cypher_list.append("""{}:"{}" """.format(field, value))
                cypher_list.append(', ')
            cypher_list[-1] = '});'
            cypher_text = ''.join(cypher_list)
            cypher.append(cypher_text)
            #print(cypher_text)
        # export category
        for category in use_db['category']:
            edit = self.edit_only(category)
            name = edit['name']
            if edit['only']:
                cypher_list = ["""MATCH (c:CATEGORY {{name:"{}"}})""".format(name)]
            else:
                cypher_list = ["""MERGE (c:CATEGORY {{name:"{}", urls:[], tags:[], notes:[] }})""".format(name)]
            for field in use_db['category'][category]:
                for item in use_db['category'][category][field]:
                    cypher_list.append("""set r.{} = (r.{} + "{}")""".format(field, field, item))
            cypher_list[-1] = cypher_list[-1] + ';'
            cypher_text = '\n'.join(cypher_list)
            cypher.append(cypher_text)
            #print(cypher_text)
        # export resources
        for resource in use_db['resource']:
            edit = self.edit_only(resource)
            name = edit['name']
            if edit['only']:
                cypher_list = ["""MATCH (r:RESOURCE {{name:"{}"}})""".format(name)]
            else:
                cypher_list = ["""MERGE (r:RESOURCE {{name:"{}", urls:[], tags:[], notes:[] }})""".format(name)]
            for field in use_db['resource'][resource]:
                for item in use_db['resource'][resource][field]:
                    cypher_list.append("""set r.{} = (r.{} + "{}")""".format(field, field, item))
            cypher_list[-1] = cypher_list[-1] + ';'
            cypher_text = '\n'.join(cypher_list)
            cypher.append(cypher_text)
            #print(cypher_text)
        # export processes
        for process in use_db['process']:
            edit = self.edit_only(process)
            name = edit['name']
            if edit['only']:
                cypher_list = ["""MATCH (r:PROCESS {{name:"{}"}})""".format(name)]
            else:
                cypher_list = ["""MERGE (r:PROCESS {{name:"{}", urls:[], tags:[], notes:[] }})""".format(name)]
            for field in use_db['process'][process]:
                for item in use_db['process'][process][field]:
                    cypher_list.append("""set r.{} = (r.{} + "{}")""".format(field, field, item))
            cypher_list[-1] = cypher_list[-1] + ';'
            cypher_text = '\n'.join(cypher_list)
            cypher.append(cypher_text)
            #print(cypher_text)
        # export agents
        for agent in use_db['agent']:
            edit = self.edit_only(agent)
            name = edit['name']
            if edit['only']:
                cypher_list = ["""MATCH (a:AGENT {{name:"{}"}})""".format(name)]
            else:
                cypher_list = ["""MERGE (a:AGENT {{name:"{}", urls:[], tags:[], notes:[], labels:[], synonyms:[] }})""".format(name)]
            for field in use_db['agent'][agent]:
                for item in use_db['agent'][agent][field]:
                    cypher_list.append("""set a.{} = (a.{} + "{}")""".format(field, field, item))
            cypher_list[-1] = cypher_list[-1] + ';'
            cypher_text = '\n'.join(cypher_list)
            cypher.append(cypher_text)
            #print(cypher_text)
        # export relationships
        for rtype in use_db['relationships']:
            partner1_type = scribl.cypher_relationships[rtype][0]
            partner2_type = scribl.cypher_relationships[rtype][1]
            if rtype in ['RELATES', 'DESCRIBES', 'REFERENCES', 'MENTIONS']:
                match_field = 'key'
            else:
                match_field = 'name'
            for relation in use_db['relationships'][rtype]:
                cypher_list = ["""MATCH (p1:{} {{{}:"{}"}}), (p2:{} {{name:"{}"}})""".format(partner1_type, match_field, relation[0], partner2_type, relation[1])]
                if rtype[:9] == 'RESOURCE_':
                    cypher_list.append("""MERGE (p1)-[:{}]->(p2);""".format(rtype[9:]))
                else:
                    cypher_list.append("""MERGE (p1)-[:{}]->(p2);""".format(rtype))
                cypher_text = '\n'.join(cypher_list)
                cypher.append(cypher_text)
                #print(cypher_text)
        # clean up any redundant 'binds' relationships (but if diff cypher contains nothing, skip it)
        if len(cypher) > 0:
            cypher_text = ("""MATCH (a1:AGENT)-[r1:BINDS]->(a2:AGENT) WITH a1,a2 MATCH(a1:AGENT)<-[r2:BINDS]-(a2:AGENT) DELETE r2;""")
            cypher.append(cypher_text)
        return cypher

    def edit_only(self, item_name):
        if item_name[:3] == scribl.edit_diff_item_prefix:
            return {'only':True, 'name':item_name[3:]}
        else:
            return {'only':False, 'name':item_name}

    def export_cypher_text(self, cypher):
        return '\n'.join(cypher)

    def check_synonyms(self):
        agents = []
        synonyms = {}
        result = {'synonym appears in different agents':{}, 'synonym appears as an agent':[]}
        for agent in self.db['agent']:
            agents.append(agent)
            for synonym in self.db['agent'][agent]['synonyms'][1:]:
                if not synonym in synonyms:
                    synonyms[synonym] = []
                synonyms[synonym].append(agent)
        for synonym in synonyms:
            if len(synonyms[synonym]) > 1:
                result['synonym appears in different agents'][synonym] = copy.copy(synonyms[synonym])
            if synonym in agents:
                result['synonym appears as an agent'].append(synonym)
        return result

    def check_agent_labels(self):
        no_label = []
        for agent in self.db['agent']:
            if len(self.db['agent'][agent]['labels']) == 0:
                no_label.append(agent)
        return no_label

    def _generate_xml_node(self, node_db, node_name=""):

        xmlnode_list = []

        for node in node_db:
            edit = self.edit_only(node)
            name = edit['name']
            graphml_list = ["""<node id="{}">""".format(name)]
            graphml_list.append("<desc>{}</desc>".format(node_name))
            graphml_list.append("""<data key="desc">{}</data>""".format(node_name))
            for field in node_db[node]:
                for item in node_db[node][field]:
                    graphml_list.append("""<data key="{}">{}</data>""".format(field, item))
            graphml_list.append("</node>")
            graphml_text = '\n'.join(graphml_list)
            xmlnode_list.append(graphml_text)

        return '\n'.join(xmlnode_list)

    def generate_graphml(self, diff_db=None):
        use_db = self.db
        graphml = []
        # export articles
        graphml.append("""<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd">""")

        # NODE TYPE
        graphml.append("""<key id="desc" for="node" attr.name="desc" attr.type="string"/>""")

        # ARTICLE, RESOURCE, AGENT, PROCESS

        # FIXME: not sure why plural 'urls' and 'notes' are not defined in the default_keymap
        scribl_attributes = ['urls', 'labels', 'tags', 'notes', 'synonyms']
        scribl_attributes += scribl.default_keymap['cypher_keys'] # cypher_keys include the Zotero keys

        for key in scribl_attributes:
            graphml.append("""<key id="{}" for="node" attr.name="{}" attr.type="string"/>""".format(key, key))

        # RELATIONSHIP
        graphml.append("""<key id="relationship" for="edge" attr.name="label" attr.type="string"/>""")


        graphml.append("<graph id='G' edgedefault='directed'>")
        for article_key in use_db['article']:
            edit = self.edit_only(article_key)
            name = edit['name']
            graphml_list = ["<node id='{}'>\n".format(name)]
            graphml_list.append("<desc>ARTICLE</desc>\n")
            ## NetworkX doesn't support '<desc>' GraphML element well, so repeat it here
            graphml_list.append("""<data key="desc">ARTICLE</data>\n""")
            for field in use_db['article'][article_key]:
                value = use_db['article'][article_key][field]
                # make sure to escape any inline XML characters, e.g. '&', '>' etc.
                value = escape(value)
                graphml_list.append("""<data key="{}">{}</data>\n""".format(field, value))
            graphml_list.append("</node>")
            graphml_text = ''.join(graphml_list)
            graphml.append(graphml_text)

        # node generation the same for all remaining nodes

        category_xml = self._generate_xml_node(use_db['category'], node_name="CATEGORY")
        graphml.append(category_xml)

        resource_xml = self._generate_xml_node(use_db['resource'], node_name="RESOURCE")
        graphml.append(resource_xml)

        process_xml = self._generate_xml_node(use_db['process'], node_name="PROCESS")
        graphml.append(process_xml)

        agent_xml = self._generate_xml_node(use_db['agent'], node_name="AGENT")
        graphml.append(agent_xml)

        for rtype in use_db['relationships']:
            partner1_type = scribl.cypher_relationships[rtype][0]
            partner2_type = scribl.cypher_relationships[rtype][1]
            if rtype in ['RELATES', 'DESCRIBES', 'REFERENCES', 'MENTIONS']:
                match_field = 'key'
            else:
                match_field = 'name'
            for relation in use_db['relationships'][rtype]:
                graphml_list = ["""<edge id="{}-{}-{}-{}" source="{}" target="{}">""".format(partner1_type, relation[0], partner2_type, relation[1],
                                                                                             relation[0],
                                                                                             relation[1])]
                graphml_list.append("""<data key="relationship">{}</data>""".format(rtype))
                graphml_list.append("</edge>")
                graphml_text = '\n'.join(graphml_list)
                graphml.append(graphml_text)

        graphml.append("</graph>")
        graphml.append("</graphml>")
        return graphml

    def export_graphml_text(self, graphml):
        return '\n'.join(graphml)
