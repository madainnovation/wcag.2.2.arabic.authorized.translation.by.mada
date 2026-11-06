# WCAG 2.2 Arabic translation

[GitHub repository](https://github.com/madainnovation/wcag.2.2.arabic.authorized.translation.by.mada)
· [Public HTML preview](https://madainnovation.github.io/wcag.2.2.arabic.authorized.translation.by.mada/)

The public preview is served by GitHub Pages and updated by the publishing
workflow. Both version links in the translation header use this public URL.

Open **[wcag22-ar/index.html](wcag22-ar/index.html)**. The `wcag22-ar/` folder is the
portable deliverable: the Arabic document, local W3C styles and images, the
terminology register, source references, and review notes. Copy the whole folder
to retain its formatting. It can be opened directly without a server.

The document uses the actual W3C WCAG 2.2 English HTML template dated
12 December 2024. Its section hierarchy, contents list, numbering, help links,
definition anchors, and W3C presentation are retained, with Arabic text and
right-to-left adaptations. A bilingual translation header follows the published
Arabic 2.1 layout, with 2.2 draft details and the updated project links.
The published Arabic WCAG 2.1 translation is the
linguistic reference; `النفاذ` remains the core accessibility term.

This is a **review draft**, not a W3C Authorized Translation. It contains all
140 sections, 86 active success criteria, and 101 glossary definitions. The nine
new criteria and revised passages have draft Arabic translations. Criterion
4.1.1 is retained only as an obsolete/removed entry, as in the English source.
The linked Understanding and Techniques documents are external English resources
and are outside this translation's scope.

## About Mada Center

[Mada Center](https://www.mada.org.qa/) (مركز مدى), based in Qatar, works to
advance universal access and inclusion for persons with disabilities and older
people. Its programs support inclusive education, access to employment, and
participation in community life. Mada provides assistive technology services,
training, and accessibility consultancy, alongside research and the development
of Arabic accessibility resources and solutions.

Making international accessibility guidance available in Arabic supports this
work by helping organizations and practitioners understand and apply shared
standards. Read more about Mada's mission and services on its
[About Us page](https://www.mada.org.qa/about-us/).

## About AIAEG

The [Arab ICT Accessibility Expert Group (AIAEG)](https://aiaeg.mada.org.qa/)
— مجموعة الخبراء العرب في نفاذ تكنولوجيا المعلومات والاتصالات — is an initiative
from Mada that brings together expertise in ICT accessibility across the Arab
region. Its working groups support collaboration on Arabic resources,
terminology, and professional knowledge in accessibility and assistive technology.

AIAEG's published work includes the Arabic WCAG 2.1 translation working group,
Mada's accessibility and assistive technology glossary, and an ICT accessibility
and inclusive design competency framework. These resources provide context for
the continued development of Arabic accessibility guidance. The
[AIAEG members page](https://aiaeg.mada.org.qa/%d8%a7%d9%84%d8%a3%d8%b9%d8%b6%d8%a7%d8%a1/)
introduces the group's network; membership does not by itself indicate review or
approval of this WCAG 2.2 draft.

## The WCAG 2.2 Arabic translation initiative

This initiative aims to make WCAG 2.2 available to Arabic-speaking designers,
developers, content authors, accessibility evaluators, educators, and policy
teams. It builds on the terminology and unchanged wording of the
[published Arabic WCAG 2.1 translation](https://www.w3.org/Translations/WCAG21-ar/)
while translating the additions and revisions in the
[12 December 2024 WCAG 2.2 Recommendation](https://www.w3.org/TR/2024/REC-WCAG22-20241212/).

The repository provides a readable Arabic document, a shared terminology
register, and a complete English–Arabic comparison for passage-by-passage review.
The aim is to preserve the meaning and precision of the English requirements
and support consistent Arabic usage across accessibility practice. This WCAG 2.2
text remains a **review draft**; the published WCAG 2.1 translation's approval
does not extend to it.

### Take part in the review

- Read the [live Arabic draft](https://madainnovation.github.io/wcag.2.2.arabic.authorized.translation.by.mada/)
  alongside the [English–Arabic comparison](wcag22-ar/TRANSLATION-COMPARISON.md)
  and [terminology register](TERMINOLOGY.md).
- [Open an issue](https://github.com/madainnovation/wcag.2.2.arabic.authorized.translation.by.mada/issues)
  with the criterion number or section link, the English passage, the current
  Arabic text, and a suggested correction with its rationale. Feedback on
  readability, right-to-left presentation, and broken links is also welcome.
- For proposed edits, change the translation inputs described below and submit
  a pull request. Record deliberate changes to inherited wording in `REVIEW.md`.
- Consult the [W3C translators archive](https://lists.w3.org/Archives/Public/w3c-translators/)
  for public translation discussions.

## Project files

- `wcag22-ar/TRANSLATION-COMPARISON.md`: complete English–Arabic passages with
  review boxes. Change `[ ]` to `[x]` after confirming a row; rebuilding retains
  confirmations only for rows whose identifier and both passages are unchanged.
- `wcag22-ar/LINK-CHECK.md`: complete external HTTP link inventory and results,
  including confirmed 404s and destinations whose status could not be verified.
- `translation/changes.html`: new and revised Arabic passages.
- `translation/edits.json`: explicit changes to inherited Arabic wording.
- `translation/contributors.html`: bilingual WCAG 2.2 draft header, with the
  organization, contact details, and translation review links.
- `translation/rtl.css`: Arabic adaptations of the W3C template.
- `references/`: unmodified source snapshots and upstream template assets.
- `TERMINOLOGY.md`: bilingual terms and proposed new criterion titles.
- `REVIEW.md`: deliberate corrections, review priorities, and validation limits.
- `SOURCES.md`: source URLs and provenance.
- `reports/`: coverage, English source differences, and validation results.
- `scripts/build.py`: assembles the draft into the W3C English template.
- `publication.json`: public repository and current/latest HTML preview URLs.
- `.github/workflows/pages.yml`: builds, checks, and publishes `wcag22-ar/`
  through GitHub Pages on every push to `main`.
- `scripts/comparison.py`: exports the complete bilingual review file.
- `scripts/check_links.py`: checks external destinations in the portable files;
  `--reuse` reuses results checked within the last hour when updating the report.
- `scripts/check_layout.py`: compares selected CSS rules with the English
  template at seven screen widths and in print. This is a static CSS review,
  not a browser rendering or overflow measurement.
- `scripts/validate.py`: checks structure, links, levels, identifiers, notes,
  and selected numerical requirements against the English source.

## Rebuild

Requires Python 3.10 or later.

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/build.py
.venv/bin/python scripts/validate.py
```

Edit the translation inputs, then rebuild. Both `wcag22-ar/index.html` and the
root redirect `index.html`, plus the comparison Markdown file, are generated.
The build does not fetch or alter the
reference snapshots. Structural checks have passed; human linguistic review
and browser visual review remain outstanding.

## GitHub Pages

The repository's Pages source must be **GitHub Actions**. The publishing
workflow deploys the contents of `wcag22-ar/` as the site root, including the
local styles and review files. The workflow can also be started manually.
Pushes and Pages configuration require the corresponding repository access.
