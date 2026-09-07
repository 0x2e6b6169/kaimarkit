---
id: 131
title: DOC-23 · Eigene Seite fuer die Bedienung der Oberflaeche
status: todo
priority: high
created: 2026-09-07T11:09:52.799107404+02:00
updated: 2026-09-07T11:09:52.799107404+02:00
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
