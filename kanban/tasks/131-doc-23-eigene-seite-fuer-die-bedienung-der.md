---
id: 131
title: DOC-23 · Eigene Seite fuer die Bedienung der Oberflaeche
status: done
priority: high
created: 2026-09-07T11:09:52.799107404+02:00
updated: 2026-09-07T11:56:09.186549071+02:00
started: 2026-09-07T11:18:06.512514647+02:00
completed: 2026-09-07T11:18:06.512514647+02:00
assignee: akar
tags:
    - docs
class: standard
---

## Ziel

Dringender Nutzerauftrag: Die Dokumentation ist bislang durchgehend für Betreiber und
Entwickler geschrieben — Schnellstart mischt Docker-Aufbau, curl-Aufrufe und die
Bedienung der Oberfläche in einer Seite. Wer nur die Web-Oberfläche benutzt, ohne
Container zu bauen oder die API zu rufen, braucht eine eigene Seite, die nichts davon
voraussetzt.

## Eigene Dateien

- Neue Seite `docs/benutzung.md` (Name nach Ermessen der Lane, konsistent mit den
  bestehenden: `schnellstart.md`, `formate.md`, `grenzen.md`)
- `docs/schnellstart.md`, Abschnitt "Über die Oberfläche" (aktuell Zeile 78–116): der
  Inhalt zieht auf die neue Seite um, an seiner Stelle bleibt ein kurzer Verweis
  dorthin. Der Rest von schnellstart.md — Voraussetzungen, Start, curl-Beispiele —
  bleibt unberührt und gehört nicht zu diesem Ticket.
- `mkdocs.yml`, Abschnitt `nav`: die neue Seite eintragen.
- `docs/index.md`, Abschnitt "Wohin als Nächstes": die neue Seite in die Liste
  aufnehmen.

## Vorgaben

- Zielgruppe: jemand, der eine Adresse genannt bekommen hat und die Oberfläche öffnet
  — keine Docker-, Terminal- oder API-Kenntnis vorausgesetzt. Kein curl-Beispiel auf
  dieser Seite.
- Inhalt mindestens: Dateien per Ablegen oder Auswahl hochladen; die Warteschlange und
  was eine Zeile zeigt (Status, Engine, Dauer, eine gescheiterte Datei hält die
  anderen nicht auf); Webseiten über das mehrzeilige Adressfeld; die Optionen
  (Enginewahl als Schaltergruppe mit Erklärung, der OCR-Schalter mit seiner
  Reichweite — FE-26 hat dafür ein Info-Zeichen im UI, das gehört hier erwähnt);
  Vorschau und Herunterladen einzeln oder als ZIP; eine laufende Datei abbrechen;
  eine Warnung lesen (seit BE-39/BE-40 nennt sie Grund und Umweg).
- Was heute schon unter "Über die Oberfläche" in schnellstart.md steht, ist die
  fachliche Grundlage — prüfen, ob es seit FE-26/FE-27/BE-39/BE-40 noch stimmt, statt
  es unverändert zu verschieben.
- Verweise auf [Formate](formate.md) und [Grenzen](grenzen.md) für Details, die dort
  schon stehen, statt sie zu duplizieren.

## Prüfung

- `mkdocs build --strict` läuft durch.
- Kein Docker- oder curl-Beispiel auf der neuen Seite (geflachte Textsuche, kein
  Codeblock mit `docker` oder `curl`).
- `docs/schnellstart.md` behält die Voraussetzungen und den curl-Weg unverändert;
  "Über die Oberfläche" existiert dort nur noch als Verweis.

[[2026-09-07]] Mon 11:18

## Ergebnis akar-43

Neue Seite `docs/benutzung.md` (nav: "Oberfläche", zwischen Schnellstart und
Formate), Verweis in `docs/index.md`, Abschnitt "Über die Oberfläche" in
`docs/schnellstart.md` auf 34 Wörter Verweis gekürzt. Merge 223700f.

**Rot vor grün.** Vor der Arbeit schlugen vier Prüfpunkte fehl: Seite fehlt,
nicht im nav, 368 Wörter im Abschnitt statt < 60, kein Verweis auf benutzung.md.
`mkdocs build --strict` war vorher schon grün — dieser Punkt ist ein
Regressionsschutz, kein Beleg. Danach: 0 Fundstellen `docker|curl` im
geflachten Text und in Codeblöcken, 34 Wörter, Rückgabewert 0 und 0
WARNING/ERROR-Zeilen. Der `schnellstart.md`-Diff ist ein einziger Hunk ab
Zeile 80; Voraussetzungen, Start und alle curl-Wege stehen unverändert.

**Was am alten Abschnitt nicht mehr stimmte** (geprüft gegen `frontend/src/`
und `backend/app/`):

- **Warnungen kamen gar nicht vor.** Seit BE-39 (`_placeholder_warnings` /
  `_detour` in `converters/docling.py`) und BE-40
  (`_embedded_image_warnings` in `converters/markitdown.py`) nennt eine
  Warnung Grund und Umweg. Die neue Seite zitiert beide Wortlaute.
- **Der OCR-Schalter fehlte vollständig.** FE-26 hat ihn um den Kurzsatz
  "wirkt nur in PDF und Bilddateien" und ein tastaturerreichbares Info-Zeichen
  ergänzt (`components/OptionsPanel.vue`, `data-test="ocr-short"` /
  `"ocr-info"`). Neuer Unterabschnitt "Text in Bildern erkennen".
- **"Die Vorschau klappt das gewandelte Markdown auf"** war zu dünn. Der Knopf
  heißt seit FE-27 "Vorschau" bzw. "Vorschau schließen"
  (`components/FileRow.vue`), und darin stehen zwei Reiter "Vorschau" und
  "Rohtext" plus "Kopieren" (`components/MarkdownPreview.vue`).
- **"wie im nächsten Abschnitt beschrieben"** zeigte auf "Welche Engine kommt
  zum Zug?" in schnellstart.md und wäre nach dem Umzug ins Leere gelaufen.
  Ersetzt durch die Erklärung selbst.
- **Der Zustand `warming` fehlte.** `EngineSelect.vue` zeigt "(lädt noch)"
  und lässt die Engine wählbar; der alte Text kannte nur wählbar/nicht wählbar.
- **Der Rücksprung auf "automatisch"** fehlte
  (`OptionsPanel.vue`, `watch(offered, …)`).

Neu belegt und vorher nirgends beschrieben: Zeichen und Wort je Zustand
(`FileRow.vue`, `BADGES`), mitlaufende Dauer `läuft · 0:47`, höchstens zwei
gleichzeitig (`MAX_PARALLEL` in `useConversion.ts`), "Entfernen", die
Grenze `limits.max_files` samt Rückgabe der Adressen ins Feld
(`UrlInput.keep`), `kaimarkit.zip` und `_errors.txt` (`download.ts`),
das Banner "Der Dienst antwortet nicht" und die Version im Fuß (`App.vue`).

## Auflage aufgehoben (2026-09-07, katche)

Die Vorgabe "Kein Docker- oder curl-Beispiel auf der neuen Seite" ist durch DOC-26
(#136) aufgehoben: Ein Aufruf über die Schnittstelle gehört seither ausdrücklich in
den Nutzer-Bereich, als zweiter Weg neben der Oberfläche.
