"""Baut die Beispieldateien in diesem Verzeichnis neu.

Aufruf aus ``backend/``::

    python tests/fixtures/build_fixtures.py

Alle Inhalte entstehen hier, nichts stammt aus fremden Quellen. Jede Datei traegt
den Baustein ``Kaimarkit Fixture``; darauf verlassen sich die Smoketests in
``tests/test_converters.py``.

Sieben der neun Dateien baut die Standardbibliothek. Nur ``tabelle.xlsx`` braucht
openpyxl und ``bild.png`` Pillow; beide kommen mit ``markitdown[all]`` ohnehin in die
Entwicklungsumgebung.
"""

from __future__ import annotations

import zipfile
from pathlib import Path

HERE = Path(__file__).parent

#: Der Baustein, auf den sich jeder Smoketest verlaesst.
MARKER = "Kaimarkit Fixture"

#: Zeilen der Tabelle in tabelle.pdf und tabelle.xlsx.
TABLE = [
    ["Format", "Engine"],
    ["pdf", "docling"],
    ["odt", "pandoc"],
]


def build_html() -> None:
    (HERE / "seite.html").write_text(
        "<!doctype html>\n"
        '<html lang="de">\n'
        '<head><meta charset="utf-8"><title>Kaimarkit Fixture</title></head>\n'
        "<body>\n"
        "<h1>Kaimarkit Fixture</h1>\n"
        "<p>Eine Seite aus dem Fixturebestand.</p>\n"
        "</body>\n"
        "</html>\n",
        encoding="utf-8",
    )


def build_csv() -> None:
    (HERE / "liste.csv").write_text(
        "Format,Zweck\ncsv,Kaimarkit Fixture\nhtml,Zweite Zeile\n", encoding="utf-8"
    )


def build_docx() -> None:
    content_types = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Default Extension="rels"'
        ' ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Override PartName="/word/document.xml" ContentType="application/vnd.'
        'openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
        "</Types>"
    )
    rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006'
        '/relationships/officeDocument" Target="word/document.xml"/></Relationships>'
    )
    document = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        "<w:body>"
        '<w:p><w:pPr><w:pStyle w:val="Heading1"/></w:pPr>'
        f"<w:r><w:t>{MARKER}</w:t></w:r></w:p>"
        "<w:p><w:r><w:t>Ein Absatz aus dem Fixturebestand.</w:t></w:r></w:p>"
        "</w:body></w:document>"
    )
    with zipfile.ZipFile(HERE / "bericht.docx", "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", content_types)
        archive.writestr("_rels/.rels", rels)
        archive.writestr("word/document.xml", document)


def build_epub() -> None:
    container = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">'
        '<rootfiles><rootfile full-path="OEBPS/content.opf"'
        ' media-type="application/oebps-package+xml"/></rootfiles></container>'
    )
    opf = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="id">'
        '<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">'
        '<dc:identifier id="id">urn:uuid:kaimarkit-fixture</dc:identifier>'
        f"<dc:title>{MARKER}</dc:title><dc:language>de</dc:language>"
        '<meta property="dcterms:modified">2026-01-01T00:00:00Z</meta></metadata>'
        '<manifest><item id="nav" href="nav.xhtml" media-type="application/xhtml+xml"'
        ' properties="nav"/>'
        '<item id="kap1" href="kap1.xhtml" media-type="application/xhtml+xml"/></manifest>'
        '<spine><itemref idref="kap1"/></spine></package>'
    )
    nav = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">'
        "<head><title>Inhalt</title></head><body>"
        '<nav epub:type="toc"><ol><li><a href="kap1.xhtml">Erstes Kapitel</a></li></ol></nav>'
        "</body></html>"
    )
    chapter = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<html xmlns="http://www.w3.org/1999/xhtml"><head><title>Erstes Kapitel</title></head>'
        f"<body><h1>{MARKER}</h1><p>Ein Kapitel aus dem Fixturebestand.</p></body></html>"
    )
    with zipfile.ZipFile(HERE / "buch.epub", "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("mimetype", "application/epub+zip", zipfile.ZIP_STORED)
        archive.writestr("META-INF/container.xml", container)
        archive.writestr("OEBPS/content.opf", opf)
        archive.writestr("OEBPS/nav.xhtml", nav)
        archive.writestr("OEBPS/kap1.xhtml", chapter)


def build_odt() -> None:
    manifest = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<manifest:manifest xmlns:manifest="urn:oasis:names:tc:opendocument:xmlns:manifest:1.0"'
        ' manifest:version="1.2">'
        '<manifest:file-entry manifest:full-path="/"'
        ' manifest:media-type="application/vnd.oasis.opendocument.text"/>'
        '<manifest:file-entry manifest:full-path="content.xml"'
        ' manifest:media-type="text/xml"/>'
        '<manifest:file-entry manifest:full-path="styles.xml"'
        ' manifest:media-type="text/xml"/></manifest:manifest>'
    )
    content = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<office:document-content'
        ' xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"'
        ' xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" office:version="1.2">'
        "<office:body><office:text>"
        f'<text:h text:outline-level="1">{MARKER}</text:h>'
        "<text:p>Ein Absatz aus dem Fixturebestand.</text:p>"
        "</office:text></office:body></office:document-content>"
    )
    # Pandoc liest styles.xml und bricht ohne die Datei ab, auch wenn sie leer bleibt.
    styles = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<office:document-styles'
        ' xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"'
        ' office:version="1.2"><office:styles/></office:document-styles>'
    )
    with zipfile.ZipFile(HERE / "text.odt", "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(
            "mimetype", "application/vnd.oasis.opendocument.text", zipfile.ZIP_STORED
        )
        archive.writestr("META-INF/manifest.xml", manifest)
        archive.writestr("content.xml", content)
        archive.writestr("styles.xml", styles)


