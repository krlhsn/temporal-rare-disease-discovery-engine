# Looking for Patterns Across Symptoms and Time

A health condition is not always described by one symptom. Sometimes the research question involves several features appearing across different parts of the body, and the timing of those features may matter too.

That is the idea I explored with the **Temporal Rare-Disease Discovery Engine (TRDDE)**. It is an educational Python prototype for comparing fictional profiles, looking at shared features and their illustrative onset-age intervals, and turning interesting overlaps into questions that could be examined in proper research.

The important word is *questions*. A pattern produced by this program is not a diagnosis, and it does not establish that two people have the same condition.

## Why look at timing as well as overlap?

Imagine two fictional profiles. Both contain a few of the same features, but those features are recorded across age ranges. Comparing only the list of shared features would leave out part of the picture. Looking at the intervals adds another dimension: do the illustrative age ranges overlap, or does one appear earlier in the example?

TRDDE combines two separate comparisons:

- **Feature similarity:** an inverse-frequency weighted Jaccard score. A feature found in fewer profiles receives more weight within the supplied demonstration cohort.
- **Temporal compatibility:** the proportion of shared features whose onset-age intervals overlap.

The prototype combines these values using a 70/30 weighting to create an exploratory ranking score. It also requires a candidate pair to share at least two features across at least two broad body-system labels. These are transparent design choices for exploring the idea, not medically validated weights or thresholds.

## Why the data are fictional

The built-in demonstration contains ten fictional profiles, twenty feature types and fifty illustrative observations. The feature identifiers are local SYN- identifiers; they are not Human Phenotype Ontology identifiers. The project does not contain real patient records, disease annotations or live connections to biomedical databases.

Using synthetic examples makes it possible to inspect how the comparison rules behave without presenting invented profiles as real patients. It also makes the limits visible: a program can calculate overlap in a small example, but that does not show that the same pattern exists in a real population.

The code compares profile pairs, records shared features and systems, checks interval relationships, and creates a structured research-question dossier for selected overlaps. The suggested next step is deliberately cautious: check whether a pattern can be verified in independent datasets, while considering missing information, ascertainment bias, confounding and alternative explanations.

## The difficult part is interpretation

A score can look precise even when the information behind it is only illustrative. That is why the project labels its combined value as an exploratory ranking score, not a probability or a measure of clinical importance.

The timing comparison has a similar boundary. Two intervals overlapping in a fictional profile does not prove that one feature caused another, that the features share a biological mechanism, or that the profiles represent the same disease. It only describes the relationship between the intervals supplied to the program.

I wanted the output to lead toward a better research question, not to make a stronger claim than the input can support. That distinction affects the names used in the code, the report fields and the limitations shown to the reader.

## What I learned from the prototype

Working through this idea made me think more carefully about how data representation shapes a result. A feature needs a clear identifier and a system label. A time value may need to be represented as an interval rather than a single exact age. A ranking rule needs to be understandable enough that someone can inspect what contributed to it.

It also showed me why a working prototype and a validated research method are different things. Synthetic data can help test the software logic, but meaningful biomedical conclusions would require suitable real-world datasets, expert review, careful statistical analysis and independent replication.

## What comes next

Possible next steps include documented mappings to established phenotype vocabularies, carefully governed data-import workflows, explicit handling of missingness and evidence quality, and evaluation against independent datasets. Those are future research directions, not capabilities currently included in this version.

TRDDE is a small exploration of one question: can combining feature overlap with timing help researchers formulate patterns worth checking? The prototype can demonstrate how that question might be structured. Whether any pattern is real is a separate question, and it needs evidence beyond this program.

---

**Project:** [Temporal Rare-Disease Discovery Engine on GitHub](https://github.com/krlhsn/temporal-rare-disease-discovery-engine)
**Course context:** Stanford Code in Place X, Fall 2026
**Author:** Kamrul Hassan

**Responsible use:** TRDDE is an educational research prototype, not a diagnostic, screening or clinical decision-support tool. No health or treatment decisions should be made using it.
