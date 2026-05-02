# Submission Strategy

## Primary Target

Primary journal target: **Regulation & Governance**.

Reason: the paper is strongest as a regulatory-governance mechanism article about how anti-capture reforms interact across transparency, enforcement, rulemaking, procurement, public financing, dark money, and revolving-door constraints. The Deep Research report recommends this as the best fit and reports an 11,000-word ceiling including abstract, references, endnotes, tables, and figures.

Working article frame:

- Main claim: organized interests preserve influence through strategic channel substitution when reforms constrain one visible route.
- Main audience: regulation, governance, public policy, public administration, and political economy scholars.
- Main empirical posture: public administrative data provide distributional anchors and validation moments, not causal estimates.
- Main results to keep in the article: one campaign snapshot, one sensitivity slice, one ablation table, and one interaction tradeoff view.
- Material to move to supplement before submission: full scenario catalog, full calibration queue, parser details, full sensitivity matrices, full ablation matrices, and implementation notes.

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

## Source Links

- Deep Research venue report: `/Users/jacobanderson/Downloads/Deep Research Reports/Lobby Simulator/deep-research-report_journal-conference.md`
- Wiley LaTeX authoring template: <https://authors.wiley.com/author-resources/Journal-Authors/Prepare/latex-template.html>
- Wiley template bundle used by `make wiley-template`: <https://authors.wiley.com/asset/WileyDesign.zip>
