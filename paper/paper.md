---
title: 'scribl: A system for the semantic capture of relationships in biological literature'
tags:
  - systems biology
  - network biology
  - literature mining
  - bioinformatics
  - computational biology
authors:
  - name: Gordon Webster
    orcid: 0009-0009-2862-0467
    affiliation: "1, 2"
    equal-contrib: true
  - name: Alexander K. Lancaster
    orcid: 0000-0002-0002-9263
    affiliation: "1, 2"
    equal-contrib: true
affiliations:
  - name: Amber Biology LLC, USA
    index: 1
  - name: Ronin Institute, USA
    index: 2
date: 28 February 2024
bibliography: paper.bib
---

# Summary

The digital capture of research articles and their attendant metadata
in a database is an excellent way to create a searchable catalog of
scientific literature. In such a database however, nearly all of the
semantic detail contained in the curated articles is lacking. A
typical literature search based upon text and keywords can be a blunt
instrument, often generating large sets of articles of potential
interest that still need to be read more closely in order to determine
if the processes or phenomena that they describe are actually relevant
to the user. In life science research in particular, a scientific
literature database is most immediately useful to a scientist looking
for general literature on a broad research area, or conversely, to a
scientist who has very precise idea of what they are searching for -
perhaps even down to the title of a specific article, the name of a
specific gene, or the name of an author who is working on a research
problem that is directly relevant to their own interests. In between
these two extremes is the scientist whose research is focused on a
relatively narrow scientific area, the results of which require a
broader, more holistic perspective to make sense of. This latter
category arguably encompasses the great majority of life science
researchers who find themselves working on a relatively small set of
biological processes and entities that are themselves components of a
much larger system to which they contribute, and whose properties and
behaviors are largely defined by the context of this larger system in
which they are embedded.

As biology has become ever more quantitative with the advent of lab
automation and digital data capture, the rate of generation of
scientific data has significantly outstripped our ability to generate
real knowledge and insight from that data. As a case in point, the
differential expression of a panel of genes between a healthy and a
distressed cell might initially appear to be a set of unconnected data
points from which it is challenging to draw any conclusions, until the
relationships between the differentially expressed genes are made
clear by mapping them onto a specific cell signaling pathway. It is
these relationships between the many components of complex biological
systems and between the processes that they participate in, that are
central to the properties and behaviors of these systems to which we
would apply the term “biology”.

Beyond merely listing the names of the agents (proteins, genes,
compounds, receptor complexes etc. etc.) and processes underlying the
biology, it would therefore be extremely valuable for the researcher
to be able to query a scientific literature database based also upon
the relationships between these agents and processes. It is to this
end that a simple syntax was developed to allow for the curation of
these relationships along with the articles that describe them -
relationships that would otherwise be buried in the texts of those
articles.

# Statement of need

`scribl` is Python package that can query a literature database
containing declarative statements in `scribl` syntax related to the
processes described above, and generates a graph database [@scribl].
The `scribl` language was designed for the curation from scientific
articles, of the relationships between the various biological agents
and processes that they describe.

`scribl` statements are added as tags to articles in a literature
database (the **scribl** codebase currently supports the free,
open-source [Zotero](https://www.zotero.org/) database).  Here is an
example:

```
::agent c9orf72 :gene :protein :url https://www.uniprot.org/uniprot/Q96LT7
::agent gtp :tag nucleoside, purine, nucleoside triphosphate
::process exportin releases cargo into cytoplasm @ exportin-1
::process smcr8 mutation > ulk1 phosphorylation < autophagy = smcr8 expression
```

These tags are
parsed and used to create a graph data structure that can be then be
exported for use in a graph database platform such as
[neo4j](https://neo4j.com), or Python's
[NetworkX](https://networkx.org/), see \autoref{fig:graph-networkx}.


![Visualization of scribl database via NetworkX.\label{fig:graph-networkx}](../graphdb-visual.png)

Figure sizes can be customized by adding an optional second parameter:

![Visualization of scribl database via NetworkX.\label{fig:graph-networkx}](../graphdb-visual.png){ width=20% }

# Acknowledgements

The development of the scribl platform was made possible with the
support of the Association for Frontotemporal Degeneration. We are
particularly grateful to AFTD members Debra Niehoff and Penny Dacks
for their direction and guidance.

# References
