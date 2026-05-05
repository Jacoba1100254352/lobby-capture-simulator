# Submission Strategy

## Primary Target

Primary journal target: **Regulation & Governance**.

Reason: the paper is strongest as a regulatory-governance mechanism article about how anti-capture reforms interact across transparency, enforcement, rulemaking, procurement, public financing, dark money, and revolving-door constraints. The Deep Research report recommends this as the best fit and reports an 11,000-word ceiling including abstract, references, endnotes, tables, and figures.

Working article frame:

- Main claim: organized interests preserve influence through strategic channel substitution when reforms constrain one visible route.
- Main audience: regulation, governance, public policy, public administration, and political economy scholars.
- Main empirical posture: public administrative data provide distributional anchors and validation moments, not causal estimates.
- Main results to keep in the article: one campaign snapshot, one sensitivity slice, one ablation table, a channel-mix figure, an evasion-sensitivity figure, a scenario tradeoff figure, and one interaction tradeoff view.
- Material to move to supplement before submission: full scenario catalog, full calibration queue, parser details, full sensitivity matrices, full ablation matrices, and implementation notes.

## Figure Plan

Wiley's figure-preparation guidance treats graphs, flowcharts, diagrams, scatter plots, and other text-based figures as line art and lists EPS/PDF as preferred formats. Wiley's LaTeX guidance also asks authors to provide electronic graphics files and not create figures using LaTeX code. The current manuscript therefore uses separate generated PDF figure files, with SVG sources retained for reproducibility:

- `paper/figures/Figure_1_channel_mix.pdf` and `.svg`: stacked channel-allocation bars for selected scenarios.
- `paper/figures/Figure_2_evasion_sensitivity.pdf` and `.svg`: line chart showing hidden influence rising as evasion freedom increases.
- `paper/figures/Figure_3_interaction_tradeoffs.pdf` and `.svg`: hidden-influence versus net-transparency interaction scatter.
- `paper/figures/Figure_4_scenario_tradeoffs.pdf` and `.svg`: capture-rate versus hidden-influence scenario scatter.
- `paper/figures/channel_mix.tex`, `evasion_sensitivity.tex`, `interaction_tradeoffs.tex`, and `scenario_tradeoffs.tex`: thin LaTeX wrappers that include the PDF graphics and keep captions/labels in the manuscript.

These are intentionally analytical figures, not illustrative decoration. They make the paper's mechanism legible while keeping the source reproducible from committed report CSVs.

## Template Plan

Wiley provides a generic LaTeX authoring template for Wiley journals. This repo now supports that path without making it the default local build:

- `paper/main.tex` is the compile-stable local manuscript used by `make paper`.
- `paper/regulation-governance-wiley.tex` is the Regulation & Governance/Wiley wrapper that uses Wiley's `USG` class.
- `make wiley-template` downloads the official `WileyDesign.zip` bundle into ignored `paper/.wiley-template/`.
- `make wiley-tex-deps` installs the extra Wiley-template packages into the user TeX tree through `tlmgr --usermode`.
- `make paper-wiley` attempts the Wiley-template build after the official bundle is fetched.
- `make submission-package` creates `dist/lobby-capture-wiley-submission.zip` with root-level LaTeX source, compiled PDF, generated tables, generated figure files, supporting information files, bibliography, Wiley support files, and patched peer-review class copy.
- `make paper-artifacts` is the normal post-edit refresh path: it reruns report sweeps, source moments, validation, calibration queue, generated tables, generated figures, the local PDF, the Wiley PDF, word count, and the submission zip.
- `make paper-artifacts-check` is the PDF/submission guard: it runs the full refresh, verifies the local and Wiley PDFs exist and are newer than their paper inputs, checks the submission zip contents, compiles the extracted submission zip from its root, and screens the Wiley PDF for generic template placeholder text.

The default build remains `make paper` because it is faster and uses the local article wrapper, but the Wiley wrapper is now reproducible after `make wiley-template wiley-tex-deps`. The build script creates ignored scratch files under `paper/.wiley-build/`, patches only the generated class copy to remove generic template sample journal art and placeholder publication metadata, and exposes Wiley's bundled `wileyNJD-Chicago-lastoo.bst` fallback under the class-required `wileyNJD-Chicago.bst` name; the primary `.bst` bundled in the current Wiley archive emits duplicate-function BibTeX errors on TeX Live 2026. The Wiley page also instructs authors to check the specific journal guidance and to submit both a LaTeX source bundle and a compiled PDF when submitting LaTeX through Wiley Research Exchange. `make figures` requires Inkscape on `PATH` so the generated SVG sources can be converted into Wiley-preferred PDF graphics.

