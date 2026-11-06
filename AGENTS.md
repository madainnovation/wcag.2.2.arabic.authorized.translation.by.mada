# Arabic WCAG 2.2 translation

This project translates the W3C WCAG 2.2 Recommendation into Arabic using the
published Arabic WCAG 2.1 translation as its linguistic reference.

- Primary Arabic reference: https://www.w3.org/Translations/WCAG21-ar/
- Pinned English target: https://www.w3.org/TR/2024/REC-WCAG22-20241212/
- Preserve the published 2.1 Arabic wording for unchanged requirements. Use
  `النفاذ` for accessibility and consult `TERMINOLOGY.md` before introducing terms.
- New and revised translations are review drafts. Never describe this project
  as a W3C Authorized Translation or reuse the 2.1 approval, reviewer list,
  coordinator designation, or publication date as approval of 2.2.
- Preserve normative force, numbers, units, levels, exceptions, cross-references,
  and the distinction between informative notes and normative requirements.
- Preserve English technical identifiers, formulae, and bibliography titles.
- Edit `translation/changes.html` and `translation/edits.json`; regenerate
  `wcag22-ar/index.html` with `scripts/build.py`. The root `index.html` redirects
  to that document. Do not hand-edit generated outputs.
- Use the original English W3C WCAG 2.2 HTML as the template. Preserve its
  structure and styles; apply Arabic direction adaptations in `translation/rtl.css`.
- Keep Arabic translation attribution in `translation/contributors.html`.
  Attribute published 2.1 contributors to that work; distinguish these credits
  from the English specification authors and any future 2.2 review team.
- Reference snapshots are unmodified evidence. Do not edit them.
- Record any deliberate correction to inherited wording in `REVIEW.md`.
- Run `scripts/build.py` and `scripts/validate.py` after translation changes.
  Structural validation does not constitute linguistic or W3C approval.
