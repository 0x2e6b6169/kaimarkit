---
id: 20
title: 'DOC-1 · MkDocs, Material-Theme und mike: mkdocs.yml, Navigation, Seitengeruest'
status: done
priority: high
created: 2026-08-31T10:20:23.564339142+02:00
updated: 2026-08-31T10:48:45.960248605+02:00
started: 2026-08-31T10:48:45.234369873+02:00
completed: 2026-08-31T10:48:45.234369873+02:00
assignee: akar
tags:
    - docs
depends_on:
    - 3
class: standard
---

## Ziel

Die Werkzeugkette fuer die versionierte Dokumentation, damit IN-1 die Docs-Stufe
bauen kann. Ein leeres Geruest genuegt dafuer.

## Eigene Dateien

- `mkdocs.yml`
- `docs/*` als Stuempfe mit Ueberschrift und einem Satz

## Vorgaben

- `mkdocs-material`, deutsch (`theme.language: de`, `plugins.search.lang: de`).
- **`site_url: /docs/`** - der Unterpfad, nicht die Wurzel. Steht dort die Wurzel,
  verlinkt der Versions-Dropdown auf `/0.3/` statt `/docs/0.3/` und laeuft ins
  Leere.
- `extra.version.provider: mike`, `default: latest`.
- Palette mit hell/dunkel, Standard folgt dem System.
- Erweiterungen: admonition, pymdownx.superfences, pymdownx.tabbed, tables,
  attr_list, pymdownx.highlight.
- Navigation nach dem Baum aus dem Plan.
- `mike` laeuft **beim Veroeffentlichen, nicht beim Container-Build**. Hier wird
  nur konfiguriert, nicht veroeffentlicht.
- `pyproject.toml` nicht anfassen - die Abhaengigkeitsgruppe `docs` legt BE-1 an.

## Pruefung

`mkdocs build --strict` laeuft ohne Warnung durch. `mkdocs serve` zeigt die
Navigation mit allen Seiten.

[[2026-08-31]] Mon 10:48
## Ergebnis (akar-01)

mkdocs.yml mit Material, deutscher Sprache, mike als Versionsprovider, Palette
hell/dunkel mit Systemvorgabe und den Erweiterungen aus dem Plan; dazu zehn
Stumpfseiten nach dem Navigationsbaum.

Pruefung bestanden: `mkdocs build --strict` endet mit Code 0 und ohne WARNING
oder ERROR. `mkdocs serve` liefert unter /docs/ aus und zeigt alle zehn Seiten
in der Navigation, Betrieb als Abschnitt mit vier Unterseiten.

Eine Abweichung von den Vorgaben: MkDocs lehnt ein site_url ohne Schema ab
("The URL isn't valid, it should include the http:// (scheme)"). Deshalb steht
dort https://kaimarkit.example.com/docs/ mit Kommentar - der geforderte Pfad
/docs/ bleibt erhalten, nur der Host ist ein Platzhalter. Wer die Docs unter
einem echten Namen veroeffentlicht, tauscht den Host aus.

pyproject.toml, docker/ und die Betriebsinhalte (DOC-3) blieben unangetastet.
mkdocs-material und mike sind in der pyenv-Umgebung claude-code bereits
vorhanden; die Abhaengigkeitsgruppe docs legt BE-1 an.