## Submission Formatting Status

Current formatting choices made in the repository:

- author, affiliation, country, and corresponding email are present in the local article and Wiley wrapper;
- the manuscript includes data/code availability, financial disclosure, conflicts of interest, and AI-use disclosure statements;
- generated graphs are separate numbered PDF figure files, with legends retained in the manuscript through the LaTeX wrappers;
- the primary local draft uses `plainnat` author-year citations and a conventional 1-inch-margin article layout for compile stability;
- the Wiley-specific wrapper uses the official `USG` class once the downloaded template and full TeX package set are available;
- generated tables are set as wide table floats without `resizebox` scaling so the Wiley two-column reviewer PDF stays readable;
- CI runs Java 21 tests and `make paper-artifacts-check`, which rebuilds report snapshots, validation outputs, generated tables, generated figures, the local PDF, the Wiley PDF, word count, and the Wiley submission package before checking PDF freshness, package contents, and standalone package compilation. CI then runs `git diff --exit-code` so regenerated tracked artifacts cannot drift silently.

Before live submission, re-check the Regulation & Governance author page in Wiley Online Library under Contribute because Wiley notes that journal-specific instructions override generic Wiley guidance.

On this machine, the missing Wiley-template packages have been installed into the user TeX tree with `make wiley-tex-deps`; `make paper-artifacts-check` should be treated as the reproducibility check for the local PDF, Wiley wrapper, generated evidence, and submission package.

## Backup Target

Backup journal target: **Interest Groups & Advocacy**.

Retargeting implications:

- Narrow the article around lobbying organizations, funders, and advocacy coalitions.
- Reduce the paper to a focused 7,500-9,000 word actor-centered manuscript.
- Keep no more than six keywords.
- Prepare an anonymized submission package for double-blind review.
- Use Harvard-style author-date citations and endnotes rather than footnotes if the paper is moved to this venue.

## Conference Feedback Path

Preferred feedback route: Social Simulation Conference if the active call remains open; otherwise prepare the project for the next IC2S2, APSA, APPAM, or Social Simulation Conference cycle.

The conference version should lead with model architecture, validation design, and reproducibility rather than the full policy-theory argument.

## Why Not ACM First

The Congress Institutional Simulator paper uses ACM because it was framed for ACM Collective Intelligence as a computational framework for legislative design-space search. That paper's `acmart` setup uses anonymous review mode, ACM CCS concepts, ACM keywords, and ACM's author-year reference format. That is appropriate for a computing/collective-intelligence venue where the main contribution is a reusable computational framework for comparing institutional mechanisms.

The Lobby Capture Simulator has a different center of gravity. Its main contribution is a regulatory-governance mechanism argument about lobbying, money in politics, rulemaking, enforcement, dark money, public financing, and channel substitution. Regulation & Governance is therefore a better first target because the likely reviewers are closer to capture theory, public administration, regulation, transparency systems, and institutional reform.

ACM remains a plausible secondary path only if the manuscript is reframed as a computational-social-systems paper. That version would need:

- `acmart` rather than Wiley's `USG` class;
- ACM CCS concepts and required ACM metadata;
- `\Description{}` text for every figure;
- a methods-first contribution focused on simulation architecture, model reproducibility, and computational institutional design;
- a likely conference target such as ACM Collective Intelligence rather than a regulation/governance journal.

The practical reason not to use ACM now is that ACM's template is production infrastructure for ACM publications, not a general-purpose simulation-paper style. Using it for a Wiley journal would add the wrong metadata and review conventions while weakening the substantive journal fit.

## Source Links

- Deep Research venue report: `/Users/jacobanderson/Downloads/Deep Research Reports/Lobby Simulator/deep-research-report_journal-conference.md`
- Congress Institutional Simulator ACM paper reference: `/Users/jacobanderson/Documents/simulators/Congress Institutional Simulator/paper/README.md`
- Wiley figure-preparation guidance: <https://authorservices-ppd.wiley.com/author-resources/Journal-Authors/Prepare/manuscript-preparation-guidelines.html/figure-preparation.html>
- Wiley LaTeX authoring template: <https://authors.wiley.com/author-resources/Journal-Authors/Prepare/latex-template.html>
- Wiley submission help and data-availability guidance: <https://authors.wiley.com/help/submitting-your-manuscript.html>
- Wiley publishing ethics and AI disclosure guidance: <https://authors.wiley.com/ethics-guidelines/index.html>
- Wiley template bundle used by `make wiley-template`: <https://authors.wiley.com/asset/WileyDesign.zip>
- ACM LaTeX article-preparation guidance: <https://authors.acm.org/proceedings/production-information/preparing-your-article-with-latex>
