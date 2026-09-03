"""Baut die Beispieldateien in diesem Verzeichnis neu.

Aufruf aus ``backend/``::

    python tests/fixtures/build_fixtures.py

Alle Inhalte entstehen hier, nichts stammt aus fremden Quellen. Jede Datei traegt
den Baustein ``Kaimarkit Fixture``; darauf verlassen sich die Smoketests in
``tests/test_converters.py``.

Acht der zwölf Dateien baut die Standardbibliothek. Nur ``tabelle.xlsx`` braucht
openpyxl und die drei Bilder Pillow; beide kommen mit ``markitdown[all]`` ohnehin
in die Entwicklungsumgebung.
"""

from __future__ import annotations

import zipfile
import zlib
from pathlib import Path

HERE = Path(__file__).parent

#: Der Baustein, auf den sich jeder Smoketest verlaesst.
MARKER = "Kaimarkit Fixture"

#: Der Satz in scan.png und foto_exif6.jpg. Die OCR-Tests in
#: ``tests/test_docling_ocr.py`` erwarten ihn im Ergebnis; er hat absichtlich keine
#: Umlaute, damit sie die Texterkennung prüfen und nicht ihr Zeichenrepertoire.
SCAN_SENTENCE = "Dieser Satz stammt aus einem Scan."

#: Der Satz, der in ``bild_im_dokument.docx`` und ``bild_im_dokument.pdf`` allein im
#: eingebetteten Bild steht — nirgends in der Textebene. Wer ihn im Markdown findet,
#: hat einen Beleg dafür, dass die Texterkennung das Bild gelesen hat. Auch er kommt
#: ohne Umlaute aus (BE-38, GitHub #2).
IMAGE_SENTENCE = "Dieser Satz steckt nur im Bild."

#: Der EXIF-Tag ``Orientation``. ``6`` heißt „beim Anzeigen um 90 Grad im
#: Uhrzeigersinn drehen“ — so legen Handys ein hochkant aufgenommenes Foto ab.
EXIF_ORIENTATION = 0x0112

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


def _write_pdf(name: str, stream: str, image: tuple[bytes, int, int] | None = None) -> None:
    """Setzt einen Inhaltsstrom in ein einseitiges PDF und schreibt es.

    Der Behaelter ist von Hand gesetzt und unkomprimiert: fuenf Objekte, eine
    Schrift, eine xref-Tabelle mit gezaehlten Offsets. Alle PDF-Fixtures teilen ihn
    sich, denn sie unterscheiden sich nur im Inhaltsstrom.

    ``image`` haengt ein Graustufenbild als sechstes Objekt an und meldet es in den
    Ressourcen der Seite als ``/Im1`` — der Inhaltsstrom zeichnet es dann mit
    ``/Im1 Do``. Die Rohdaten kommen deflatiert herein; das spart nichts als Platz,
    aber ein unkomprimiertes Bild machte die Datei zwanzigmal so gross.
    """
    body = stream.encode("ascii")

    resources = b"/Font << /F1 5 0 R >>"
    if image is not None:
        resources += b" /XObject << /Im1 6 0 R >>"

    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] "
        b"/Resources << " + resources + b" >> /Contents 4 0 R >>",
        b"<< /Length %d >>\nstream\n" % len(body) + body + b"endstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>",
    ]

    if image is not None:
        data, width, height = image
        objects.append(
            b"<< /Type /XObject /Subtype /Image /Width %d /Height %d /ColorSpace"
            b" /DeviceGray /BitsPerComponent 8 /Filter /FlateDecode /Length %d >>\nstream\n"
            % (width, height, len(data))
            + data
            + b"\nendstream"
        )

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
    (HERE / name).write_bytes(bytes(out))


def _grid(left: int, top: int, columns: int, rows: int, width: int, height: int) -> list[str]:
    """Die Linien eines Gitters als Zeichenbefehle.

    Docling erkennt eine Tabelle an ihren Linien. Stuenden nur die Zellen da, saehe
    das Modell Textzeilen.
    """
    right, bottom = left + columns * width, top - rows * height
    lines = [f"{left} {top - i * height} m {right} {top - i * height} l S" for i in range(rows + 1)]
    lines += [
        f"{left + j * width} {top} m {left + j * width} {bottom} l S" for j in range(columns + 1)
    ]
    return lines


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

    _write_pdf("tabelle.pdf", "0.6 w\n" + "\n".join(lines) + "\n" + "\n".join(text) + "\n")


