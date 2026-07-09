#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html as html_lib
import re
import shutil
import unicodedata
import uuid
import zipfile
from copy import deepcopy
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import quote, urljoin, urlsplit, urlunsplit

from lxml import etree, html
from PIL import Image, ImageDraw, ImageFont


LANGUAGE_CONFIGS = {
    "en": {
        "source_url": "https://www.vatican.va/content/leo-xiv/en/encyclicals/documents/20260515-magnifica-humanitas.html",
        "source_html": Path("vatican-magnifica-humanitas.source.html"),
        "build_dir": Path("build/magnifica-humanitas-epub-en"),
        "output_epub": Path("Magnifica Humanitas - Pope Leo XIV.epub"),
        "title": "Magnifica Humanitas",
        "subtitle": "On Safeguarding the Human Person in the Time of Artificial Intelligence",
        "author": "Pope Leo XIV",
        "publisher": "The Holy See",
        "date": "2026-05-15",
        "cover_kicker": "ENCYCLICAL LETTER",
        "cover_date": "15 MAY 2026",
        "title_page_label": "ENCYCLICAL LETTER",
        "title_page_nav": "Title Page",
        "contents_label": "Contents",
        "notes_label": "Notes",
        "start_anchors": ("INTRODUCTION_",),
        "top_level_pattern": r"^(INTRODUCTION|CHAPTER [A-Z]+|CONCLUSION)$",
    },
    "fr": {
        "source_url": "https://www.vatican.va/content/leo-xiv/fr/encyclicals/documents/20260515-magnifica-humanitas.html",
        "source_html": Path("vatican-magnifica-humanitas.fr.source.html"),
        "build_dir": Path("build/magnifica-humanitas-epub-fr"),
        "output_epub": Path("Magnifica Humanitas - Pape Leon XIV (fr).epub"),
        "title": "Magnifica Humanitas",
        "subtitle": "Sur la protection de la personne humaine à l’ère de l’intelligence artificielle",
        "author": "Pape Léon XIV",
        "publisher": "Le Saint-Siège",
        "date": "2026-05-15",
        "cover_kicker": "LETTRE ENCYCLIQUE",
        "cover_date": "15 MAI 2026",
        "title_page_label": "LETTRE ENCYCLIQUE",
        "title_page_nav": "Page de titre",
        "contents_label": "Sommaire",
        "notes_label": "Notes",
        "start_anchors": ("INTRODUCTION",),
        "top_level_pattern": r"^(INTRODUCTION|Chapitre\s+\d+|CONCLUSION)$",
    },
    "it": {
        "source_url": "https://www.vatican.va/content/leo-xiv/it/encyclicals/documents/20260515-magnifica-humanitas.html",
        "source_html": Path("vatican-magnifica-humanitas.it.source.html"),
        "build_dir": Path("build/magnifica-humanitas-epub-it"),
        "output_epub": Path("Magnifica Humanitas - Papa Leone XIV (it).epub"),
        "title": "Magnifica Humanitas",
        "subtitle": "Sulla custodia della persona umana nel tempo dell'intelligenza artificiale",
        "author": "Papa Leone XIV",
        "publisher": "La Santa Sede",
        "date": "2026-05-15",
        "cover_kicker": "LETTERA ENCICLICA",
        "cover_date": "15 MAGGIO 2026",
        "title_page_label": "LETTERA ENCICLICA",
        "title_page_nav": "Pagina del titolo",
        "contents_label": "Indice",
        "notes_label": "Note",
        "start_anchors": ("INTRODUZIONE",),
        "top_level_pattern": r"^(INTRODUZIONE|CAPITOLO\s+\d+|CONCLUSIONE)$",
    },
    "pt": {
        "source_url": "https://www.vatican.va/content/leo-xiv/pt/encyclicals/documents/20260515-magnifica-humanitas.html",
        "source_html": Path("vatican-magnifica-humanitas.pt.source.html"),
        "build_dir": Path("build/magnifica-humanitas-epub-pt"),
        "output_epub": Path("Magnifica Humanitas - Papa Leao XIV (pt).epub"),
        "title": "Magnifica Humanitas",
        "subtitle": "Sobre a salvaguarda da pessoa humana na era da inteligência artificial",
        "author": "Papa Leão XIV",
        "publisher": "A Santa Sé",
        "date": "2026-05-15",
        "cover_kicker": "CARTA ENCÍCLICA",
        "cover_date": "15 DE MAIO DE 2026",
        "title_page_label": "CARTA ENCÍCLICA",
        "title_page_nav": "Página de rosto",
        "contents_label": "Índice",
        "notes_label": "Notas",
        "start_anchors": ("Introdução",),
        "top_level_pattern": r"^(INTRODUÇÃO|CAPÍTULO [IVXLCDM]+|CONCLUSÃO)$",
    },
    "pl": {
        "source_url": "https://www.vatican.va/content/leo-xiv/pl/encyclicals/documents/20260515-magnifica-humanitas.html",
        "source_html": Path("vatican-magnifica-humanitas.pl.source.html"),
        "build_dir": Path("build/magnifica-humanitas-epub-pl"),
        "output_epub": Path("Magnifica Humanitas - Pope Leo XIV (pl).epub"),
        "title": "Magnifica Humanitas",
        "subtitle": "O trosce o osobę ludzką w dobie sztucznej inteligencji",
        "author": "Papież Leon XIV",
        "publisher": "Stolica Apostolska",
        "date": "2026-05-15",
        "cover_kicker": "ENCYKLIKA",
        "cover_date": "15 MAJA 2026",
        "title_page_label": "ENCYKLIKA",
        "title_page_nav": "Strona tytułowa",
        "contents_label": "Treść",
        "notes_label": "Notatki",
        "start_anchors": ("WPROWADZENIE_",),
        "top_level_pattern": r"^(WPROWADZENIE|ROZDZIAŁ [A-Z]+|ZAKOŃCZENIE)$",
    },
}

