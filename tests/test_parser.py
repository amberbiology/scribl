from __future__ import annotations

__author__ = "Amber Biology"

import scribl
from scribl.parse_scribl import ScriblParser

tags = """
::category stress granules; ::category tdp-43 aggregation; ::category als
::category c9orf72 pathology; ::category neuroinflammation; ::category als
::category biomarkers; ::category c9orf72 pathology; ::category clinical; ::category mapt/tau pathology; ::category progranulin pathology; ::category tdp-43 aggregation
::category autophagy; ::category exosomal clearance; ::category tdp-43 aggregation; ::category als
::agent ambra :protein  :url https://www.uniprot.org/uniprot/Q9C0C7 | uvrag | beclin1; ::agent ampk :protein :url https://www.uniprot.org/uniprot/Q9Y478; ::agent atg1-atg13 complex :complex | ulk1 | atg13 | atg9 | fip200; ::agent atg13 :protein :url https://www.uniprot.org/uniprot/O75143; ::agent atg14 :protein :url https://www.uniprot.org/uniprot/Q6ZNE5; ::agent atg5 :protein :url https://www.uniprot.org/uniprot/Q9H1Y0; ::agent atg9 :protein :url https://www.uniprot.org/uniprot/Q7Z3C6; ::agent bad :protein :url https://www.uniprot.org/uniprot/Q92934 | calcineurin; ::agent bak :protein :url https://www.uniprot.org/uniprot/Q16611; ::agent bax :protein :url https://www.uniprot.org/uniprot/Q07812; ::agent bcl2 :protein :url https://www.uniprot.org/uniprot/P10415 | jnk1 | dapk | ip3r; ::agent beclin1 :protein :url https://www.uniprot.org/uniprot/Q14457 | ambra | vps34 | vps15; ::agent beclin1 core complex :complex | atg14 | uvrag | bif1; ::agent bif1 :protein :url https://www.uniprot.org/uniprot/Q9Y371; ::agent ca2+ :url https://pubchem.ncbi.nlm.nih.gov/compound/Calcium-ion :syn calcium; ::agent calcineurin :protein :url https://www.uniprot.org/uniprot/P48454; ::agent calpain :protein :url https://www.uniprot.org/uniprot/P17655 ~ atg5; ::agent camkk-beta :protein :url https://www.uniprot.org/uniprot/Q96RR4 ~ ampk; ::agent caspase8 :protein :url https://www.uniprot.org/uniprot/Q14790 ~ beclin1; ::agent cytochrome c :protein :url https://www.uniprot.org/uniprot/P08574; ::agent dapk :protein :url https://www.uniprot.org/uniprot/P53355 ~ bcl2; ::agent fip200 :protein :url https://www.uniprot.org/uniprot/Q8TDY2; ::agent ip3r :protein :url https://www.uniprot.org/uniprot/Q14643; ::agent jnk1 :protein :url https://www.uniprot.org/uniprot/P45983 ~ bcl2; ::agent lc3 :protein :biomarker :url https://www.uniprot.org/uniprot/Q9GZQ8; ::agent lc3i :protein :biomarker :url https://www.uniprot.org/uniprot/Q9GZQ8; ::agent lc3ii :protein :biomarker :url https://www.uniprot.org/uniprot/Q9GZQ8; ::agent mtor :protein :url https://www.uniprot.org/uniprot/P42345 ~ atg13 ~ ulk1; ::agent rapamycin :url https://pubchem.ncbi.nlm.nih.gov/compound/5284616; ::agent rubicon :protein :url https://www.uniprot.org/uniprot/Q92622 | beclin1; ::agent serca :protein :url https://www.uniprot.org/uniprot/O14983; ::agent ulk1 :protein :url https://www.uniprot.org/uniprot/O75385 :txt ulk1 is phosphorylated by mtor; ::agent uvrag :protein :url https://www.uniprot.org/uniprot/Q9P2Y5; ::agent vps15 :protein :url https://www.uniprot.org/uniprot/Q99570; ::agent vps34 :protein :url https://www.uniprot.org/uniprot/Q8NEB9; ::category apoptosis; ::category autophagy; ::process activation of ampk @ ampk < mtor phosphorylation of atg13 < mtor phosphorylation of ulk1; ::process activation of apoptotic caspases > apoptosis; ::process activation of bad @ bad > apoptosis; ::process activation of calcineurin > activation of bad @ calcineurin; ::process activation of calpain @ calpain > calpain cleaves atg5; ::process activation of camkk-beta @ camkk-beta > activation of ampk; ::process apoptosis; ::process autophagosome formation; ::process autophagy; ::process bcl2 binds beclin1 @ bcl2 @ beclin1 < autophagy; ::process bcl2 sequesters ip3r in er membrane @ ip3r @ bcl2 < release of cytochrome c into cytoplasm; ::process calcium influx into mitochondria > apoptosis; ::process calpain cleaves atg5 @ calpain @ atg5 > apoptosis < autophagosome formation > suppression of bcl2 activity in mitochondria; ::process caspase8 cleaves beclin1 < autophagosome formation @ caspase8 @ beclin1; ::process cell hypoxia; ::process cell starvation > mtor phosphorylation of atg13 > mtor phosphorylation of ulk1; ::process cellular stress > mtor phosphorylation of atg13 > mtor phosphorylation of ulk1; ::process cytosolic lc3i converted to membrane-bound lc3ii > autophagosome formation @ lc3i @ lc3ii; ::process elevation of cytoplasmic calcium levels > apoptosis > activation of camkk-beta @ ca2+; ::process formation of atg1-atg13 complex @ ulk1 @ atg13 @ fip200 @ atg9 > autophagy > autophagosome formation; ::process formation of beclin1 core complex @ beclin1 @ ambra @ vps34 @ vps15  + beclin1 core complex > autophagy > autophagosome formation; ::process lysosomal protein degradation; ::process mitochondrial outer membrane permeabilization > release of cytochrome c into cytoplasm; ::process mtor phosphorylation of atg13 < formation of atg1-atg13 complex; ::process mtor phosphorylation of ulk1 < formation of atg1-atg13 complex; ::process oligomerization of proapoptotic proteins bax and bak > mitochondrial outer membrane permeabilization; ::process phosphorylation of bcl2 @ bcl2 @ jnk1 @ dapk < bcl2 binds beclin1 < bcl2 sequesters ip3r in er membrane; ::process pumping calcium ions into er @ serca @ ca2+; ::process regulation of calcium exchange between er and cytoplasm @ ca2+ @ ip3r @ serca; ::process release of calcium ions into cytoplasm @ ip3r  @ ca2+ > elevation of cytoplasmic calcium levels; ::process release of cytochrome c into cytoplasm @ cytochrome c > activation of apoptotic caspases; ::process rubicon binds beclin1 @ rubicon @ beclin1 < formation of beclin1 core complex; ::process suppression of bcl2 activity in mitochondria @ atg5 @ bcl2 > apoptosis; ::process vesicle nucleation @ beclin1 > autophagosome formation
::agent caspase-1 :protein :url https://www.uniprot.org/uniprot/P29466; ::agent creb1 :protein :url https://www.uniprot.org/uniprot/P16220; ::agent rna-pol2 :protein :url https://www.uniprot.org/uniprot/P24928; ::agent tardbp :gene :url https://www.uniprot.org/uniprot/Q13148; ::agent tdp-43 :protein :url https://www.uniprot.org/uniprot/Q13148; ::agent ubiquitin :protein :url https://www.uniprot.org/uniprot/P0CG47; ::category als; ::category apoptosis; ::category rna processing; ::category tdp-43 aggregation
::agent importin-a :protein :url https://www.uniprot.org/uniprot/P52292; ::agent nup107 :protein :url https://www.uniprot.org/uniprot/P57740; ::agent nup62 :protein :url https://www.uniprot.org/uniprot/P37198; ::agent ran :protein :url https://www.uniprot.org/uniprot/P62826; ::agent rangap1 :protein :url https://www.uniprot.org/uniprot/P46060; ::agent tdp-43 :protein :url https://www.uniprot.org/uniprot/Q13148; ::category als; ::category apoptosis; ::category nuclear transport; ::category stress granules; ::category tdp-43 aggregation
::agent tau :protein :url https://www.uniprot.org/uniprot/P10636; ::agent tdp-43 :protein  :url https://www.uniprot.org/uniprot/Q13148; ::agent ubiquitin :protein :url https://www.uniprot.org/uniprot/P0CG47; ::category biomarkers; ::category clinical; ::category mapt/tau pathology; ::category progranulin pathology; ::category tdp-43 aggregation
::agent arp2 :protein :url https://www.uniprot.org/uniprot/P61160; ::agent arp3 :protein :url https://www.uniprot.org/uniprot/P61158; ::agent c9orf72 :gene :protein :url https://www.uniprot.org/uniprot/Q96LT7; ::agent coronin :protein :url https://www.uniprot.org/uniprot/P31146; ::agent g3bp1 :protein :url https://www.uniprot.org/uniprot/Q13283; ::agent hur :protein  :url https://www.uniprot.org/uniprot/Q15717; ::agent importin-b1 :protein  :url https://www.uniprot.org/uniprot/Q14974; ::agent ran :protein :url https://www.uniprot.org/uniprot/P62826; ::agent sqstm1 :protein :url https://www.uniprot.org/uniprot/Q13501; ::agent tia1 :protein :url https://www.uniprot.org/uniprot/P31483; ::category als; ::category c9orf72 pathology; ::category genetics
::agent alpha-synuclein :protein :url https://www.uniprot.org/uniprot/P37840; ::agent tdp-43 :protein :url https://www.uniprot.org/uniprot/Q13148; ::agent ubiquitin :protein :url https://www.uniprot.org/uniprot/P0CG47; ::category als; ::category nuclear transport; ::category tdp-43 aggregation
::agent csl4 :protein :url https://www.uniprot.org/uniprot/Q9Y3B2; ::agent kiaa0052 :protein :url https://www.uniprot.org/uniprot/Q15477; ::agent mpp6 :protein :url https://www.uniprot.org/uniprot/Q99547; ::agent mtr3 :protein :url https://www.uniprot.org/uniprot/Q5RKV6; ::agent oip2 :protein :url https://www.uniprot.org/uniprot/Q96B26; ::agent rrp4 :protein :url https://www.uniprot.org/uniprot/Q13868; ::agent rrp40 :protein :url https://www.uniprot.org/uniprot/Q9NQT5; ::agent rrp41 :protein :url https://www.uniprot.org/uniprot/Q9NPD3; ::agent rrp42 :protein :url https://www.uniprot.org/uniprot/Q15024; ::agent rrp44 :protein :url https://www.uniprot.org/uniprot/Q9Y2L1; ::agent rrp46 :protein :url https://www.uniprot.org/uniprot/Q9NQT4; ::agent scl100 :protein :url https://www.uniprot.org/uniprot/Q01780; ::agent scl75 :protein :url https://www.uniprot.org/uniprot/Q06265; ::category exosomal clearance; ::category rna processing
::agent atg101 :protein :url https://www.uniprot.org/uniprot/Q9BSB4 | atg13 | wdr41 | ulk1; ::agent atg13 :protein :url https://www.uniprot.org/uniprot/O75143; ::agent c9orf72 :protein :gene :url https://www.uniprot.org/uniprot/Q96LT7 | c9orf72 complex | smcr8 | rab39b; ::agent c9orf72 complex :complex | ulk1 complex; ::agent cathepsin l :protein :url https://www.uniprot.org/uniprot/P07711; ::agent lc3 :protein :biomarker  :url https://www.uniprot.org/uniprot/Q9GZQ8; ::agent lc3i :protein :biomarker :url https://www.uniprot.org/uniprot/Q9GZQ8; ::agent lc3ii :protein :biomarker :url https://www.uniprot.org/uniprot/Q9GZQ8; ::agent mtor :protein :url https://www.uniprot.org/uniprot/P42345 | rapamycin; ::agent procathepsin l :protein :url https://www.uniprot.org/uniprot/P07711; ::agent rab39b :protein :url https://www.uniprot.org/uniprot/Q96DA2; ::agent rapamycin :url https://pubchem.ncbi.nlm.nih.gov/compound/5284616; ::agent smcr8 :protein :url https://www.uniprot.org/uniprot/Q8TEV9; ::agent ulk1 :protein :url https://www.uniprot.org/uniprot/O75385 | atg13 | ulk1 complex :syn  atg1; ::agent ulk1 complex :complex; ::agent wdr41 :protein :url https://www.uniprot.org/uniprot/Q9HAD4; ::category autophagy; ::category c9orf72 pathology; ::category genetics; ::category lysosomal clearance; ::process autophagosome formation @ ulk1 complex @ ulk1; ::process autophagy @ ulk1 complex; ::process c9orf72 hexanucleotide repeat expansion; ::process c9orf72 knockout < ulk1 phosphorylation > procathepsin l expression > autophagy; ::process c9orf72 mutation > c9orf72 hexanucleotide repeat expansion; ::process cell starvation > interaction of c9orf72 complex and ulk1 complex; ::process interaction of c9orf72 complex and ulk1 complex @ ulk1 complex @ c9orf72 complex; ::process lc3 processing @ lc3 + lc3i + lc3ii; ::process lysosomal protein degradation @ cathepsin l; ::process mtor-mediated inhibition of autophagy @ mtor < autophagy; ::process phagophore recruits atg proteins > autophagosome formation @ atg101 @ atg13; ::process procathepsin l expression + procathepsin l; ::process procathepsin l processing @ procathepsin l + cathepsin l; ::process regulation of ulk1 expression @ ulk1 = ulk1 expression; ::process smcr8 expression  + smcr8; ::process smcr8 knockout < smcr8 expression < autophagosome formation < lysosomal protein degradation > lc3 processing; ::process smcr8 mutation > ulk1 phosphorylation < autophagy = smcr8 expression; ::process ulk1 expression + ulk1; ::process ulk1 phosphorylation < autophagy @ ulk1
::agent  caspase-1 :protein :url https://www.uniprot.org/uniprot/P29466; ::agent  tau :protein :url https://www.uniprot.org/uniprot/P10636; ::agent mapt  :gene :url https://www.uniprot.org/uniprot/P10636; ::agent tardbp :gene :url https://www.uniprot.org/uniprot/Q13148; ::agent tdp-43 :protein :url https://www.uniprot.org/uniprot/Q13148; ::category als; ::category nuclear transport; ::category tdp-43 aggregation
::category genetics; ::category tdp-43 aggregation; ::category als
::category genetics; ::category neuroinflammation; ::category progranulin pathology
::agent adamts7 :protein :url https://www.uniprot.org/uniprot/Q9UKP4 :syn a disintegrin and metalloproteinase with thrombospondin motifs 7 ~ progranulin; ::agent akt :protein :url https://www.uniprot.org/uniprot/P31751 :syn akt2; ::agent apoa1 :protein :url https://www.uniprot.org/uniprot/P02647 :syn apolipoprotein a-1; ::agent cpg :dna :syn cpg dinucleotide | tlr9; ::agent cxcl1 :protein :url https://www.uniprot.org/uniprot/P09341 :syn mgsa, nap-3; ::agent elastase :protein :url https://www.uniprot.org/uniprot/P08246 ~ progranulin; ::agent erk1 :protein :url https://www.uniprot.org/uniprot/P27361 :syn mapk3; ::agent granulin :protein :url https://www.uniprot.org/uniprot/P28799; ::agent grn :gene  :url https://www.uniprot.org/uniprot/P28799; ::agent grn rna :rna :mrna :url https://www.uniprot.org/uniprot/P28799; ::agent il12 :protein :url https://www.uniprot.org/uniprot/P29460 :syn interleukin-12; ::agent il6 :protein :url https://www.uniprot.org/uniprot/P05231 :syn interleukin-6; ::agent il8 :protein :url https://www.uniprot.org/uniprot/P10145 :syn interleukin-8; ::agent lamp1 :protein :url https://www.uniprot.org/uniprot/P11279; ::agent mcp-1 :protein :url https://www.uniprot.org/uniprot/P13500 :syn ccl2, c-c motif chemokine 2; ::agent mmp12 :protein :url https://www.uniprot.org/uniprot/P39900 :syn macrophage metalloelastase ~ progranulin; ::agent mmp14 :protein :url https://www.uniprot.org/uniprot/P50281 ~ progranulin; ::agent p75ntr :protein :url https://www.uniprot.org/uniprot/P08138 :syn ngfr, low affinity neurotrophin receptor; ::agent pi3k :protein :url https://www.uniprot.org/uniprot/P48736 | pi3k regulatory complex; ::agent pi3k regulatory complex :complex | pi3k; ::agent progranulin :protein :url https://www.uniprot.org/uniprot/P28799; ::agent proteinase3 :protein :url https://www.uniprot.org/uniprot/P24158 :syn prtn3, myeloblastin ~ progranulin; ::agent slpi :protein :url https://www.uniprot.org/uniprot/P03973 :syn antileukoproteinase :txt protease inhibitor | progranulin; ::agent sortilin :protein :url https://www.uniprot.org/uniprot/Q99523 | progranulin | p75ntr; ::agent tdp-43 :protein :url https://www.uniprot.org/uniprot/Q13148 ~ grn rna; ::agent tlr9 :protein :url https://www.uniprot.org/uniprot/Q9NR96 :syn toll-like receptor 9; ::agent tnf-alpha :protein :url https://www.uniprot.org/uniprot/P01375 :syn tnf; ::agent tnfr :protein :url https://www.uniprot.org/uniprot/P20333 :syn tumor necrosis factor receptor | tnf-alpha | progranulin; ::agent ubiquitin :protein :url https://www.uniprot.org/uniprot/P0CG47; ::agent vldl :protein :syn very low density lipoprotein; ::category clinical; ::category neuroinflammation; ::category progranulin pathology; ::category tdp-43 aggregation; ::process activation of cell proliferation pathways @ progranulin @ erk1 @ pi3k @ akt; ::process activation of tlr9 @ tlr9 @ progranulin @ granulin @ cpg :txt progranulin or granulin?; ::process apolipoprotin a1 binds progranulin @ apoa1 @ progranulin < protease cleavage of progranulin - granulin; ::process autophagy @ progranulin @ sortilin; ::process double knockdown of elastase and proteinase3 @ elastase @ proteinase3 > elevation of intracellular progranulin levels; ::process elevated expression of inflammatory cytokines @ mcp-1 @ cxcl1 @ il6 @ il12 @ tnf-alpha; ::process elevation of intracellular progranulin levels @ progranulin; ::process formation of pi3k regulatory complex @ pi3k + pi3k regulatory complex; ::process grn mutation @ grn > tdp-43 aggregation > progranulin haploinsufficiency; ::process hepatic VLDL secretion @ vldl @ sortilin; ::process impairment of synaptic plasticity; ::process increase in density of synaptic vesicles :txt potential biomarker for porgranulin insufficiency?; ::process inflammatory stimuli in astrocytes > progranulin expression @ granulin; ::process loss of tdp-43 from nucleus @ tdp-43 < rna processing; ::process lysosomal protein degradation @ progranulin @ sortilin; ::process neurite outgrowth @ progranulin; ::process progranulin binds tnf receptor @ progranulin @ tnfr <  tnf-alpha binds tnf receptor < tnf-alpha induction of il8 release; ::process progranulin expression @ grn + progranulin > activation of cell proliferation pathways < tnf-alpha induction of il8 release > neurite outgrowth; ::process progranulin haploinsufficiency @ grn < progranulin expression > elevated expression of inflammatory cytokines; ::process progranulin knockdown < neurite outgrowth > reduction of synaptic connectivity > impairment of synaptic plasticity; ::process proneurotrophin-induced apoptosis @ sortilin; ::process prosaposin trafficking to lysosomes @ sortilin; ::process protease cleavage of progranulin @ progranulin @ elastase @ mmp12 @ mmp14 @ proteinase3 @ adamts7 + granulin; ::process reduction of synaptic connectivity > increase in density of synaptic vesicles; ::process regulation of extracellular progranulin levels @ progranulin @ sortilin; ::process rna processing @ tdp-43 @ grn rna; ::process slpi binds progranulin @ slpi @ progranulin < protease cleavage of progranulin - granulin; ::process slpi expression < protease cleavage of progranulin @ slpi; ::process tdp-43 aggregation @ tdp-43 > loss of tdp-43 from nucleus; ::process tnf-alpha binds tnf receptor @ tnf-alpha @ tnfr > tnf-alpha induction of il8 release; ::process tnf-alpha induction of il8 release @ progranulin @ tnf-alpha @ il8; ::process ubiquitination of tdp-43 @ tdp-43 @ ubiquitin > tdp-43 aggregation; ::process wound healing > progranulin expression
::category neuroinflammation; ::category progranulin pathology
::category neuroinflammation; ::category progranulin pathology
::category genetics; ::category neuroinflammation; ::category progranulin pathology; ::category tdp-43 aggregation; ::category als
::resource protein data bank :url https://www.rcsb.org/search :txt archive of structural data of biological macromolecules"""

