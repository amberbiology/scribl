---
title: 'scribl: A system for the semantic capture of relationships in biological literature'
tags:
  - systems biology
  - network biology
  - literature mining
  - bioinformatics
  - computational biology
  - Zotero
  - graph database
authors:
  - name: Gordon D. Webster
    orcid: 0009-0009-2862-0467
    affiliation: "1"
    equal-contrib: true
  - name: Alexander K. Lancaster
    orcid: 0000-0002-0002-9263
    affiliation: "1, 2"
    equal-contrib: true
affiliations:
  - name: Amber Biology LLC, USA
    index: 1
  - name: Institute for Globally Distributed Open Research and Education
    index: 2
date: 15 April 2024
bibliography: paper.bib
---

# Summary

When using literature databases, researchers in systems biology need
to go beyond simple keyword-based queries of biological agents (e.g.,
proteins, genes, compounds, receptor complexes) and processes (e.g,
autophagy, cell cycle) [@krallinger_linking_2008] that return
lists of articles, to extracting and visualizing relationships documented
within those papers [@cary_pathway_2005; @suderman_tools_2007; @pavlopoulos_visualizing_2015].
Here we describe a system that supports the annotation of scientific
articles, that represent and visualize these relationships. This
system, `scribl`, consists of two parts: (1) a simple syntax that can
be used to curate the biological relationships described within the text of
those articles, (2) a Python software API and pipeline that can
transform a [Zotero](https://www.zotero.org/) literature database,
with entries annotated with this syntax, into a database suitable for
graph-based relationship queries.

# The `scribl` language

The language was designed for the curation of scientific articles to
document the relationships between biological agents and processes
that they describe. Examples of relationships for each of the five
basic entities for a single article are shown in
\autoref{fig:scribl-schema}.

![The scribl schema comprises a hierarchy of five basic entities: `article`, `category`, `resource`, `process`, and `agent`. Here we depict an example network of entities and possible relationships for a single `article`.\label{fig:scribl-schema}](scribl-schema.png){ width=82% }

A curator can add `scribl` statements as tags to each article
in a literature database, to represent aspects of the causal relationships
that are described in the article.

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

The `scribl` Python package provides an API to query a [Zotero](https://zotero.org)
database where each literature record has been annotated using
declarative statements in the `scribl` syntax described in
\autoref{scribl-examples}. Currently, the literature source for
`scribl` input can be either a remote Zotero database, or a file
export from a local Zotero installation. Once the Zotero data has been
parsed, the resulting graph data structure can be then be exported for
use in graph database platforms. `scribl` also supports the
incremental updating of the graph database as new Zotero entries come
in (\autoref{fig:scribl-workflow}).

![Two major workflows for the `scribl` software: creating a new graph database (left) and updating an existing one (right). The workflow contains a step that identifies possible syntactic errors in `scribl` statements so that they can be fixed in the Zotero database before database generation. Note that "Zotero csv export" could be replaced by a query to a remote Zotero library  \label{fig:scribl-workflow}](scribl-workflow.png){ width=102% }

`scribl` functions can be accessed programatically through writing a
Python script that calls the `scribl` API, or via the included
command-line program `scribl`.

`scribl` currently supports output in one of two graph formats:

1. [Cypher query language](https://opencypher.org/)
   [@francis_cypher_2018] used by the graph database platform
   [neo4j](https://neo4j.com). The output Cypher query text can be
   used directly to initialize a Neo4j database.  The Neo4j setup
   itself is not automated by `scribl` and must be installed
   separately.

2. [GraphML](http://graphml.graphdrawing.org/) [@brandes_graphml_2002]
   format that can be read and used for processing and visualization
   by packages such as Python's [NetworkX](https://networkx.org/)
   [@hagberg_exploring_2008]. The `scribl` command-line program can
   generate visualizations (e.g, \autoref{fig:graph-networkx}) from
   GraphML output, and from an input Zotero file in CSV format
   directly, a basic example of which is shown below:

   ``` shell
   scribl -g db --z zotero.csv --networkx-fig graphdb-visual.png
   ```

![NetworkX visualization of a graph database exported as GraphML, generated directly by `scribl`.\label{fig:graph-networkx}](../graphdb-visual.png){ width=70% }

Once a graph database has been created, queries can be created
that are not possible with traditional keyword searching. For example, once the
scribl output is loaded into a Neo4j database, it is possible to write
Cypher queries of the kind: "Show me all of the agents that are
involved in the process `nuclear export` along with the articles that describe
them".

# Statement of need

### Why `scribl`?

The `scribl` platform was developed to fill a need for a simple way to
enable global sharing and collaborative curation of biological
relationships embedded in literature records, and to rapidly translate
those relationships into queryable graph networks. The `scribl` syntax
was designed to be simple to learn, but rich enough to
represent important relationships relevant to molecular and systems
biology.

Zotero was chosen as the initial backend, because it is simple to
install and run, as well as supporting the tagging of literature records and
web-based curation. `scribl` allows a researcher or
group of researchers, to rapidly build and visualize important
relationships useful for understanding the cellular and systems biology
within a chosen subdomain. In fact our main use-case for `scribl` was
the building of a relationship database of neurodegenerative disease
pathways for the frontotemporal degeneration (FTD) research community.

### What `scribl` is not

`scribl` is not primarily intended for the construction of formal,
kinetic models of biological systems in the way that modeling languages such as
[Kappa](https://kappalanguage.org/) [@boutillier_kappa_2020] and
[SBML](https://sbml.org/) [@keating_sbml_2020] are. However, these
networks can be considered a coarse-grained model of biological
systems that sit somewhere between low resolution, keyword-based
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
