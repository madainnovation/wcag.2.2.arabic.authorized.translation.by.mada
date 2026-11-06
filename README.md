# WCAG 2.2 Arabic translation

[GitHub repository](https://github.com/madainnovation/wcag.2.2.arabic.authorized.translation.by.mada)
· [Public HTML preview](https://madainnovation.github.io/wcag.2.2.arabic.authorized.translation.by.mada/)

The public preview is served by GitHub Pages after the first successful
deployment. Both version links in the translation header use this public URL.

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

## Project files

- `wcag22-ar/TRANSLATION-COMPARISON.md`: complete English–Arabic passages with
  review boxes. Change `[ ]` to `[x]` after confirming a row; rebuilding retains
  confirmations only for rows whose identifier and both passages are unchanged.
- `wcag22-ar/LINK-CHECK.md`: complete external HTTP link inventory and results,
  including confirmed 404s and destinations whose status could not be verified.
- `translation/changes.html`: new and revised Arabic passages.
- `translation/edits.json`: explicit changes to inherited Arabic wording.
- `translation/contributors.html`: credits for the published Arabic 2.1
  translation on which this draft builds, including historical contributor links.
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
