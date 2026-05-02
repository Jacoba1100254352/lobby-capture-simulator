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

Wiley's figure-preparation guidance treats graphs, flowcharts, diagrams, scatter plots, and other text-based figures as line art and lists EPS/PDF as preferred formats. The current manuscript therefore uses generated LaTeX line-art figures rather than bitmap screenshots:

- `paper/figures/channel_mix.tex`: stacked channel-allocation bars for selected scenarios.
- `paper/figures/evasion_sensitivity.tex`: line chart showing hidden influence rising as evasion freedom increases.
- `paper/figures/interaction_tradeoffs.tex`: hidden-influence versus net-transparency interaction scatter.
- `paper/figures/scenario_tradeoffs.tex`: capture-rate versus hidden-influence scenario scatter.

These are intentionally analytical figures, not illustrative decoration. They make the paper's mechanism legible while keeping the source reproducible from committed report CSVs.

## Template Plan

Wiley provides a generic LaTeX authoring template for Wiley journals. This repo now supports that path without making it the default local build:

- `paper/main.tex` is the compile-stable local manuscript used by `make paper`.
- `paper/regulation-governance-wiley.tex` is the Regulation & Governance/Wiley wrapper that uses Wiley's `USG` class.
- `make wiley-template` downloads the official `WileyDesign.zip` bundle into ignored `paper/.wiley-template/`.
- `make paper-wiley` attempts the Wiley-template build after the official bundle is fetched.

The default build remains `make paper` because the official Wiley template depends on packages that are not always present in TeX Live Basic. The Wiley page also instructs authors to check the specific journal guidance and to submit both a LaTeX source bundle and a compiled PDF when submitting LaTeX through Wiley Research Exchange.

On this machine, `make paper-wiley` fetches the official bundle successfully but reports a smaller local TeX install: `dashrule.sty`, `multirow.sty`, `cuted.sty`, `floatpag.sty`, `dblfloatfix.sty`, `soul.sty`, `xargs.sty`, `tcolorbox.sty`, `varwidth.sty`, `tikzpagenodes.sty`, `boites.sty`, and `wrapfig.sty` are missing. The local submission draft should therefore continue to use `make paper` until those packages or a fuller TeX Live installation are available.

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
- Wiley template bundle used by `make wiley-template`: <https://authors.wiley.com/asset/WileyDesign.zip>
- ACM LaTeX article-preparation guidance: <https://authors.acm.org/proceedings/production-information/preparing-your-article-with-latex>