SOURCE_URL = ""
SOURCE_HTML = Path()
BUILD_DIR = Path()
OUTPUT_EPUB = Path()

TITLE = ""
SUBTITLE = ""
AUTHOR = ""
PUBLISHER = ""
DATE = ""
LANG = ""
COVER_KICKER = ""
COVER_DATE = ""
TITLE_PAGE_LABEL = ""
TITLE_PAGE_NAV = ""
CONTENTS_LABEL = ""
NOTES_LABEL = ""
START_ANCHORS: tuple[str, ...] = ()
TOP_LEVEL_PATTERN = re.compile("")


def set_language(lang: str) -> None:
    config = LANGUAGE_CONFIGS[lang]
    globals().update(
        SOURCE_URL=config["source_url"],
        SOURCE_HTML=config["source_html"],
        BUILD_DIR=config["build_dir"],
        OUTPUT_EPUB=config["output_epub"],
        TITLE=config["title"],
        SUBTITLE=config["subtitle"],
        AUTHOR=config["author"],
        PUBLISHER=config["publisher"],
        DATE=config["date"],
        LANG=lang,
        COVER_KICKER=config["cover_kicker"],
        COVER_DATE=config["cover_date"],
        TITLE_PAGE_LABEL=config["title_page_label"],
        TITLE_PAGE_NAV=config["title_page_nav"],
        CONTENTS_LABEL=config["contents_label"],
        NOTES_LABEL=config["notes_label"],
        START_ANCHORS=config["start_anchors"],
        TOP_LEVEL_PATTERN=re.compile(str(config["top_level_pattern"]), re.IGNORECASE),
    )


def normspace(value: str) -> str:
    value = value.replace("\xa0", " ")
    return re.sub(r"\s+", " ", value).strip()


def escape(value: str) -> str:
    return html_lib.escape(value, quote=True)


def safe_id(value: str, used: set[str]) -> str:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    normalized = re.sub(r"[^A-Za-z0-9_-]+", "_", normalized).strip("_")
    normalized = normalized or "section"
    if normalized[0].isdigit():
        normalized = f"id_{normalized}"

    candidate = normalized
    i = 2
    while candidate in used:
        candidate = f"{normalized}_{i}"
        i += 1
    used.add(candidate)
    return candidate


