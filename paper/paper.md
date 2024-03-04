---
title: 'scribl: A system for the semantic capture of relationships in biological literature'
tags:
  - systems biology
  - network biology
  - literature mining
  - bioinformatics
  - computational biology
  - Zotero
authors:
  - name: Gordon D. Webster
    orcid: 0009-0009-2862-0467
    affiliation: "1, 2"
    equal-contrib: true
  - name: Alexander K. Lancaster
    orcid: 0000-0002-0002-9263
    affiliation: "1, 2, 3"
    equal-contrib: true
affiliations:
  - name: Amber Biology LLC, USA
    index: 1
  - name: Ronin Institute, USA
    index: 2
  - name: Institute for Globally Distributed Open Research and Education
    index: 3
date: 03 March 2024
bibliography: paper.bib
---

# Summary

When using literature databases, researchers in systems biology need
to go beyond simple keyword-based queries of biological agents (e.g.,
proteins, genes, compounds, receptor complexes) and processes (e.g,
autophagy, cell cycle) [@krallinger_linking_2008] that return a bare
list of papers, to extracting and visualize relationships documented
within those papers [@cary_pathway_2005; @suderman_tools_2007; @pavlopoulos_visualizing_2015].
Here we develop a system that supports the annotation of scientific
articles, that represent and visualize these relationships. This
system, `scribl`, consists of two parts: (1) a simple syntax that can
be used to curation of biological relationships within the text of
those articles, (2) a Python software API and pipeline that can
transform a [Zotero](https://www.zotero.org/) literature database,
with entries annotated with this syntax into database suitable
graph-based relationship queries.

# The `scribl` language

The language was designed for the curation of scientific articles to
document the relationships between the various biological agents and
processes that they describe. Examples of relationships for each of
the five basic entities for a single article are shown in
\autoref{fig:scribl-schema}.

![The scribl schema comprises a hierarchy of five basic entities: `article`, `category`, `resource`, `process`, and `agent`. Here we depict an example network of entities and possible relationships for a single `article`.\label{fig:scribl-schema}](scribl-schema.png){ width=80% }

`scribl` statements can be added as tags by a curator to each article
in a literature database to represent aspects of causal relationships
identified by the curator.

|   |
|:--|
| `::agent c9orf72 :gene :protein :url https://www.uniprot.org/uniprot/Q96LT7`     |
| `::agent gtp :tag nucleoside, purine, nucleoside triphosphate`                   |
| `::process exportin releases cargo into cytoplasm @ exportin-1`                  |
| `::process smcr8 mutation > ulk1 phosphorylation < autophagy = smcr8 expression` |
: Example scribl statements included in Zotero tags\label{scribl-examples}

\autoref{scribl-examples} shows two types of entities: (1) agents
(`::agent`): are actual biochemical entities (e.g. proteins) described
in the literature article in question, along with some metadata about
the agent, (2) processes (`::process`) which represent broad
mechanistic, or phenomenological biological processes (e.g.,
`autophagy`).

# The `scribl` Python package

The `scribl` Python package queries a [Zotero](https://zotero.org)
database where each literature record has been annotated using
declarative statements in the `scribl` syntax described in
\autoref{scribl-examples}. Currently, the literature source for
`scribl` input can be either a remote Zotero database, or a file
export from a local Zotero installation. Once the Zotero data has been
parsed, the resulting graph data structure can be then be exported for
use in a graph database platforms. `scribl` also supports the
incremental updating of the graph database as new Zotero entries come
in (\autoref{fig:scribl-workflow}).

![Two major workflows for the `scribl` software: creating a new graph database (left) and updating an existing one (right). Note that "Zotero csv export" could be replaced by a query to a remove Zotero library  \label{fig:scribl-workflow}](scribl-workflow.png)

`scribl` currently supports output in one of two formats:

1. [Cypher query language](https://opencypher.org/)
[@francis_cypher_2018] used by the graph database platform
[neo4j](https://neo4j.com). The output Cypher query can be used
directly to initialize a Neo4j database.  The Neo4j setup itself it
not done by `scribl`, but must be installed separately.

2.  [GraphML](http://graphml.graphdrawing.org/)
[@brandes_graphml_2002] format. This format can be read and used for
processing and visualization by packages such as Python's
[NetworkX](https://networkx.org/) [@hagberg_exploring_2008] (e.g,
\autoref{fig:graph-networkx}).

![Visualization of scribl database exported as GraphML via NetworkX.\label{fig:graph-networkx}](../graphdb-visual.png){ width=70% }

Once a graph database is created, it is possible to create searches
not possible with traditional keyword searching. For example, once the
scribl output is loaded into a Neo4j database, it is possible to write
Cypher queries of the kind: "Show me all of the agents that are
involved in the process `exportin` and the articles that describe
them".

# Statement of need

### Why `scribl`?

The `scribl` platform was developed to fill a need for a simple way to
enable global sharing and collaborative curation of biological
relationships embedded in literature records, and to rapidly translate
those relationships into queryable graph networks. The `scribl` syntax
was designed to be simple enough to learn, but rich enough to
represent important relationships relevant to molecular and systems
biology.

Zotero was also chosen as the initial backend, because it is simple to
install and run, and add tags to each literature record, and supports
the web-based curation features. `scribl` allows a researcher, or
group of researchers, to rapidly build and visualize important
relationships useful for understanding the celluar and systems biology
within a chosen subdomain. In fact our main use-case for `scribl` was
building a such a relationship database of neurodegenerative disease
pathways for the frontotemporal degeneration (FTD) community.

### What `scribl` is not

`scribl` is not primarily intended for the construction of formal
kinetic systems biology models such as the modeling languages
[Kappa](https://kappalanguage.org/) [@boutillier_kappa_2020] and
[SBML](https://sbml.org/) [@keating_sbml_2020]. However, these
networks could be considered a coarse-grained model of biological
systems that sit in between low resolution, keyword-based
representations; and high resolution, formal, kinetic
models. `scribl`-enabled networks may also help researchers identify
interactions or parameters that require measurement in order to build
those detailed models.

`scribl` is also not intended to be a replacement for biological graph
databases such as [Reactome](https://reactome.org)
[@gillespie_reactome_2022]. The Reactome database is actually based
upon the same Neo4j graph database engine supported by scribl, so
`scribl` could actually help facilitate the curation of biological
pathways from newly-published literature, in a format that is ready
for graph data repositories like Reactome.

# Availability

`scribl` is available as a package on PyPI with the source code and
documentation available at https://github.com/amberbiology/scribl.

# Acknowledgements

The development of the scribl platform was made possible with the
support of the [Association for Frontotemporal Degeneration
(AFTD)](https://theaftd.org/). We are grateful to AFTD members Debra
Niehoff and Penny Dacks for their support.

# References
