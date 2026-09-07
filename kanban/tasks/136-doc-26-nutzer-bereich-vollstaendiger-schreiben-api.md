---
id: 136
title: DOC-26 · Nutzer-Bereich vollstaendiger schreiben, API-Weg ergaenzen
status: done
priority: high
created: 2026-09-07T11:54:11.282319702+02:00
updated: 2026-09-07T12:06:40.369702005+02:00
started: 2026-09-07T12:06:39.742435122+02:00
completed: 2026-09-07T12:06:39.742435122+02:00
assignee: akar
tags:
    - docs
class: standard
---

## Ziel

Direkte Nutzerkorrektur: Der Nutzer-Bereich liest sich zu knapp — er behandelt nur den
Weg über die Oberfläche, obwohl zur Zielgruppe auch gehört, wer die Schnittstelle
direkt anspricht. Die Zielgruppe hat den Dienst bereits zur Verfügung; ein Hinweis auf
Start oder Einrichtung gehört hier nicht mehr hin (das leistet der Admin-Bereich).

## Eigene Dateien

- `docs/nutzer/dateien-wandeln.md`
- `docs/nutzer/webseiten-wandeln.md`
- `docs/nutzer/engine-und-texterkennung.md`
- `docs/nutzer/warnungen-und-fehler.md`
- `mkdocs.yml` (Abschnitt `nav`), nur falls sich Seitentitel oder -zahl ändern

Nicht hier: `docs/admin/api.md` bleibt die vollständige Referenz aller Endpunkte und
Fehlercodes für Admins und Integratoren; dieses Ticket dupliziert sie nicht, sondern
verweist für die vollständige Liste dorthin.

## Vorgaben

- **Zielgruppe:** Menschen, die die Weboberfläche **oder** die Schnittstelle nutzen
  wollen — beides schon erreichbar, keine Einrichtung, kein Terminal-Vorwissen
  vorausgesetzt außer dem, was ein Beispielaufruf selbst zeigt.
- **Kein Verweis auf Start/Einrichtung mehr.** Der jetzige Einleitungssatz "Wer den
  Dienst selbst starten will, findet den Weg unter Schnellstart" (und Ähnliches)
  entfällt aus allen vier Seiten — die Zielgruppe hat das Werkzeug bereits.
- **Jeder Anwendungsfall zeigt beide Wege.** Was heute nur die Oberfläche
  beschreibt, bekommt daneben den Weg über die Schnittstelle: ein vollständiges
  Aufruf-Beispiel (Adresse, nötige Felder) und der für den Fall wichtige Teil der
  Antwort — nicht die ganze Endpunktliste, die bleibt `api.md` vorbehalten. Beispiel
  "Eine Datei wandeln": Ablegen/Auswählen **und** ein Aufruf mit dem Ergebnis, das
  dabei herauskommt. Beispiel "Warnungen verstehen": der gelbe Kasten **und** das
  Feld `warnings` in der JSON-Antwort mit demselben Wortlaut.
- **Vollständiger statt länger.** Nicht auffüllen — jeder zusätzliche Satz trägt eine
  Tatsache oder ein Beispiel. `~/.claude/rules/SPRACHE.md` gilt weiter, mit
  besonderem Augenmerk auf "Erst Substanz, dann Form": ein Absatz, der nur elegant
  klingt, ohne eine neue Aussage zu machen, gehört nicht rein.
- Bestehende Fakten und Wortlaute (Warnungstexte, Zustände der Warteschlange,
  Knopfbeschriftungen) bleiben erhalten, auch wenn sich die Gliederung ändert.

## Prüfung

- Jede der vier Seiten zeigt für ihren Anwendungsfall nachweislich beide Wege: den
  über die Oberfläche und mindestens ein vollständiges Beispiel über die
  Schnittstelle mit Aufruf und Antwortausschnitt.
- Keine Fundstelle mehr für einen Verweis auf Start/Einrichtung in den vier Seiten
  (geflachte Textsuche, nicht zeilenweise).
