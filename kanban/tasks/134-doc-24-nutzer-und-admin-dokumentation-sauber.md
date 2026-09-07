---
id: 134
title: DOC-24 · Nutzer- und Admin-Dokumentation sauber trennen
status: done
priority: high
created: 2026-09-07T11:30:16.173220563+02:00
updated: 2026-09-07T11:39:58.514462026+02:00
started: 2026-09-07T11:39:57.910770928+02:00
completed: 2026-09-07T11:39:57.910770928+02:00
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

[[2026-09-07]] Mon 11:39

---

## Ergebnis (akar-44)

Zweig `task/134-doc-24`, Merge `1d71826`.

**Neue Struktur (alt → neu).** `docs/betrieb/` ist weg; `docs/admin/` ist flach.

| alt | neu |
|---|---|
| `docs/benutzung.md` | `docs/nutzer/dateien-wandeln.md`, `…/webseiten-wandeln.md`, `…/engine-und-texterkennung.md`, `…/warnungen-und-fehler.md` |
| `docs/schnellstart.md` | `docs/admin/schnellstart.md` |
| `docs/formate.md` | `docs/admin/formate.md` |
| `docs/api.md` | `docs/admin/api.md` |
| `docs/grenzen.md` | `docs/admin/grenzen.md` |
| `docs/betrieb/konfiguration.md` | `docs/admin/konfiguration.md` |
| `docs/betrieb/lokal.md` | `docs/admin/lokal.md` |
| `docs/betrieb/traefik.md` | `docs/admin/traefik.md` |
| `docs/betrieb/authelia.md` | `docs/admin/authelia.md` |
| `docs/entwicklung.md` | unverändert, außerhalb beider Bereiche |

Alle neun Umzüge als `git mv`; `git log --follow` reicht über den Umzug hinweg
bis zu DOC-23 beziehungsweise BE-35 zurück.

**Zwei Entscheidungen, die der Rumpf offen ließ.**

Die Verzeichnisse heißen `docs/nutzer/` und `docs/admin/`, weil die Doku deutsch
ist und `docs/betrieb/` schon einen deutschen Pfad vorgab; die Dateinamen bleiben,
wie sie waren, damit der Umzug nicht zusätzlich Links umschreibt.

`benutzung.md` zerfällt in vier Seiten statt einer. Eine einzelne Seite „Die
Oberfläche" in der Gruppe „Für Nutzer" hätte im nav nichts über
Anwendungsfälle gesagt — genau das soll die Gliederung aber zeigen. Vier Absichten
tragen je eine Seite: eine Datei wandeln, eine Webseite wandeln, Engine und
Texterkennung wählen, Warnungen und Fehler verstehen. Fünf oder mehr wären zu dünn
geworden; „Nicht mehr warten" bleibt deshalb bei der Warteschlange.

**Zahlen.** 58 interne Markdown-Links im Baum, davon 30 durch den Umzug geändert
(21 in `docs/admin/`, 7 in `docs/nutzer/`, 2 in `docs/entwicklung.md`) plus 5 in
`README.md` und eine Pfadnennung in Prosa (`docs/admin/grenzen.md:7`). Ein Skript
prüft alle 58 Ziele **und** alle sieben Anker gegen die Überschriften der Zieldatei
— `mkdocs build --strict` prüft Anker nicht. Überschriften: 98 vorher, 100 nachher;
sieben verschwundene Titel sind alle belegt wiederverwendet (Ebenenwechsel,
Seitentitel oder Aufteilung), keiner ersatzlos. Ein Satzvergleich der alten
`benutzung.md` gegen die vier neuen Seiten meldet vier nicht wörtlich
wiedergefundene Sätze; alle vier sind bewusste Umformulierungen, deren Aussage
erhalten ist.

**Rot vor grün.**

- nav-Gruppen: vorher `grep -cE '^\s*- (Für Nutzer|Für Admins):' mkdocs.yml` → 0,
  nachher → 2.
- `index.md`: vorher geflacht 0 Treffer auf „Für Nutzer"/„Für Admins" und 7 Zeilen
  flache Seitenliste, nachher je 1 Treffer und 0 Listenzeilen.
- Kein Docker/curl im Nutzer-Bereich: geflacht 0 Treffer über `docs/nutzer/*.md`.
  Diese Prüfung war inhaltlich **schon vorher grün** — `benutzung.md` enthielt
  nichts dergleichen. Gegenprobe, damit die Suche nachweislich greift:
  dieselbe Suche über `docs/admin/*.md` findet 64 Treffer.
- `mkdocs build --strict`: **vorher schon grün** (RC 0), nachher grün. Der rote
  Material-Hinweis auf MkDocs 2.0 ist ein Herstellerhinweis, keine Warnung.

**Befund, außerhalb der eigenen Dateien, nichts geändert.** Acht Dateien außerhalb
`docs/` nennen alte Pfade in Prosa oder Kommentaren und sind seit dem Merge falsch:
`docker/.env.example` (3×), `docker/docker-compose.authelia.yml` (3×),
`docker/docker-compose.traefik.yml` (2×), `Makefile` (1×),
`backend/app/uploads.py` (1×), `backend/tests/test_docling_ocr.py` (1×),
`frontend/src/components/EngineSelect.vue` (1×),
`frontend/src/components/OptionsPanel.vue` (1×). Dazu `CLAUDE.md` (Konvention 6
nennt `docs/betrieb/konfiguration.md`, der Ticketschnitt-Abschnitt zweimal
`docs/formate.md`) und `.claude/skills/work-lane/SKILL.md`. Ein Nachfolgeticket
sollte sie besitzen; sie liegen in drei fremden Lanes und gehörten nicht in
dieses.