def any_ancestor_tag(element: etree._Element, tag_name: str) -> bool:
    return any(isinstance(ancestor.tag, str) and ancestor.tag.lower() == tag_name for ancestor in element.iterancestors())


def remove_preserving_tail(parent: etree._Element, child: etree._Element) -> None:
    tail = child.tail
    previous = child.getprevious()
    parent.remove(child)
    if tail:
        if previous is not None:
            previous.tail = (previous.tail or "") + tail
        else:
            parent.text = (parent.text or "") + tail


def build_id_map(content: etree._Element) -> dict[str, str]:
    used: set[str] = set()
    ids: dict[str, str] = {}
    for anchor in content.xpath(".//a[@name]"):
        old = anchor.get("name")
        if old and old not in ids:
            ids[old] = safe_id(old, used)
    return ids


def extract_toc_levels(content: etree._Element, id_map: dict[str, str]) -> dict[str, int]:
    levels: dict[str, int] = {}
    for paragraph in content.xpath("./p"):
        if any(paragraph.xpath(f'.//a[@name="{anchor}"]') for anchor in START_ANCHORS):
            break

        for anchor in paragraph.xpath('.//a[@href and starts-with(@href, "#")]'):
            href = anchor.get("href", "")
            old_id = href[1:]
            if old_id.startswith("_ftn") or old_id not in id_map:
                continue

            text = normspace(anchor.text_content())
            if not text:
                continue

            if TOP_LEVEL_PATTERN.match(text):
                level = 1
            elif any_ancestor_tag(anchor, "i"):
                level = 3
            else:
                level = 2

            levels.setdefault(id_map[old_id], level)
    return levels


def sanitize_element(element: etree._Element, id_map: dict[str, str]) -> etree._Element:
    cleaned = deepcopy(element)

    def clean(node: etree._Element) -> None:
        if not isinstance(node.tag, str):
            return

        tag = node.tag.lower()
        if tag == "b":
            node.tag = "strong"
        elif tag == "i":
            node.tag = "em"

        if node.text:
            node.text = node.text.replace("\xa0", " ")
        if node.tail:
            node.tail = node.tail.replace("\xa0", " ")

        for child in list(node):
            if not isinstance(child.tag, str):
                remove_preserving_tail(node, child)
                continue
            clean(child)

        original_style = node.get("style", "")
        name = node.get("name")
        href = node.get("href")
        text_align_center = "text-align: center" in original_style.lower()

        for attr in list(node.attrib):
            del node.attrib[attr]

        if name:
            node.set("id", id_map.get(name, name))

        if node.tag == "a" and href:
            if href.startswith("#"):
                node.set("href", f"#{id_map.get(href[1:], href[1:])}")
            else:
                external_href = urljoin(SOURCE_URL, href).replace("http://www.vatican.va", "https://www.vatican.va")
                parts = urlsplit(external_href)
                node.set("href", urlunsplit((parts.scheme, parts.netloc, parts.path, parts.query, quote(parts.fragment, safe="/"))))

        if text_align_center and node.tag in {"p", "div"}:
            node.set("class", "center")

    clean(cleaned)
    return cleaned


def heading_from_paragraph(
    paragraph: etree._Element,
    id_map: dict[str, str],
    toc_levels: dict[str, int],
) -> tuple[etree._Element | None, dict[str, str | int] | None]:
    anchors = paragraph.xpath('.//a[@name and not(starts-with(@name, "_ftn"))]')
    if not anchors:
        return None, None

    old_id = anchors[0].get("name")
    if not old_id:
        return None, None

    new_id = id_map.get(old_id, old_id)
    text = normspace(paragraph.text_content())
    if not text or len(text) > 220:
        return None, None

    is_heading = new_id in toc_levels or bool(paragraph.xpath(".//b")) or "text-align: center" in paragraph.get("style", "").lower()
    if not is_heading:
        return None, None

    level = toc_levels.get(new_id, 2)
    tag = "h1" if level <= 1 else "h2" if level == 2 else "h3"
    heading = etree.Element(tag)
    heading.set("id", new_id)
    heading.text = text
    return heading, {"id": new_id, "text": text, "level": level}


