---
id: 136
title: DOC-26 · Nutzer-Bereich vollstaendiger schreiben, API-Weg ergaenzen
status: todo
priority: high
created: 2026-09-07T11:54:11.282319702+02:00
updated: 2026-09-07T11:54:11.282319702+02:00
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