def build_breit_pdf() -> None:
    """Ein PDF mit einer breiten, engen Tabelle — die Vorlage fuer den Platzhalterfall.

    Elf Spalten auf vierzehn Zeilen, in Sieben-Punkt-Schrift. Diese Form hat Docling
    im Abnahmelauf vom 01.09.2026 als Bild eingeordnet und durch ``<!-- image -->``
    ersetzt; ``tabelle.pdf`` mit seinen drei Spalten tut das nicht. Ohne eine solche
    Vorlage im Bestand ist die Platzhalter-Warnung aus ``docling.py`` nirgends mehr
    nachzufahren.

    Ob eine bestimmte Fassung von Docling hier wirklich einen Platzhalter setzt,
    entscheidet das Modell und nicht diese Datei. Der zugehoerige Test steht deshalb
    hinter der Marke ``slow`` und laeuft nur dort, wo Docling installiert ist.
    """
    left, top = 30, 780
    columns, rows = 11, 14
    width, height = 50, 22

    text = [f"BT /F1 14 Tf {left} {top + 24} Td ({MARKER}) Tj ET"]
    for row in range(rows):
        baseline = top - row * height - 15
        for column in range(columns):
            cell = f"Spalte {column + 1}" if row == 0 else f"Z{row:02d}S{column + 1:02d}"
            text.append(f"BT /F1 7 Tf {left + column * width + 3} {baseline} Td ({cell}) Tj ET")

    lines = _grid(left, top, columns, rows, width, height)
    _write_pdf("breit.pdf", "0.6 w\n" + "\n".join(lines) + "\n" + "\n".join(text) + "\n")


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


def build_scan_png() -> None:
    """Ein Scan, wie ihn der Nutzer hochlädt: ein Bild mit einem bekannten Satz.

    Anders als ``bild.png`` ist dieses Bild die Vorlage für einen Test, der den
    Satz wiederfinden will (BE-34, GitHub #2). Deshalb ist es größer gesetzt und
    entsteht deterministisch: fester Font, feste Größe, fester Satz. Ein Neubau
    liefert dasselbe Bild.
    """
    from PIL import Image, ImageDraw, ImageFont

    dejavu = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
    if not dejavu.exists():
        raise SystemExit(
            "scan.png braucht DejaVuSans.ttf; ohne festen Font ist das Bild nicht reproduzierbar."
        )
    font = ImageFont.truetype(str(dejavu), 40)

    image = Image.new("L", (1000, 160), color=255)
    draw = ImageDraw.Draw(image)
    draw.text((40, 56), SCAN_SENTENCE, fill=0, font=font)
    image.save(HERE / "scan.png", optimize=True)


def build_exif_jpg() -> None:
    """Derselbe Satz wie in ``scan.png``, nur wie eine Kamera ihn ablegt.

    Handys speichern die Pixel so, wie der Sensor sie liefert, und notieren die
    Drehung daneben als EXIF-Orientation. Wer den Tag nicht ausliest, sieht den Satz
    hochkant; die Texterkennung findet darin nichts (BE-34, GitHub #2).

    Die beiden Vorlagen unterscheiden sich in nichts als dieser Drehung — derselbe
    Font, dieselbe Größe, derselbe Satz. Der Test in ``tests/test_docling_ocr.py``
    misst deshalb genau sie und nichts sonst.
    """
    from PIL import Image, ImageDraw, ImageFont

    dejavu = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
    if not dejavu.exists():
        raise SystemExit(
            "foto_exif6.jpg braucht DejaVuSans.ttf; ohne festen Font ist das Bild"
            " nicht reproduzierbar."
        )
    font = ImageFont.truetype(str(dejavu), 40)

    upright = Image.new("L", (1000, 160), color=255)
    draw = ImageDraw.Draw(upright)
    draw.text((40, 56), SCAN_SENTENCE, fill=0, font=font)

    # ``ROTATE_90`` dreht gegen den Uhrzeigersinn. Orientation 6 nimmt diese Drehung
    # beim Anzeigen zurück: Wer den Tag auswertet, sieht wieder ``upright``.
    sideways = upright.transpose(Image.Transpose.ROTATE_90)
    exif = Image.Exif()
    exif[EXIF_ORIENTATION] = 6
    sideways.save(HERE / "foto_exif6.jpg", quality=92, exif=exif)


def _sentence_image(width: int = 900, height: int = 300) -> object:
    """``IMAGE_SENTENCE`` als Graustufenbild, so wie ``scan.png`` gesetzt.

    Dieselbe Vorlage geht in das docx und in das PDF. Beide Fixtures zeigen damit
    denselben Satz in derselben Schrift; ein Unterschied im Ergebnis liegt dann am
    Format und nicht am Bild.
    """
    from PIL import Image, ImageDraw, ImageFont

    dejavu = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
    if not dejavu.exists():
        raise SystemExit(
            "Die Fixtures mit Bild im Dokument brauchen DejaVuSans.ttf; ohne festen"
            " Font sind sie nicht reproduzierbar."
        )
    font = ImageFont.truetype(str(dejavu), 40)

    image = Image.new("L", (width, height), color=255)
    ImageDraw.Draw(image).text((40, 130), IMAGE_SENTENCE, fill=0, font=font)
    return image