def serialize_element(element: etree._Element) -> str:
    return etree.tostring(element, encoding="unicode", method="xml", with_tail=False)


def build_content_fragments(content: etree._Element, id_map: dict[str, str], toc_levels: dict[str, int]) -> tuple[list[str], list[str], list[dict[str, str | int]]]:
    children = list(content)
    start_index = None
    for i, child in enumerate(children):
        if isinstance(child.tag, str) and any(child.xpath(f'.//a[@name="{anchor}"]') for anchor in START_ANCHORS):
            start_index = i
            break
    if start_index is None:
        raise RuntimeError("Could not find the start of the encyclical body.")

    body: list[str] = []
    notes: list[str] = []
    toc_entries: list[dict[str, str | int]] = []

    for child in children[start_index:]:
        if not isinstance(child.tag, str):
            continue

        footnote_paragraphs = []
        if child.tag.lower() == "p" and child.xpath('.//a[starts-with(@name, "_ftn") and not(starts-with(@name, "_ftnref"))]'):
            footnote_paragraphs.append(child)
        footnote_paragraphs.extend(
            child.xpath('.//p[contains(concat(" ", normalize-space(@class), " "), " MsoFootnoteText ") or .//a[starts-with(@name, "_ftn") and not(starts-with(@name, "_ftnref"))]]')
        )
        if footnote_paragraphs:
            for paragraph in footnote_paragraphs:
                cleaned = sanitize_element(paragraph, id_map)
                cleaned.set("class", "footnote")
                if normspace(cleaned.text_content()):
                    notes.append(serialize_element(cleaned))
            continue

        if child.tag.lower() == "hr":
            continue

        if child.tag.lower() == "p" and not normspace(child.text_content()):
            continue

        heading, toc_entry = heading_from_paragraph(child, id_map, toc_levels)
        if heading is not None and toc_entry is not None:
            body.append(serialize_element(heading))
            if not str(toc_entry["id"]).startswith("ftn"):
                toc_entries.append(toc_entry)
            continue

        cleaned = sanitize_element(child, id_map)
        if cleaned.tag.lower() == "p" and not normspace(cleaned.text_content()):
            continue
        body.append(serialize_element(cleaned))

    return body, notes, toc_entries


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Georgia Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Georgia.ttf",
        "/System/Library/Fonts/Supplemental/Times New Roman Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Times New Roman.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
    ]
    for candidate in candidates:
        path = Path(candidate)
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font_obj: ImageFont.ImageFont, max_width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        bbox = draw.textbbox((0, 0), candidate, font=font_obj)
        if bbox[2] - bbox[0] <= max_width or not current:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_centered_lines(
    draw: ImageDraw.ImageDraw,
    lines: list[str],
    font_obj: ImageFont.ImageFont,
    y: int,
    fill: str,
    line_gap: int,
    width: int,
) -> int:
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font_obj)
        x = (width - (bbox[2] - bbox[0])) // 2
        draw.text((x, y), line, font=font_obj, fill=fill)
        y += (bbox[3] - bbox[1]) + line_gap
    return y


