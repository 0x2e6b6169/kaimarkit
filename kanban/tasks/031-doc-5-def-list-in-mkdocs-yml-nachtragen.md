---
id: 31
title: DOC-5 · def_list in mkdocs.yml nachtragen
status: done
priority: low
created: 2026-08-31T11:16:04.308070874+02:00
updated: 2026-08-31T11:47:49.930792644+02:00
started: 2026-08-31T11:41:56.427926704+02:00
completed: 2026-08-31T11:46:30.210103797+02:00
assignee: akar
tags:
    - docs
class: standard
---

## Ziel

`markdown_extensions` in `mkdocs.yml` kennt `def_list` nicht. Definitionslisten
rendern deshalb als Absaetze mit fuehrendem Doppelpunkt, und `mkdocs build --strict`
schlaegt dabei nicht an — der Fehler faellt erst beim Ansehen der Seite auf.

Gefunden in DOC-3 (#27) beim Beschreiben der Optionen von
`KAIMARKIT_API_MIDDLEWARES`. Dort ist die Stelle umformuliert, die Luecke bleibt.

## Eigene Dateien

- `mkdocs.yml`

## Vorgaben

`def_list` in `markdown_extensions` aufnehmen. Pruefen, ob weitere Erweiterungen
aus dem Material-Theme fehlen, die das Seitengeruest schon benutzt.

## Pruefung

Eine Testseite mit Definitionsliste rendert als `<dl>`, nicht als Absatz.
`mkdocs build --strict` endet mit 0 und ohne Warnung.

## Ergebnis

Nur `def_list` ergaenzt, dazu ein zweizeiliger Kommentar in `mkdocs.yml`, der
festhaelt, warum die Erweiterung noetig ist und warum `--strict` ihr Fehlen nicht
meldet.

**Erweiterungssuche.** Alle zehn Seiten unter `docs/` nach Markdown-Konstrukten
durchsucht statt nach der Material-Liste geraten. Gefunden: Admonitions (`!!! info`,
`note`, `warning`, `danger` auf sechs Seiten), Tabellen (sieben Seiten), Codebloecke
und Autolinks. Alles davon ist abgedeckt — `admonition`, `tables`,
`pymdownx.highlight`, `pymdownx.superfences`. Nicht vorhanden und deshalb auch nicht
ergaenzt: Fussnoten, Aufgabenlisten, einklappbare Admonitions (`???`), Icons,
Tastenkuerzel, Code-Annotationen, Snippets, Abkuerzungen. `attr_list` und
`pymdownx.tabbed` stehen bereits in der Konfiguration, ohne dass eine Seite sie
benutzt; beide bleiben unangetastet.

**Pruefung.** Testseite `docs/zz-deflist-probe.md` mit zwei Definitionspaaren gebaut
und das erzeugte HTML unter `site/` durchsucht:

```
<dl>
<dt><code>KAIMARKIT_API_MIDDLEWARES</code></dt>
<dd><p>Die Middlewares des <code>/api</code>-Routers.</p></dd>
<dt>Leer</dt>
<dd><p>Gibt die API frei.</p></dd>
</dl>
```

Gegenprobe mit auskommentiertem `def_list`: `grep -c '<dl>'` liefert 0, im Absatz
steht `:   Die Middlewares des …` — und `mkdocs build --strict` endet trotzdem mit 0.
Damit ist belegt, dass `--strict` diesen Fehler nicht findet.

Testseite und `site/` wieder entfernt, `git status` sauber. Abschliessender
`mkdocs build --strict` ohne Testseite: Exit 0, keine Warnung, keine Fehlermeldung
(die Material-Notiz zu MkDocs 2.0 ist ein Hinweis des Themes, keine Build-Warnung).

**Seiten, die von einer Definitionsliste profitieren wuerden.** Fremdes Eigentum,
deshalb nur gemeldet: `docs/betrieb/konfiguration.md` Zeile 118-124 — die Erklaerung
zu `AUTHELIA_VERIFY_URL` und `KAIMARKIT_API_MIDDLEWARES` steht als Fliesstext hinter
der Tabelle, weil DOC-3 die Definitionsliste aufloesen musste. Sonst faellt nichts
auf; die uebrigen Aufzaehlungen sind als Tabelle oder Liste richtig aufgehoben.


## Muster fuer kuenftige Doku-Pruefungen

Ein Nachweis, der den Fehler schon einmal durchgelassen hat, ist kein Nachweis.
`mkdocs build --strict` endet bei fehlendem `def_list` mit 0 und ohne Warnung —
wer damit prueft, prueft das Werkzeug statt der Sache.

Richtig ist, im erzeugten HTML unter `site/` nach dem erwarteten Element zu
greppen, hier `<dl>`. Dazu gehoert die Negativkontrolle: einmal ohne die
Erweiterung bauen und zeigen, dass `--strict` weiterhin schweigt. Erst beides
zusammen belegt, dass die Aenderung wirkt.

Uebertragbar auf jede Doku-Pruefung, deren Fehlerbild sich erst beim Rendern
zeigt.
