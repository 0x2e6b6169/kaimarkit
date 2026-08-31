---
id: 20
title: 'DOC-1 · MkDocs, Material-Theme und mike: mkdocs.yml, Navigation, Seitengeruest'
status: todo
priority: high
created: 2026-08-31T10:20:23.564339142+02:00
updated: 2026-08-31T10:30:46.278297465+02:00
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
