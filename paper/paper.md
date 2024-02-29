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
date: 28 February 2024
bibliography: paper.bib
---

# Summary

Searchable catalogs of curated scientific literature and metadata
often lack semantic detail contained in the curated articles.  Typical
literature searches based upon text and keywords are a blunt
instrument, generating large sets of articles of potential interest
that need to be read more closely to determine if they are relevant to
the researcher. In life science research, most scientific literature
databases are most immediately useful to scientists looking for
information in two categories (1) those looking general literature on
a broad research area, or (2) those looking for a precise terms,
e.g. a specific gene or author. A third category of literature search
exists in between these two extremes: searches where the desired
results involve a small set of agents (e.g., proteins, genes,
compounds, receptor complexes) or biological processes (e.g,
autophagy, cell cycle), but that are themselves components of much
larger systems.

It would therefore be extremely valuable for the researcher to be able
to query a literature database to extract and visualize relationships
between any specified agents and processes. Here we develop a system
that supports the annotation of scientific articles, to represent and
visualize these relationship. This system, `scribl`, consists of two
parts: (1) a simple syntax that can be used to curation of biological
relationships within the text of those articles, (2) a Python software
pipeline that can transform a literature database (currently
supporting the free, open-source [Zotero](https://www.zotero.org/)
database) with entries annotated with this syntax into graph database
suitable for the kind of relationship queries.

# Features

**The `scribl` language** The language was designed for the curation
from scientific articles, of the relationships between the various
biological agents and processes that they describe. `scribl`
statements are added as tags by a curator to each article in a
literature database to represent aspects of causual relationships
identified by the curator. \autoref{fig:scribl-examples} shows some
example statements.

|   |
|:--|
| `::agent c9orf72 :gene :protein :url https://www.uniprot.org/uniprot/Q96LT7`     |
| `::agent gtp :tag nucleoside, purine, nucleoside triphosphate`                   |
| `::process exportin releases cargo into cytoplasm @ exportin-1`                  |
| `::process smcr8 mutation > ulk1 phosphorylation < autophagy = smcr8 expression` |
: Example scribl statements []{label="fig:scribl-examples"}

This example shows two types of entities: (1) agents (`::agent`): are
actual biochemical entities (e.g. proteins) described in the
literature article in question, allow with some metadata about the
agent in question, (2) processes (`::process`) which represent
biological processes, which may be a specific biochemical process, but
more likely are more of a coarser-grained nature.

**The `scribl` Python package**.  The `scribl` Python package can
query a [Zotero](https://zotero.org) database containing declarative
statements in `scribl` syntax described above, and generate a graph
database. The resulting graph data structure can be then be exported
for use in a graph database platforms. `scribl` currently supports
output in one of two formats:

1. [Cypher query
language](https://opencypher.org/)[@francis_cypher_2018] used by the
graph database platform [neo4j](https://neo4j.com). The output Cypher
query can be used directly to initialize a Neo4j database.  The Neo4j
setup itself it not done by `scribl`, but must be installed
separately.

2.  [GraphML](http://graphml.graphdrawing.org/)
[@brandes_graphml_2002] format. This format can be read and used for
processing and visualization by packages such as Python's
[NetworkX](https://networkx.org/) [@hagberg_exploring_2008]. (see
\autoref{fig:graph-networkx} for example).

![Visualization of scribl database via NetworkX.\label{fig:graph-networkx}](../graphdb-visual.png)

Once created, it is possible to searches on the graph database not
possible with traditional keyword searching. For example, once the
scribl output is loaded into a Neo4j database, it is possible to write
Cypher queries of the kind: "Show me all of the agents that are
involved in the process `exportin` and the articles that describe
them".

# Statement of need

The biological relationships captured in `scribl` are not intended to
replace a reading of the literature but rather to further narrow down
the search for relevant biological agents and processes.

Nor is `scribl` intended to provide a semantic platform for the
construction of formal models of biological process and interacting
agents such as the modeling languages
[Kappa](https://kappalanguage.org/) [@boutillier_kappa_2020] and
[SBML](https://sbml.org/) [@keating_sbml_2020]. The development of
such models requires a much narrower focus on a specific set of agents
and reactions, and is significantly constrained by the requirement for
a level of specific, quantitative detail that most life science
articles do not provide. In this sense then, `scribl` could be
considered a platform for the development of a kind of coarse-grained
model of biological systems that sits somewhere between the very low
resolution representation of a system by keywords and literature
terms, and the very high resolution representation of a formal,
kinetic model. It is worth noting that at the time of writing, even
though a biological system might be comprehensively described in great
detail by a particular scientific article, the kind of natural
language processing5 technology required to extract an accurate,
formal model of that system from the article text has yet to reach the
level at which this could realistically be achieved algorithmically.

Nor is scribl intended to be a replacement for biological graph
databases such as [Reactome](https://reactome.org)
[@gillespie_reactome_2022]. The Reactome database is actually based
upon the same graph database engine that is the current default
supported by scribl, so scribl could actually serve as a useful aid to
facilitate the curation of biological pathways from newly-published
literature, in a format that is ready for graph data repositories like
Reactome. It is also often desirable for researchers to curate
literature databases that are focused on narrower, more specific areas
of interest, including those that may also be poorly represented in
the larger data repositories.

# Acknowledgements

The development of the scribl platform was made possible with the
support of the [Association for Frontotemporal Degeneration
(AFTD)](https://theaftd.org/). We are grateful to AFTD members Debra
Niehoff and Penny Dacks for their support.

# References