def create_cover(path: Path) -> None:
    width, height = 1600, 2400
    image = Image.new("RGB", (width, height), "#f7f1e6")
    draw = ImageDraw.Draw(image)
    burgundy = "#6d1726"
    graphite = "#262626"
    gold = "#b9965d"

    margin = 110
    draw.rectangle((margin, margin, width - margin, height - margin), outline=burgundy, width=8)
    draw.rectangle((margin + 32, margin + 32, width - margin - 32, height - margin - 32), outline=gold, width=3)

    y = 360
    y = draw_centered_lines(draw, [COVER_KICKER], font(54), y, graphite, 18, width)
    y += 120
    y = draw_centered_lines(draw, ["MAGNIFICA", "HUMANITAS"], font(126, bold=True), y, burgundy, 34, width)
    y += 120
    subtitle_lines = wrap_text(draw, SUBTITLE.upper(), font(48), width - 360)
    y = draw_centered_lines(draw, subtitle_lines, font(48), y, graphite, 22, width)
    y += 190
    draw.line((width // 2 - 210, y, width // 2 + 210, y), fill=gold, width=6)
    y += 110
    y = draw_centered_lines(draw, [AUTHOR.upper()], font(58, bold=True), y, graphite, 18, width)
    y += 48
    draw_centered_lines(draw, [COVER_DATE], font(44), y, graphite, 14, width)

    image.save(path, "PNG", optimize=True)


def make_xhtml(title: str, body: str, css_href: str = "../styles/book.css") -> str:
    return f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="{LANG}" lang="{LANG}">
<head>
  <meta charset="utf-8" />
  <title>{escape(title)}</title>
  <link rel="stylesheet" type="text/css" href="{escape(css_href)}" />
</head>
<body>
{body}
</body>
</html>
"""


def render_nav_tree(entries: list[dict[str, str | int]]) -> str:
    root: list[dict[str, object]] = []
    stack: list[tuple[int, list[dict[str, object]]]] = [(0, root)]

    for entry in entries:
        level = int(entry.get("level", 1))
        level = max(1, min(level, 3))
        while stack and level <= stack[-1][0]:
            stack.pop()
        node: dict[str, object] = {
            "href": entry["href"],
            "text": entry["text"],
            "children": [],
        }
        stack[-1][1].append(node)
        stack.append((level, node["children"]))  # type: ignore[arg-type]

    def render(nodes: list[dict[str, object]]) -> str:
        items = ["<ol>"]
        for node in nodes:
            items.append(f'<li><a href="{escape(str(node["href"]))}">{escape(str(node["text"]))}</a>')
            children = node["children"]
            if children:
                items.append(render(children))  # type: ignore[arg-type]
            items.append("</li>")
        items.append("</ol>")
        return "\n".join(items)

    return render(root)


def write_epub_files(body_fragments: list[str], notes: list[str], toc_entries: list[dict[str, str | int]]) -> None:
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)

    (BUILD_DIR / "META-INF").mkdir(parents=True)
    (BUILD_DIR / "OEBPS" / "text").mkdir(parents=True)
    (BUILD_DIR / "OEBPS" / "styles").mkdir(parents=True)
    (BUILD_DIR / "OEBPS" / "images").mkdir(parents=True)

    (BUILD_DIR / "mimetype").write_text("application/epub+zip", encoding="utf-8")
    (BUILD_DIR / "META-INF" / "container.xml").write_text(
        """<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml" />
  </rootfiles>
</container>
""",
        encoding="utf-8",
    )

    create_cover(BUILD_DIR / "OEBPS" / "images" / "cover.png")

    css = """
body {
  font-family: Georgia, "Times New Roman", serif;
  line-height: 1.45;
  margin: 5%;
  color: #1f1f1f;
}
a {
  color: #6d1726;
  text-decoration: none;
}
h1, h2, h3 {
  font-family: Georgia, "Times New Roman", serif;
  color: #5f1320;
  line-height: 1.2;
  margin-top: 1.6em;
}
h1 {
  font-size: 1.7em;
  text-align: center;
}
h2 {
  font-size: 1.3em;
}
h3 {
  font-size: 1.08em;
  font-style: italic;
}
p {
  margin: 0 0 0.85em;
  text-align: justify;
}
.center {
  text-align: center;
}
.title-page {
  text-align: center;
  margin-top: 18%;
}
.title-page p {
  text-align: center;
}
.book-title {
  font-size: 2.2em;
  color: #5f1320;
  margin: 0.6em 0 0.2em;
}
.subtitle {
  font-size: 1.1em;
}
.source {
  font-size: 0.85em;
  margin-top: 3em;
}
.footnote {
  font-size: 0.88em;
  text-align: left;
}
#notes {
  border-top: 1px solid #b9965d;
  margin-top: 2em;
  padding-top: 1em;
}
img.cover {
  display: block;
  height: auto;
  margin: 0 auto;
  max-width: 100%;
}
""".strip()
    (BUILD_DIR / "OEBPS" / "styles" / "book.css").write_text(css + "\n", encoding="utf-8")

    cover_body = f'<section class="cover"><img class="cover" src="../images/cover.png" alt="{escape(TITLE)} cover" /></section>'
    (BUILD_DIR / "OEBPS" / "text" / "cover.xhtml").write_text(make_xhtml("Cover", cover_body), encoding="utf-8")

    title_body = f"""
<section class="title-page">
  <p>{escape(TITLE_PAGE_LABEL)}</p>
  <h1 class="book-title">{escape(TITLE)}</h1>
  <p class="subtitle">{escape(SUBTITLE)}</p>
  <p>{escape(AUTHOR)}</p>
  <p>{escape(DATE)}</p>
  <p class="source">Source: <a href="{escape(SOURCE_URL)}">{escape(PUBLISHER)}</a></p>
</section>
""".strip()
    (BUILD_DIR / "OEBPS" / "text" / "title.xhtml").write_text(make_xhtml(TITLE, title_body), encoding="utf-8")

    notes_section = ""
    if notes:
        notes_section = f"""
<section id="notes" epub:type="footnotes">
  <h1>{escape(NOTES_LABEL)}</h1>
  {"\n  ".join(notes)}
</section>
""".strip()

    content_body = f"""
<section id="encyclical">
  {"\n  ".join(body_fragments)}
</section>
{notes_section}
""".strip()
    (BUILD_DIR / "OEBPS" / "text" / "content.xhtml").write_text(make_xhtml(TITLE, content_body), encoding="utf-8")

    nav_entries = [
        {"href": "text/title.xhtml", "text": TITLE_PAGE_NAV, "level": 1},
        *[
            {
                "href": f'text/content.xhtml#{entry["id"]}',
                "text": str(entry["text"]),
                "level": int(entry["level"]),
            }
            for entry in toc_entries
        ],
    ]
    if notes:
        nav_entries.append({"href": "text/content.xhtml#notes", "text": NOTES_LABEL, "level": 1})

    nav_body = f"""
<nav epub:type="toc" id="toc">
  <h1>{escape(CONTENTS_LABEL)}</h1>
  {render_nav_tree(nav_entries)}
</nav>
""".strip()
    (BUILD_DIR / "OEBPS" / "nav.xhtml").write_text(make_xhtml("Contents", nav_body, "styles/book.css"), encoding="utf-8")

    ncx_points = []
    play_order = 1
    for entry in nav_entries:
        ncx_points.append(
            f"""    <navPoint id="navPoint-{play_order}" playOrder="{play_order}">
      <navLabel><text>{escape(str(entry["text"]))}</text></navLabel>
      <content src="{escape(str(entry["href"]))}" />
    </navPoint>"""
        )
        play_order += 1

    identifier = f"urn:uuid:{uuid.uuid5(uuid.NAMESPACE_URL, SOURCE_URL)}"
    (BUILD_DIR / "OEBPS" / "toc.ncx").write_text(
        f"""<?xml version="1.0" encoding="UTF-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
  <head>
    <meta name="dtb:uid" content="{identifier}" />
    <meta name="dtb:depth" content="3" />
    <meta name="dtb:totalPageCount" content="0" />
    <meta name="dtb:maxPageNumber" content="0" />
  </head>
  <docTitle><text>{escape(TITLE)}</text></docTitle>
  <docAuthor><text>{escape(AUTHOR)}</text></docAuthor>
  <navMap>
{"\n".join(ncx_points)}
  </navMap>
</ncx>
""",
        encoding="utf-8",
    )

    (BUILD_DIR / "OEBPS" / "content.opf").write_text(
        f"""<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="bookid" xml:lang="{LANG}">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="bookid">{identifier}</dc:identifier>
    <dc:title>{escape(TITLE)}</dc:title>
    <dc:creator>{escape(AUTHOR)}</dc:creator>
    <dc:language>{LANG}</dc:language>
    <dc:publisher>{escape(PUBLISHER)}</dc:publisher>
    <dc:date>{DATE}</dc:date>
    <dc:source>{escape(SOURCE_URL)}</dc:source>
    <dc:description>{escape(SUBTITLE)}</dc:description>
    <meta property="dcterms:modified">2026-05-25T00:00:00Z</meta>
    <meta name="cover" content="cover-image" />
  </metadata>
  <manifest>
    <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav" />
    <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml" />
    <item id="style" href="styles/book.css" media-type="text/css" />
    <item id="cover-image" href="images/cover.png" media-type="image/png" properties="cover-image" />
    <item id="cover" href="text/cover.xhtml" media-type="application/xhtml+xml" />
    <item id="title-page" href="text/title.xhtml" media-type="application/xhtml+xml" />
    <item id="content" href="text/content.xhtml" media-type="application/xhtml+xml" />
  </manifest>
  <spine toc="ncx">
    <itemref idref="cover" />
    <itemref idref="title-page" />
    <itemref idref="content" />
  </spine>
</package>
""",
        encoding="utf-8",
    )


def create_epub() -> None:
    if OUTPUT_EPUB.exists():
        OUTPUT_EPUB.unlink()

    with zipfile.ZipFile(OUTPUT_EPUB, "w") as epub:
        epub.write(BUILD_DIR / "mimetype", "mimetype", compress_type=zipfile.ZIP_STORED)
        for path in sorted(BUILD_DIR.rglob("*")):
            if path.is_dir() or path.name == "mimetype":
                continue
            epub.write(path, path.relative_to(BUILD_DIR).as_posix(), compress_type=zipfile.ZIP_DEFLATED)


def validate_xml() -> None:
    parser = etree.XMLParser(resolve_entities=False, no_network=True)
    for path in [
        BUILD_DIR / "META-INF" / "container.xml",
        BUILD_DIR / "OEBPS" / "content.opf",
        BUILD_DIR / "OEBPS" / "toc.ncx",
        BUILD_DIR / "OEBPS" / "nav.xhtml",
        BUILD_DIR / "OEBPS" / "text" / "cover.xhtml",
        BUILD_DIR / "OEBPS" / "text" / "title.xhtml",
        BUILD_DIR / "OEBPS" / "text" / "content.xhtml",
    ]:
        etree.parse(str(path), parser)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a Magnifica Humanitas EPUB from the Vatican HTML.")
    parser.add_argument("--lang", choices=sorted(LANGUAGE_CONFIGS), default="en", help="Vatican language version to package")
    args = parser.parse_args()
    set_language(args.lang)

    if not SOURCE_HTML.exists():
        request = Request(SOURCE_URL, headers={"User-Agent": "magnifica-humanitas-epub/1.0"})
        with urlopen(request, timeout=30) as response:
            SOURCE_HTML.write_bytes(response.read())

    document = html.parse(str(SOURCE_HTML))
    root = document.getroot()
    content_nodes = root.xpath('//*[contains(concat(" ", normalize-space(@class), " "), " documento ")]//*[contains(concat(" ", normalize-space(@class), " "), " vaticanrichtext ") and contains(concat(" ", normalize-space(@class), " "), " text ")][2]')
    if not content_nodes:
        raise RuntimeError("Could not find the Vatican document text.")

    content = content_nodes[0]
    id_map = build_id_map(content)
    toc_levels = extract_toc_levels(content, id_map)
    body_fragments, notes, toc_entries = build_content_fragments(content, id_map, toc_levels)

    write_epub_files(body_fragments, notes, toc_entries)
    validate_xml()
    create_epub()

    print(f"Wrote {OUTPUT_EPUB}")
    print(f"Body fragments: {len(body_fragments)}")
    print(f"Notes: {len(notes)}")
    print(f"TOC entries: {len(toc_entries)}")


if __name__ == "__main__":
    main()
