# Translation review record

Prepared on 6 November 2026. This document records the draft's provenance and
review status; it is not a statement of W3C approval or WCAG conformance of the
translation website.

## Translation approach

The published Arabic WCAG 2.1 translation supplies the inherited wording and
terminology. The target is the WCAG 2.2 Recommendation of 12 December 2024,
including its updated notes, glossary definitions, conformance material, and
change log. Inherited passages have not undergone a comprehensive linguistic
retranslation. Source-editor names and bibliography titles remain in their
original language, with appropriate language/direction markup.

New titles and terms in `TERMINOLOGY.md` are proposals. Particular review
attention is needed for “عدم حجب التركيز”, “مظهر التركيز”, “المصادقة القابلة للنفاذ”,
“اختبار الوظيفة الإدراكية”, and “المستطيل المحيط الأدنى”. The published titles
“مسار المؤشر” and “ظهور المؤشر” remain unchanged. New passages use “التركيز” and
“مؤشر التركيز” to distinguish keyboard focus from pointer input.

## Deliberate corrections to inherited material

These changes are explicit in the build inputs; the reference snapshots remain
untouched. They are proposed corrections for review, not retrospective changes
to the published 2.1 translation.

| Location | Draft correction and reason |
|---|---|
| 1.1.1, time-based media exception | Corrected the displayed cross-reference from “التوجيه 2.1” to “التوجيه 1.2”, matching its destination and the English source. |
| 1.4.10 Reflow | Clarified “without requiring scrolling in two dimensions”; the inherited Arabic could be read as prohibiting either direction independently. Updated both explanatory notes to the current source. |
| 1.4.13 Content on Hover or Focus | Restored the literal HTML `title` attribute name in the browser-tooltip note, added its current bibliography reference, and translated the added scope note. |
| 2.1.4 Character Key Shortcuts | Updated the remapping exception to “includes one or more non-printable keyboard keys”, following the revised English text. |
| 5.1 Interpreting Normative Requirements | Corrected the typo “يحب” to “يجب” for MUST. Used “يجوز” for MAY, “يجب ألا” for MUST NOT, “ينبغي” for SHOULD, and “ينبغي ألا” for SHOULD NOT to preserve normative force. English keyword labels remain available in the source markup. |
| 5.3.1 Required Components | Removed the obsolete editorial sentence about adjusting a dated URI, following the current English source. |
| 5.3.2 Optional Components | Changed “يجب تقديم” to “يمكن تقديم” for additional information, since the English source says it can be provided. |
| 5.3.2 Understanding Metadata link | Replaced the inherited `Understanding/appendixC` destination (confirmed HTTP 404) with `Understanding/understanding-metadata`, the destination in the pinned English 2.2 source (HTTP 200). |
| 5.4 Partial Conformance | Updated the opening paragraph to the current source. Clarified “best knowledge” and restored “يومي عمل” for “two business days”. |
| Glossary: large scale | Restored the distinction between 18-point text and 14-point **bold** text; the inherited opening sentence did not express it clearly. |
| Glossary: relative luminance | Restored complete R, G and B channel equations; the inherited HTML truncated the G and B formulas. Applied the current 0.04045 threshold, retained the historical-value note, and updated the reference. |
| Glossary: programmatically determined link context | Replaced “نفس القائمة” with “عنصر القائمة نفسه”, following “list item” in the current source. |
| Input purposes | Restored all 53 literal field identifiers plus inline identifiers and example protocol URLs from the English source. Descriptions remain Arabic. |

Other source-driven revisions include the orientation note, the additional
visual-presentation/text-spacing notes, changed definitions of single pointer,
target, changes of context, motion animation, and set of web pages, and the
current red-flash definition. The five new glossary definitions and all nine
new success criteria are included. The obsolete `encloses` definition is not
carried into 2.2.

## Template and markup handling

The final document is assembled inside a copy of the W3C English HTML template.
Source section classes, heading wrappers, contents markup and criterion-help
boxes are retained. The local W3C styles are supplemented by `translation-rtl.css`.
Only resource URLs in the copied base stylesheet are made local; upstream
snapshots remain unchanged.

