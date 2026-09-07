---
id: 134
title: DOC-24 · Nutzer- und Admin-Dokumentation sauber trennen
status: todo
priority: high
created: 2026-09-07T11:30:16.173220563+02:00
updated: 2026-09-07T11:30:16.173220563+02:00
assignee: akar
tags:
    - docs
class: standard
---

## Ziel

Direkter Nutzerauftrag: Die Doku vermischt Nutzer- und Betriebsperspektive, obwohl
DOC-23 die Oberflächenseite schon herausgelöst hat. Der Flachbau des `nav` zeigt
Schnellstart (Setup), Oberfläche (Nutzung), Formate, API, Betrieb und Grenzen
nebeneinander, ohne dass ersichtlich ist, wer welche Seite braucht. Zwei saubere
Bereiche: **Für Nutzer**, gedacht von Anwendungsfällen her — was will jemand mit dem
Werkzeug tun. **Für Admins**, gedacht von der Betriebsperspektive her — installieren,
konfigurieren, betreiben, absichern, ansprechen.

## Eigene Dateien

- `docs/index.md` — wird kurz: was ist kaimarkit, dann zwei Wege statt einer flachen
  Liste.
- `mkdocs.yml`, Abschnitt `nav` — zwei benannte Gruppen "Für Nutzer" und "Für
  Admins"; "Start" und "Entwicklung" bleiben, wie sie sind.
- `docs/benutzung.md` — wandert in den Nutzer-Bereich (z. B. `docs/nutzer/`) und wird
  von Anwendungsfällen her neu gegliedert, nicht von UI-Elementen. Ob das eine Seite
  bleibt oder in mehrere zerfällt ("eine Datei umwandeln", "eine Webseite umwandeln",
  "die richtige Engine und OCR wählen", "eine Warnung verstehen", "wenn der Dienst
  nicht antwortet" o. ä.), entscheidet die Lane. Der bestehende Text ist die fachliche
  Grundlage; seine Fakten bleiben, seine Gliederung darf sich ändern.
- `docs/schnellstart.md`, `docs/formate.md`, `docs/grenzen.md`, `docs/api.md` sowie
  `docs/betrieb/*.md` — wandern in den Admin-Bereich (z. B. `docs/admin/`). Inhaltlich
  bleiben sie, wie sie sind, außer wo sich ein Verweis durch den Umzug ändert.
- Alle internen Markdown-Links im gesamten `docs/`-Baum, die sich durch die
  Verschiebung ändern — vorher grep über alle `.md`-Dateien nach jedem betroffenen
  Dateinamen, nicht raten, wo überall verlinkt wird.

Nicht hier: `docs/entwicklung.md`. Es bleibt an seiner Stelle und außerhalb beider
Bereiche — es ist weder Nutzer- noch Admin-Dokumentation, sondern für Mitwirkende am
Code.

## Vorgaben

- Nutzer-Bereich setzt keine Terminal- oder API-Kenntnis voraus (wie schon in
  benutzung.md) und ist von Anwendungsfällen her gegliedert.
- Admin-Bereich setzt keine Kenntnis der Oberfläche voraus und ist von der
  Betriebsperspektive her gegliedert: installieren, konfigurieren, hinter einen Proxy
  stellen, Anmeldung davorsetzen, Grenzen setzen, die Schnittstelle ansprechen.
- Kein Inhalt geht verloren — was heute unter einem Titel steht, findet sich unter dem
  neuen wieder oder als Zusammenfassung mit Verweis.
- Ein internes Kreuz-Verweis von einem Bereich in den anderen bleibt möglich (etwa
  Nutzer-Seite verweist für Details auf eine Admin-Referenzseite) — das ist kein
  Rückfall in die Vermischung, solange die Einordnung im nav eindeutig bleibt.

## Prüfung

- `mkdocs build --strict` läuft durch — das schlägt bei einem toten internen Link
  automatisch fehl.
- `mkdocs.yml` `nav` zeigt zwei benannte Gruppen für Nutzer- und Admin-Seiten.
- `docs/index.md` verweist auf beide Bereiche, nicht mehr auf eine flache Liste
  einzelner Seiten.
- Kein Docker- oder curl-Beispiel im Nutzer-Bereich (geflachte Textsuche wie in
  DOC-23).