- `mkdocs build --strict` läuft durch.

[[2026-09-07]] Mon 12:06

## Ergebnis (akar-45)

Alle vier Seiten unter `docs/nutzer/` zeigen jetzt beide Wege. Merge 255c468,
Zweig task/136-doc-26 (--no-ff).

**Woher die Beispiele stammen.** Alle Antwortausschnitte sind gegen ein eigenes
uvicorn auf Port 8123 gemessen (pyenv-Umgebung claude-code, Docling dort nicht
installiert, markitdown und pandoc ready). Gemessen: /api/health, /api/capabilities,
/api/convert (Markdown-Zweig mit Kopfzeilen und JSON-Zweig), /api/convert/batch
(JSON, mit und ohne Fehlschlag), /api/convert/url (example.com, 127.0.0.1,
schemalose Adresse), 415 unsupported_format, 400 engine_unsuitable. Der
Warnungstext im JSON von warnungen-und-fehler.md ist gemessen, nicht abgeschrieben:
die Fixture bild_im_dokument.docx wurde als bericht.docx hochgeladen, damit der
Wortlaut Zeichen fuer Zeichen dem gelben Kasten entspricht. Einzige nicht gemessene
Stelle: der /api/capabilities-Ausschnitt in engine-und-texterkennung.md ist aus
contracts/api.md uebernommen und als gekuerzt kenntlich gemacht — die Messumgebung
hatte kein Docling und haette einen untypischen Dienst gezeigt.

**Befund aus der Messung, in die Doku uebernommen:** x-warnings ist ASCII, aus
`laedt` wird dort `l?dt` (`_header_safe` in api/convert.py). Deshalb steht auf
dateien-wandeln.md, dass der Wortlaut aus der JSON-Antwort zu holen ist.

**Fakten belegt erhalten:** 29 Wortlaute, Zustaende und Beschriftungen (Zeichen der
Warteschlange, Knopfnamen, Warnungstexte, Engine-Hinweise) vorher und nachher ueber
den geflachten Text gesucht — alle 29 vorher da, alle 29 nachher da. Der Diff
loescht nur 6 Zeilen: den ersetzten Einleitungsabsatz von dateien-wandeln.md und
zwei Zeilenenden, die weitergeschrieben wurden.

**Rot vor gruen:** Pruefung 1 vorher 0 Aufrufbeispiele auf allen vier Seiten,
Pruefung 2 vorher 3 Fundstellen (`selbst starten` plus zweimal `Schnellstart`) in
dateien-wandeln.md. Pruefung 3 (`mkdocs build --strict`) war vorher schon gruen;
Gegenprobe mit einem Link ins Leere: "Aborted with 1 warnings in strict mode!" —
die Pruefung greift.

**Umfang:** dateien-wandeln 88→150 Zeilen (616→856 Woerter), webseiten-wandeln
19→66 (151→347), engine-und-texterkennung 44→111 (341→604), warnungen-und-fehler
43→109 (320→599). Beim Substanz-Durchgang gestrichen: zwei Saetze ohne Aussage und
ein wiederholender Halbsatz.

**mkdocs.yml unveraendert** — weder Seitentitel noch Seitenzahl haben sich geaendert.

**Befund ausserhalb der eigenen Dateien, nicht geaendert:** `api/meta.py:52` setzt
`ocr_available` aus `settings.ocr_enabled`, also aus der Voreinstellung, nicht
daraus, ob der Dienst Texterkennung anbietet. Das Frontend zeigt den OCR-Schalter
nur bei `ocr_available: true` (`useCapabilities.ts:77`). Folge: Ein Dienst mit
Texterkennung, die standardmaessig aus ist, versteckt den Schalter — und der Satz
auf engine-und-texterkennung.md, `Ruehrt ihn niemand an, gilt die Voreinstellung des
Dienstes`, kann dann nie den Fall 'aus' meinen. Ticket fuer sophie.