def build_bild_im_dokument_docx() -> None:
    """Ein Word-Dokument mit Textebene und einem Bild darin.

    Das ist der Fall aus GitHub-Issue #2: Wer einen abfotografierten Absatz in ein
    Word-Dokument setzt, gibt eine Datei ab, die zum groessten Teil aus Text besteht.
    Die Textebene traegt ``MARKER``, das Bild traegt ``IMAGE_SENTENCE`` — und nur
    dieser Satz belegt, dass die Texterkennung ueberhaupt gelaufen ist.
    """
    import io

    buffer = io.BytesIO()
    _sentence_image().save(buffer, format="PNG", optimize=True)
    picture = buffer.getvalue()

    content_types = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Default Extension="png" ContentType="image/png"/>'
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
    document_rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006'
        '/relationships/image" Target="media/bild.png"/></Relationships>'
    )

    # Die Ausdehnung in EMU: 900 mal 300 Bildpunkte, mit 96 dpi gerechnet.
    cx, cy = 8572500, 2857500
    drawing = (
        "<w:p><w:r><w:drawing>"
        '<wp:inline distT="0" distB="0" distL="0" distR="0">'
        f'<wp:extent cx="{cx}" cy="{cy}"/>'
        '<wp:docPr id="1" name="Bild 1"/>'
        '<a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
        '<a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">'
        '<pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">'
        '<pic:nvPicPr><pic:cNvPr id="0" name="bild.png"/><pic:cNvPicPr/></pic:nvPicPr>'
        '<pic:blipFill><a:blip r:embed="rId2"/>'
        "<a:stretch><a:fillRect/></a:stretch></pic:blipFill>"
        '<pic:spPr><a:xfrm><a:off x="0" y="0"/>'
        f'<a:ext cx="{cx}" cy="{cy}"/></a:xfrm>'
        '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr>'
        "</pic:pic></a:graphicData></a:graphic>"
        "</wp:inline></w:drawing></w:r></w:p>"
    )
    document = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"'
        ' xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"'
        ' xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing">'
        "<w:body>"
        '<w:p><w:pPr><w:pStyle w:val="Heading1"/></w:pPr>'
        f"<w:r><w:t>{MARKER}</w:t></w:r></w:p>"
        "<w:p><w:r><w:t>Ein Absatz aus dem Fixturebestand.</w:t></w:r></w:p>"
        f"{drawing}"
        "</w:body></w:document>"
    )

    target = HERE / "bild_im_dokument.docx"
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", content_types)
        archive.writestr("_rels/.rels", rels)
        archive.writestr("word/document.xml", document)
        archive.writestr("word/_rels/document.xml.rels", document_rels)
        archive.writestr("word/media/bild.png", picture)


def build_bild_im_dokument_pdf() -> None:
    """Dasselbe als PDF: eine Textebene, und darunter dasselbe Bild.

    Das Gegenstueck zum docx. Ein PDF mit Textebene laeuft in Docling durch eine
    andere Pipeline als ein Word-Dokument, und erst der Vergleich beider Dateien
    zeigt, woran ein fehlender Satz liegt (BE-38, GitHub #2).
    """
    image = _sentence_image()
    data = zlib.compress(image.tobytes(), 9)

    # Das Bild deckt 480 mal 160 Punkte einer Seite von 595 mal 842 — gut fuenfzehn
    # Prozent. Docling laesst kleine Bilder aus der Texterkennung heraus; deshalb
    # steht es hier gross auf der Seite und nicht als Briefmarke.
    stream = (
        f"BT /F1 16 Tf 72 780 Td ({MARKER}) Tj ET\n"
        "BT /F1 11 Tf 72 750 Td (Ein Absatz aus dem Fixturebestand.) Tj ET\n"
        "q 480 0 0 160 72 540 cm /Im1 Do Q\n"
    )
    _write_pdf("bild_im_dokument.pdf", stream, image=(data, image.width, image.height))


def main() -> None:
    for build in (
        build_html,
        build_csv,
        build_docx,
        build_epub,
        build_odt,
        build_pdf,
        build_breit_pdf,
        build_xlsx,
        build_pptx,
        build_png,
        build_scan_png,
        build_exif_jpg,
        build_bild_im_dokument_docx,
        build_bild_im_dokument_pdf,
    ):
        build()
        print(build.__name__)


if __name__ == "__main__":
    main()
