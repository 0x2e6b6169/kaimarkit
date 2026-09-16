---
id: 139
title: IN-22 · GitHub Action veroeffentlicht die Dokumentation auf GitHub Pages
status: done
priority: medium
created: 2026-09-16T09:16:27.448025802+02:00
updated: 2026-09-16T09:17:28.993040187+02:00
started: 2026-09-16T00:00:00Z
completed: 2026-09-16T00:00:00Z
assignee: akar
tags:
    - docs
    - ci
class: standard
---

## Ziel

Die Dokumentation erscheint ohne Handgriff im Netz. Ein Tag `v*` veröffentlicht sie
auf GitHub Pages; der Zweig `gh-pages` bleibt die eine Quelle, aus der auch die
Docs-Stufe des Abbilds liest.

## Eigene Dateien

- `.github/workflows/docs.yml`
- `mkdocs.yml` (Abschnitt `site_url` und der Eintrag `mike` unter `plugins`)
- `docs/entwicklung.md` (Abschnitt „Die Dokumentation veröffentlichen")
- `README.md` (Absatz „Das Handbuch", nur der Verweis auf die veröffentlichte Fassung)
- `CLAUDE.md` (die Zeile zu `docs-release` im Befehlsblock)

## Vorgaben

- Zwei Aufträge in einem Workflow: `mkdocs build --strict` bei jedem Push auf `main`,
  Veröffentlichen nur bei Tag `v*` oder auf Zuruf mit Angabe der Fassung.
- Veröffentlicht wird mit mike, nicht mit `actions/deploy-pages`: Die Fassungen
  liegen im Zweig `gh-pages`, und von dort liest auch das Abbild.
- Aus `v0.3.6` wird die Fassung `0.3`, Alias `latest`, Standard `latest`.
- Die Abhängigkeiten kommen aus der Gruppe `docs` in `backend/pyproject.toml` —
  gelesen wie in der Docs-Stufe des Abbilds, nicht über `pip install backend[docs]`;
  das Extra brächte Docling samt Torch auf den Läufer.
- Pages liefert den Zweig `gh-pages` aus, Pfad `/`.

## Prüfung

1. `mkdocs build --strict` endet ohne WARNING und ERROR.
2. Der Lauf der Action endet grün, und `gh-pages` führt danach die Fassung `0.3`.
3. `https://0x2e6b6169.github.io/kaimarkit/` antwortet mit 200, `versions.json` nennt
   `0.3` mit Alias `latest`.
4. Der kanonische Verweis zeigt auf eine Adresse, die es gibt, und das Versionsmenü
   von Material bleibt in der App-Konfiguration stehen (`"version"` nicht `null`).

## Ergebnis (nachgetragen am 16. September 2026)

Gebaut wurde außerhalb der Lane: Der Nutzer hat die Sitzung `kaimarkit-7a` direkt
beauftragt, kein Subagent, kein Claim, kein Ticket vor der Arbeit. Dieses Ticket
trägt den Vorgang nach, damit er auf dem Board steht und nicht nur im Verlauf.

Die Merges auf `main`, in dieser Reihenfolge:

- `c16b239` — der Workflow, dazu die Abschnitte in `docs/entwicklung.md`, `README.md`
  und `CLAUDE.md`
- `3fc7295` — `actions/checkout@v5` und `actions/setup-python@v6`; die Fassungen davor
  laufen auf einem abgekündigten Node
- `c4624d5` — `site_url` auf die Pages-Adresse, Abhängigkeiten wie im Abbild gelesen
- `c6ff241`, `404c7d3` — zwei Anläufe an der kanonischen Adresse, siehe unten

Pages steht auf Zweig `gh-pages`, Pfad `/`, gesetzt über die API; der Zweig entstand
beim ersten Lauf der Action.

Prüfung bestanden. `mkdocs build --strict` endet ohne WARNING und ERROR, in beiden
Läufen — mit mike und ohne. Die Action ist viermal grün durchgelaufen.
`https://0x2e6b6169.github.io/kaimarkit/` antwortet mit 200, `versions.json` nennt
`0.3` mit Alias `latest`, `/latest/nutzer/dateien-wandeln/` mit 200. Der kanonische
Verweis zeigt auf `…/kaimarkit/latest/…`, die App-Konfiguration führt
`provider: mike`, und kein Verweis auf `version-select` steht im HTML.

Zwei Anläufe hat die kanonische Adresse gekostet, beide Gründe stehen ausführlich in
DOC-1 (#20): mike hängt sein Plugin beim Veröffentlichen selbst ein, und
`version_selector: false` nimmt Material sein Versionsmenü. Kurzzeitig stand deshalb
`/kaimarkit/latest/0.3/` als kanonische Adresse auf der veröffentlichten Seite.

Die Vorgabe aus DOC-1, `site_url` müsse den Pfad `/docs/` führen, ist damit
gegenstandslos; die Berichtigung steht in #20.
