# Nature Communications preparation notes

Scope: this note translates the current Nature Communications author guidance into concrete rules for the strong-motion predictability-boundary manuscript.

## Official format constraints

- Article type is appropriate for a full research paper with an important advance for a specialist community.
- Initial submission is format-flexible. A single Word, TeX, LaTeX or PDF file containing text and figures is acceptable at first submission, with a 30 MB limit.
- The Article page recommends a concise main text, ideally no more than 5000 words excluding Abstract, Methods, References and figure legends.
- Title should be no more than 15 words, without punctuation, puns or exaggerated language.
- Abstract should be no more than 200 words, should not contain references, and should be understandable outside the immediate specialty.
- Standard order: Title, Authors, Abstract, Introduction, Results, Discussion, Methods, Data Availability, Code Availability, References, Acknowledgements, Author Contributions, Competing Interests, Display Items, Supplementary Information.
- Up to 10 display items are allowed in the main text. Figure legends should be no more than 350 words each.
- Data Availability and Code Availability statements are required. Data needed to interpret, verify and extend the work must be transparent and accessible to editors and reviewers.
- Supplementary Information should be a separate file and should avoid unsupported statements such as "data not shown".

Official sources:

- Nature Communications Guide to authors: https://www.nature.com/ncomms/submit/guide-to-authors
- Nature Communications How to submit: https://www.nature.com/ncomms/submit/how-to-submit
- Nature Communications Article type: https://www.nature.com/ncomms/submit/article
- Nature Communications formatting instructions: https://www.nature.com/documents/ncomms-formatting-instructions.pdf
- Nature Portfolio reporting standards: https://www.nature.com/nature-portfolio/editorial-policies/reporting-standards

## Writing rules for this manuscript

- Lead with the earthquake-engineering problem: early warning needs strong-shaking forecasts before the destructive motion arrives.
- Frame the contribution as a measured predictability boundary under public strong-motion data, not as a claim that a new model solves early warning.
- Define PGA, PGV and spectral acceleration on first use.
- Keep model details out of the opening paragraphs. The paper should first explain the question, the data scale, the splits and the boundary result.
- Avoid language that Nature explicitly flags: "novel", "new", "for the first time", "unprecedented", and other inflated claims.
- Avoid defensive sentence patterns. State what was measured, what held across audits, and where the boundary remains.
- Separate evidence layers:
  - validated main evidence: InstanceGM and K-NET held-station, bootstrap, support and tail audits;
  - transfer evidence: Japan to Europe and Australia, with target-offset calibration;
  - practical limitation: AQ2009GM is partially processed and should be described as supporting transfer evidence unless the full stream finishes;
  - future work: operational alerting and dense real-time deployment.

## Figure style rules

- Use clean white backgrounds, black or dark-gray text, thin gray grid lines only when needed.
- Use one sans-serif font family across all panels.
- Use consistent panel labels, preferably lowercase bold labels at the upper-left of each panel.
- Use a colorblind-readable palette: blue for target-domain, orange for source-domain, green for offset or calibrated results, gray for baselines or reference lines.
- Keep legends outside dense data regions. Do not let markers, labels or legends overlap.
- Put units in axis labels. Use the same y-axis scale for panels that are directly compared.
- Figure titles should describe the measured quantity, not the conclusion.
- Export production figures as vector PDF/SVG where possible, or raster images at high resolution for review copies.

## Current template decision

Use Markdown as the source manuscript now because it is easy to revise and audit with the evolving experiment outputs. Before submission, convert the same content to Word or LaTeX. Nature Communications does not require a strict Word template at initial submission, and its formatting instructions allow standard Word, TeX, LaTeX or PDF files.

## Immediate gaps before real submission

- Final author list, affiliations, corresponding-author details and ORCIDs.
- Complete reference list from Zotero/literature manager. Do not fabricate citations.
- Public repository or archived release DOI after removing internal history.
- Data repository links or exact access statements for InstanceGM, K-NET, ESM, AQ2009GM and derived feature tables.
- Supplementary Information with dataset inventory, feature definitions, split checks, sensitivity analyses and full metric tables.
- Cover letter explaining why the predictability boundary matters to a broad Nature Communications readership.
