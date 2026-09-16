---
id: 20
title: 'DOC-1 · MkDocs, Material-Theme und mike: mkdocs.yml, Navigation, Seitengeruest'
status: done
priority: high
created: 2026-08-31T10:20:23.564339142+02:00
updated: 2026-09-16T09:11:20.993693463+02:00
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

## Berichtigung (16. September 2026): site_url

Im Rumpf stand als Vorgabe: **`site_url: /docs/`** — der Unterpfad, nicht die
Wurzel, sonst verlinke der Versions-Dropdown auf `/0.3/` statt `/docs/0.3/` und
laufe ins Leere. Die Begründung stimmt nicht.

mkdocs-material baut die Einträge des Versionsmenüs zur Laufzeit aus der Basis der
geöffneten Seite (`new URL("../versions.json", config.base)`); auch die Zuordnung
derselben Seite in der anderen Fassung läuft über den gemeinsamen Präfix der
sitemap.xml und ist gegen einen anderen Pfad unempfindlich. Im fertigen Bau steht
der Wert aus `site_url` an genau zwei Stellen: im `<link rel="canonical">` jeder
Seite und in der sitemap.xml. Gezählt am Bau vom 16. September: 14 kanonische
Verweise, 14 Einträge in der sitemap, sonst keine Fundstelle. Die übrigen Treffer
auf `kaimarkit.example.com` stehen im Fließtext von Traefik und Authelia und
meinen den Namen, unter dem jemand seinen eigenen Dienst betreibt.

Seit dem 16. September veröffentlicht die Action `docs` die Seiten auf GitHub
Pages unter https://0x2e6b6169.github.io/kaimarkit/. Derselbe Zweig `gh-pages`
speist die Docs-Stufe des Abbilds, die unter `/docs/` ausliefert. Zwei Adressen,
ein Bau — `site_url` nennt nur eine, und das ist die öffentliche: Ein kanonischer
Verweis zeigt auf die veröffentlichte Kopie, nicht auf einen Platzhalter-Host, den
es nie gab.

In `mkdocs.yml` steht deshalb jetzt `site_url: https://0x2e6b6169.github.io/kaimarkit/`
und dazu das mike-Plugin mit `canonical_version: latest`, das die Fassung beim Lauf
von mike anhängt — ohne das zeigte der kanonische Verweis auf eine Adresse ohne
Fassung, die es dort nicht gibt. `version_selector: false`, weil Material seinen
eigenen Wähler mitbringt.

Die Vorgabe "Unterpfad statt Wurzel" ist damit gegenstandslos. Wer sie wieder
einsetzt, macht den kanonischen Verweis falsch, ohne am Versionsmenü etwas zu
ändern.

## Nachtrag (16. September 2026): mike hängt die Fassung selbst an

Die Berichtigung oben nannte als Konfiguration `canonical_version: latest` zusammen
mit `version_selector: false`. Das zweite Stück war falsch. Zwei Eigenheiten stecken
dahinter, und beide fallen erst am veröffentlichten Stand auf.

mike hängt sein Plugin beim Veröffentlichen selbst ein, sobald die Konfiguration es
nicht aufführt (`mkdocs_utils.inject_plugin`). In jeder von mike gebauten Fassung
steht die Version deshalb schon im `site_url` — auch ohne Eintrag in `mkdocs.yml`.
Ein `site_url`, das `latest/` selbst mitbringt, ergibt darum `/kaimarkit/latest/0.3/`.
Genau das stand kurzzeitig auf der veröffentlichten Seite.

`version_selector: false` wiederum schaltet nicht nur den Wähler von mike ab, sondern
auch den von Material: Dessen Vorlage setzt `_.version` nur, solange
`not mike or mike.config.version_selector` gilt. Im Bau zeigt sich das als
`"version": null` in der App-Konfiguration, im Browser fehlt das Menü ersatzlos.

Richtig ist `site_url` ohne Fassung im Pfad, dazu das Plugin mit einer einzigen
Einstellung:

    plugins:
      - mike:
          canonical_version: latest

Belegt am veröffentlichten Stand: `/latest/` und `/0.3/` nennen beide
https://0x2e6b6169.github.io/kaimarkit/latest/… als kanonische Adresse, die
App-Konfiguration führt `provider: mike`, und kein Verweis auf `version-select`
steht im HTML.
