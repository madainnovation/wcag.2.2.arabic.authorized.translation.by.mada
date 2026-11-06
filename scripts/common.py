"""Extraction helpers for the pinned W3C source snapshots."""
from pathlib import Path
import copy
import re
from bs4 import BeautifulSoup, Tag

ROOT = Path(__file__).resolve().parents[1]


def soup(text):
    return BeautifulSoup(text, "html.parser")


def source(name):
    return soup((ROOT / "references" / f"{name}.html").read_text())


def text(node):
    return " ".join(node.get_text(" ", strip=True).split())


def previous_id(ident):
    return {"comparison-with-wcag-2-1": "comparison-with-wcag-2-0",
            "target-size-enhanced": "target-size",
            "acknowledgements": "acknowledgments",
            "dfn-targets": "dfn-target",
            "dfn-conforming-alternate-versions": "dfn-conforming-alternate-version"}.get(
                ident, ident.replace("wcag-2-2", "wcag-2-1"))


def heading(section):
    return section.find(re.compile(r"^h[2-6]$"))


def title(h):
    h = copy.deepcopy(h)
    for tag in h.select(".secno,.section-label,.permalink"):
        tag.decompose()
    return re.sub(r"^[\d.\s]+", "", text(h))


def own(h):
    """Extract a heading's body, stopping before subsections.

    Heading boundaries recover the malformed section nesting in the published
    Arabic 2.1 HTML without changing any translated paragraphs.
    """
    if h.parent.get("class") == ["header-wrapper"]:
        h = h.parent
    elif h.parent.name == "a":
        h = h.parent
    parts = []
    for tag in h.next_siblings:
        if not isinstance(tag, Tag):
            continue
        if tag.name == "section" or re.fullmatch(r"h[1-6]", tag.name):
            break
        if set(tag.get("class", [])) & {"doclinks", "conformance-level", "sc-wcag21", "sc-wcag22"}:
            continue
        parts.append(str(tag))
    return "\n".join(parts)


def glossary_entry(dfn):
    dt = dfn.find_parent("dt")
    dd = dt.find_next_sibling("dd")
    if dd is None:
        raise ValueError(f"Missing definition: {dfn.get('id')}")
    return dt, dd