parse_text = tags.split("\n")

ue_error = "Unknown entity [bloop] in relationship @: [::process phagophore recruits atg proteins > autophagosome formation ::process phagophore recruits atg proteins @ atg101 @ atg13 ::process phagophore recruits atg proteins @ bloop ]"


def test_start():
    print("\n\nTesting scribl_code parsing ...")


def test_parser():
    print("Testing parser with general parse text ...")
    sp = ScriblParser()
    for line in parse_text:
        sp.reset()
        sp.parse(line, split_text=scribl.tag_delimiter)
        assert sp.data["errors"] == []
        assert sp.data["warnings"] == []


def test_parser_errors():
    print("Testing parser error detection and handling ...")
    sp = ScriblParser()
    print(" Unparsable line ...")
    line = "::categry neuroinflammation; ::category progranulin pathology"
    sp.reset()
    sp.parse(line, split_text=scribl.tag_delimiter)
    assert len(sp.data["errors"]) == 1
    assert (
        sp.data["errors"][0]
        == "Line: 0 Unable to parse statement [::categry neuroinflammation]"
    )
    print(" Unknown entity in relationship ...")
    line = "::category lysosomal clearance; ::process autophagosome formation @ ulk1 complex"
    sp.reset()
    sp.parse(line, split_text=scribl.tag_delimiter)
    assert len(sp.data["errors"]) == 1
    assert (
        sp.data["errors"][0]
        == 'Unrecognized entity "ulk1 complex" in relationship: ::process autophagosome formation ... @ ulk1 complex'
    )
    print(" Invalid relationship for item type ...")
    line = "::category lysosomal clearance; ::process autophagosome formation | ulk1 complex"
    sp.reset()
    sp.parse(line, split_text=scribl.tag_delimiter)
    assert len(sp.data["errors"]) == 1
    assert (
        sp.data["errors"][0]
        == 'Line: 1 Invalid relationship "| ulk1 complex" for "::process" ignored [::process autophagosome formation | ulk1 complex]'
    )
    print(" Tag length exceeds Zotero max length ...")
    line1 = "::category lysosomal clearance; ::process this is a very long process name whose purpose is to exceed the maximum number of characters "
    line2 = "that Zotero allows for a tag and to trigger the automatic check that the parser does on tag length for testing purposes blah blah blah "
    line3 = "blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah"
    line = line1 + line2 + line3
    sp.reset()
    sp.parse(line, split_text=scribl.tag_delimiter)
    assert len(sp.data["warnings"]) == 1
    assert len(sp.data["errors"]) == 0
    assert (
        sp.data["warnings"][0][:107]
        == "Line: 1 Statement length exceeds max. for Zotero syncing: ::process this is a very long process name whose "
    )
    print(" Test multiple item parsing and parse summary ...")
    sp.reset()
    sp.parse(parse_text[5], split_text=scribl.tag_delimiter)
    assert sp.parse_summary() == {
        "::category": 2,
        "::agent": 35,
        "::process": 34,
        "::resource": 0,
        "errors": 0,
        "warnings": 0,
    }


def test_parser_tools():
    print("Testing parser tools ...")
    sp = ScriblParser()
    line = parse_text[5]
    sp.parse(line, split_text=scribl.tag_delimiter)
    assert sp.data["errors"] == []
    assert sp.data["warnings"] == []
    ref = {
        "urls": ["https://www.uniprot.org/uniprot/Q9Y478"],
        "labels": [":protein"],
        "tags": [],
        "notes": [],
        "relationships": [],
        "synonyms": [],
    }
    assert sp.get("::agent", "ampk") == ref
    assert sp.catalog("::agent")[:5] == [
        "ambra",
        "ampk",
        "atg1-atg13 complex",
        "atg13",
        "atg14",
    ]
    assert sp.parse_summary() == {
        "::category": 2,
        "::agent": 35,
        "::process": 34,
        "::resource": 0,
        "errors": 0,
        "warnings": 0,
    }