def build_pdf() -> None:
    """Ein einseitiges PDF mit einer gezeichneten Tabelle, von Hand gesetzt.

    Die Linien stehen im Inhaltsstrom, damit Docling die Tabelle als Tabelle
    erkennt und nicht als drei Textzeilen.
    """
    left, right, top = 72, 380, 720
    row_height, columns = 28, (72, 226, 380)
    lines = []
    for index in range(len(TABLE) + 1):
        y = top - index * row_height
        lines.append(f"{left} {y} m {right} {y} l S")
    bottom = top - len(TABLE) * row_height
    for x in columns:
        lines.append(f"{x} {top} m {x} {bottom} l S")

    text = [f"BT /F1 16 Tf {left} {top + 30} Td ({MARKER}) Tj ET"]
    for row_index, row in enumerate(TABLE):
        baseline = top - row_index * row_height - 19
        for column_index, cell in enumerate(row):
            x = columns[column_index] + 6
            text.append(f"BT /F1 11 Tf {x} {baseline} Td ({cell}) Tj ET")

    stream = "0.6 w\n" + "\n".join(lines) + "\n" + "\n".join(text) + "\n"
    body = stream.encode("ascii")

    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] "
        b"/Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>",
        b"<< /Length %d >>\nstream\n" % len(body) + body + b"endstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>",
    ]

    out = bytearray(b"%PDF-1.4\n")
    offsets = []
    for number, obj in enumerate(objects, start=1):
        offsets.append(len(out))
        out += b"%d 0 obj\n" % number + obj + b"\nendobj\n"
    xref = len(out)
    out += b"xref\n0 %d\n" % (len(objects) + 1)
    out += b"0000000000 65535 f \n"
    for offset in offsets:
        out += b"%010d 00000 n \n" % offset
    out += b"trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (
        len(objects) + 1,
        xref,
    )
    (HERE / "tabelle.pdf").write_bytes(bytes(out))


def build_xlsx() -> None:
    from openpyxl import Workbook

    book = Workbook()
    sheet = book.active
    sheet.title = "Fixture"
    sheet.append([MARKER, "Engine"])
    for row in TABLE[1:]:
        sheet.append(row)
    book.save(HERE / "tabelle.xlsx")


def build_pptx() -> None:
    content_types = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels"'
        ' ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/ppt/presentation.xml" ContentType="application/vnd.'
        'openxmlformats-officedocument.presentationml.presentation.main+xml"/>'
        '<Override PartName="/ppt/slides/slide1.xml" ContentType="application/vnd.'
        'openxmlformats-officedocument.presentationml.slide+xml"/></Types>'
    )
    rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006'
        '/relationships/officeDocument" Target="ppt/presentation.xml"/></Relationships>'
    )
    presentation = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<p:presentation xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"'
        ' xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"'
        ' xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">'
        '<p:sldIdLst><p:sldId id="256" r:id="rId1"/></p:sldIdLst>'
        '<p:sldSz cx="9144000" cy="6858000"/><p:notesSz cx="6858000" cy="9144000"/>'
        "</p:presentation>"
    )
    presentation_rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006'
        '/relationships/slide" Target="slides/slide1.xml"/></Relationships>'
    )
    slide = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"'
        ' xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"'
        ' xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">'
        "<p:cSld><p:spTree>"
        '<p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>'
        "<p:grpSpPr/>"
        '<p:sp><p:nvSpPr><p:cNvPr id="2" name="Titel"/>'
        '<p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr><p:nvPr/></p:nvSpPr>'
        '<p:spPr><a:xfrm><a:off x="914400" y="914400"/><a:ext cx="6400800" cy="1828800"/>'
        '</a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr>'
        "<p:txBody><a:bodyPr/><a:lstStyle/>"
        f"<a:p><a:r><a:t>{MARKER}</a:t></a:r></a:p>"
        "<a:p><a:r><a:t>Eine Folie aus dem Fixturebestand.</a:t></a:r></a:p>"
        "</p:txBody></p:sp></p:spTree></p:cSld></p:sld>"
    )
    slide_rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"/>'
    )
    with zipfile.ZipFile(HERE / "folien.pptx", "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", content_types)
        archive.writestr("_rels/.rels", rels)
        archive.writestr("ppt/presentation.xml", presentation)
        archive.writestr("ppt/_rels/presentation.xml.rels", presentation_rels)
        archive.writestr("ppt/slides/slide1.xml", slide)
        archive.writestr("ppt/slides/_rels/slide1.xml.rels", slide_rels)


def build_png() -> None:
    """Ein Bild mit lesbarem Text — Vorlage fuer den OCR-Weg von Docling."""
    from PIL import Image, ImageDraw, ImageFont

    dejavu = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
    font = ImageFont.truetype(str(dejavu), 28) if dejavu.exists() else ImageFont.load_default()

    image = Image.new("L", (520, 130), color=255)
    draw = ImageDraw.Draw(image)
    draw.text((20, 24), MARKER, fill=0, font=font)
    draw.text((20, 70), "Ein Bild aus dem Fixturebestand.", fill=0, font=font)
    image.save(HERE / "bild.png", optimize=True)


def main() -> None:
    for build in (
        build_html,
        build_csv,
        build_docx,
        build_epub,
        build_odt,
        build_pdf,
        build_xlsx,
        build_pptx,
        build_png,
    ):
        build()
        print(build.__name__)


if __name__ == "__main__":
    main()
