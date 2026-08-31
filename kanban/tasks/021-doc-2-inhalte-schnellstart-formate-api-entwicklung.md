---
id: 21
title: 'DOC-2 · Inhalte: Schnellstart, Formate, API, Entwicklung, Grenzen'
status: done
priority: medium
created: 2026-08-31T10:20:24.247774672+02:00
updated: 2026-08-31T11:28:10.223801721+02:00
started: 2026-08-31T11:27:20.788381319+02:00
completed: 2026-08-31T11:27:20.788381319+02:00
assignee: akar
tags:
    - docs
depends_on:
    - 20
    - 11
class: standard
---

## Ziel

Die Dokumentation, aus der jemand das Werkzeug bedienen kann, ohne den Code zu
lesen.

## Eigene Dateien

- `docs/index.md`, `docs/schnellstart.md`, `docs/formate.md`, `docs/api.md`,
  `docs/entwicklung.md`, `docs/grenzen.md`

## Vorgaben

- Deutsch nach den Prosa-Regeln aus `~/.claude/rules/SPRACHE.md`. Bezeichner,
  Codebeispiele und Variablennamen bleiben englisch.
- `formate.md`: die Matrix aus dem Plan, dazu je Engine ein Satz, wofuer sie taugt
  und wofuer nicht. Ausdruecklich: Pandoc kann PDF nicht lesen.
- `api.md`: jeder Endpunkt mit einem curl-Beispiel, das sich kopieren und
  ausfuehren laesst. Quelle ist `contracts/api.md`.
- `grenzen.md`: was das Werkzeug nicht kann. Mindestens: gescannte PDFs ohne OCR
  liefern wenig; die Zeitgrenze beendet den Wartevorgang, nicht den Thread;
  mehrere Worker halten je eigene Docling-Modelle im Speicher.
- `entwicklung.md`: Aufbau, wie man eine vierte Engine ergaenzt, wie das Board
  benutzt wird.

## Pruefung

`mkdocs build --strict` ohne Warnung. Jeder curl-Aufruf aus `api.md` laeuft gegen
den laufenden Dienst und liefert, was dort steht.


## Ergebnis (akar-08)

Sechs Seiten geschrieben oder vervollstaendigt. `index.md`, `schnellstart.md` und
`entwicklung.md` waren Stuempfe; `formate.md`, `api.md` und `grenzen.md` hatten die
BE-Tickets bereits teilweise gefuellt.

- `index.md` — wofuer das Werkzeug da ist, die drei Engines in je einem Satz, der
  Dienst speichert nichts, Wegweiser in alle Kapitel.
- `schnellstart.md` — `make up` bis zur ersten `.md`, Healthcheck, Antwortarten nach
  `Accept`, Enginewahl, Fehlerfall, `make down`. Mit einem `!!! info`, dass die
  Oberflaeche bisher nur den Gerueststand zeigt (App.vue ist noch die Geruestseite,
  die FE-Bausteine sind nicht eingehaengt) — der curl-Weg ist der, der jetzt laeuft.
- `api.md` — `GET /api/health` fehlte ganz, jetzt mit curl-Beispiel; dazu eine Notiz
  zum Port (Beispiele nennen 8000, der Container veroeffentlicht 8080), der
  gemeinsame Fehlerrumpf und ein Abschnitt zu `/api/openapi.json` und `/api/docs`.
- `grenzen.md` — die drei geforderten Punkte sind jetzt vollstaendig: gescannte PDFs
  ohne OCR, Zeitgrenze beendet den Wartevorgang (stand schon da), je Worker eigene
  Docling-Modelle. Dazu: Bilder werden nicht beschrieben, und was der Dienst gar
  nicht tut.
- `entwicklung.md` — Aufbau, Umgebung, Befehle, Schnittstellen-Dreiklang, eine vierte
  Engine in sieben Schritten, das Board mit Worktree und Ticketschnitt.
- `formate.md` — nur Querverweise ergaenzt, der Rest stand schon.

## Pruefung

`mkdocs build --strict` → EXIT=0, null WARNING/ERROR (die rote Material-Meldung im
Log ist Werbung, keine Buildwarnung). Keine Definitionsliste verwendet, weil
`def_list` in `mkdocs.yml` fehlt (DOC-5).

Jeder curl-Aufruf gegen ein laufendes `uvicorn app.main:app --port 8000` geprueft:
`/api/health` liefert woertlich `{"status":"ok","version":"0.1.0"}`; `/api/capabilities`;
`/api/convert` als Markdown mit `X-Engine` und `Content-Disposition` und als JSON;
`/api/convert/batch` als ZIP und als JSON, mit erzwungenem Fehlschlag (`_errors.txt`
liegt drin) und mit gleichnamigen Dateien (`bericht.md`, `bericht-2.md`);
`unsupported_format` liefert woertlich `Fuer .xyz gibt es keine Engine.`;
`engine_unsuitable` und `engine_unavailable` ebenfalls geprueft. Docling war dabei
nicht installiert, die Docling-Pfade also nur aus dem Code belegt.

## Kein Widerspruch zwischen contracts/api.md und Code

Der Vertrag deckt sich mit den Endpunkten. Drei Beobachtungen fuer sophies Lane,
keine davon in dieser Doku behauptet:

1. `/api/capabilities` meldet `docling: "warming"`, obwohl die Bibliothek fehlt.
   `DoclingConverter.state()` liefert korrekt `unavailable`, aber `meta.py::_state()`
   ruft nur `available()` und macht daraus `WARMING`. Ein dauerhaft fehlendes Docling
   sieht damit aus wie eines, das gleich fertig laedt.
2. Fehlermeldungen nennen den Tempdateinamen statt des Uploads, z. B.
   `Pandoc ist an tmp0mgyapow.epub gescheitert: ...`. Kein Vertragsbruch, aber fuer
   Lesende unbrauchbar.
3. `engines` enthaelt zusaetzlich `passthrough`; das Beispiel im Vertrag zeigt nur die
   drei Engines. Harmlos, aber Vertrag und Antwort koennten sich hier angleichen.

## Ownership-Kollision beim Merge

`docs/entwicklung.md` gehoert laut Ticketschnitt DOC-2, wurde aber von BE-9
(cdd5509) um die Abschnitte Tests und Beispieldateien ergaenzt. Der Merge nach main
kollidierte deshalb. Beide Haelften sind erhalten: Die BE-9-Abschnitte stehen jetzt
hinter "Die Befehle" und vor "Die Schnittstelle steht an drei Stellen".