The W3C template's blue status strip is mirrored onto the right edge and labelled
as an Arabic WCAG 2.2 draft. Source recommendation details and copyright remain attributed
to the English document. The previous translation's approval, coordinator,
reviewer list and date are not represented as approval of this translation.

### Arabic translation contributors

The bilingual translation header follows the structure of the published Arabic
2.1 reference and appears before the W3C English-template header. It credits
**Mada Center, Qatar / مركز مدى، قطر** and **Achraf Othman / أشرف عثمان**, with
the coordinator email, organization address,
review-committee link, translation-comments link, and translation-errata link.
The English block contains the title, lead organization, address, coordinator,
and contact email. The Arabic block contains the project title, draft status and
date, current/latest public draft links, pinned English source, errata link,
terminology note, organization/contact details, and committee and comments links.
The source's authorization statement and
2021 publication date are not reused as the status or date of this 2.2 draft.

At the project owner's latest request, the entire bilingual translation header
and its contents-list label refer only to **2.2**. Organization, coordinator,
committee, comments, and errata labels use 2.2; the separate 2.1 reference entry
has been removed from the header. This presentation does not claim W3C approval.
The address has been updated to the Ministry of Communications and Information
Technology wording supplied by the project owner, in Arabic and English. The
coordinator's name now includes “Dr.” / “د.”; the email remains unchanged.
The terminology notice uses
the existing register in place of the unavailable historical glossary website.
The committee uses the owner-provided AIAEG members address. Both comments and
errata now use the owner's replacement destination:
[the W3C translators archive](https://lists.w3.org/Archives/Public/w3c-translators/).
This is the general translation correspondence archive, not a claim that it is
a dedicated WCAG 2.2 errata register.

On 6 November 2026, the W3C Arabic 2.1 page returned HTTP 200. The historical
committee, comments and translation-errata links each returned HTTP 404. These
old destinations have been replaced in the reading document as described above.
At the user's request, the committee link now points to
[the Mada AIAEG members page](https://aiaeg.mada.org.qa/%d8%a7%d9%84%d8%a3%d8%b9%d8%b6%d8%a7%d8%a1/).
Its label no longer describes it as the historical published URL. The original
reference snapshot remains unchanged.
No individual committee membership has been inferred from unavailable pages.
The Mada site returned HTTP 403 to the earlier automated check and HTTP 200 in
the subsequent full link audit. The old Mada glossary hostname
could not be resolved. The address and title reflect the owner's supplied
updates; the email remains the address published in the source translation.

The W3C English specification editors and Appendix B contributor lists remain
as in the English 2.2 source. They are distinct from Arabic translation credits.

Broken nesting from the inherited Arabic HTML is repaired during assembly.
Notes and examples retain the classifications in the English 2.2 source,
including the changed classification of some glossary examples. Paragraph
examples are rendered as semantic containers that can hold the template's
example labels. Criterion and glossary anchors resolve locally.

Generated English ReSpec configuration, definition popovers, and runtime
scripts are omitted; glossary links remain ordinary working links. All display
assets are local. W3C help links and bibliography links remain external.

### Reading layout and browser annotation

The annotated introductory explanation and the added translation-process and
link-check notices remain absent from the reading document. At the owner's
subsequent request, the bilingual translation header has been restored with the
published 2.1 layout: a shaded bordered box, an English block followed by an
Arabic block, and definition-list metadata. It identifies the document as a
dated review draft and includes the requested organization and resource labels.
The English source's own status text remains in the W3C header and body.

The RTL stylesheet replaces off-canvas separator positioning with a clipped
one-pixel box; the inherited `left: -10000px` can enlarge an RTL scroll area.
Contents numbers now occupy a separate right-hand column without floats or
negative margins. Headings isolate decimal numbers from Arabic labels, and
permalink anchors stay in normal flow. Logical list indentation also respects
the English bibliography blocks. Narrow windows wrap the help boxes and URLs.

The spacing review restores the pinned English template's 1.5 body line height,
50em content column, 1em paragraph margins, 3rem section-heading top margins,
half-em note/example padding, and two-em list/definition indentation. Arabic
headings use 1.3 line height, slightly above the source's 1.2. The logo floats
left; the right gutter reserves the same 26px strip clearance as the English
template. The contents sidebar follows the source's 78em breakpoint and 29em
body clearance, mirrored to the right. The strip is 25 × 380px, as in the source,
and hidden in print; it identifies a draft rather than asserting W3C approval.

`scripts/check_layout.py` compares winning CSS declarations at viewport widths
320, 390, 768, 1159, 1248, 1440, and 1920 pixels, plus print. Its report is
`reports/layout-validation.json`. The review covers selectors and the cascade
in the default light state with a 16px initial em; it is not a browser layout or
font-shaping test. Local browser use was attempted again and remains disabled
in Work settings, so visual verification and measured overflow remain pending.

List markup was restored to the English source: the supporting-documents list
is numbered and its final two resources are separate items; glossary entries
for changes of context, flash thresholds, and structure use bullets. This is
a presentation correction to inherited/draft markup, not a change in normative
wording. All source list types and item counts are checked.

### English–Arabic review file

`wcag22-ar/TRANSLATION-COMPARISON.md` includes every section and glossary entry,
publication details, navigation labels, help labels, and Arabic-only credits.
Rows pair individual headings, paragraphs, list items, notes, and examples.
When a paragraph was split or combined in translation, the matching passage
stays together. Two inherited glossary example-nesting differences are grouped
in the exporter without altering, omitting, or reordering their text.

The exporter checks complete text coverage and order within each unit. A separate
whole-document text accounting check guards against omitted units. Review boxes
start empty. Rebuilding preserves a checked box only if its identifier and both
passages remain unchanged. These boxes record the reviewer's confirmation; the
export itself does not establish linguistic accuracy.

### External link audit

`wcag22-ar/LINK-CHECK.md` records the HTTP result for every distinct external
destination found in the HTML and accompanying review documents. The audit uses
GET, follows redirects, and retries 404 and connection/server failures once.
URLs that differ only by a fragment share a page request; remote fragment
targets are outside the HTTP-status check. Email links are not contacted.
Reserved example-domain strings in the WCAG examples are listed separately,
preserving the source examples without counting them as broken resource links.

The initial HTML audit found three 404 destinations. The obsolete metadata
appendix link has been corrected from the English source. Translation comments
and errata now point to the W3C translators archive provided by the owner.
ISO and UNESCO returned HTTP 403 challenge pages;
their availability remains unverified, and they are not classified as 404s.
The AIAEG committee page and the Mada home page returned HTTP 200.
The initial and final machine-readable results are retained in
`reports/external-links-before-fixes.json` and `reports/external-links.json`.

### Public preview

The current/latest header links now point to the repository's GitHub Pages URL
from `publication.json`. The publication workflow builds and validates the
document before deploying only the portable `wcag22-ar/` folder. A successful
local build does not establish that the public site is live; the Pages deployment
and HTTP response must be checked separately. Existing link-audit timestamps
remain the dates those destinations were checked.

## Verification and remaining review

The automated validation checks include:

- HTML5 parsing without errors; unique IDs; all internal links resolve.
- All 140 sections in source order with the original nesting and numbering.
- All 86 active criteria and their exact conformance levels; nine new criteria;
  4.1.1 classified as removed with an informative note.
- All 101 glossary definitions; source-matching note/example counts.
- All input-purpose identifiers and criterion-help URLs preserved.
- Selected critical values and exceptions: target size, focus contrast,
  authentication exceptions, luminance formulas, and red-flash thresholds.

Browser visual inspection could not be performed because browser access is
disabled in the app settings. Desktop/mobile layout, keyboard interaction,
screen-reader reading order, print layout, and visual presentation of mixed
Arabic/Latin text therefore require a browser review. No conformance claim is
made for the document's presentation.

A human review of linguistic accuracy and normative meaning remains necessary,
especially for new criteria, exceptions, mathematical definitions, and inherited
terminology that varies within the 2.1 translation. Automated checks establish
structural coverage and selected invariants; they do not establish complete
translation accuracy or W3C authorization.
