---
id: 30
title: INT-2 · Ende-zu-Ende-Pruefung im Container
status: done
priority: medium
created: 2026-08-31T10:21:44.348462086+02:00
updated: 2026-08-31T17:14:43.928617511+02:00
started: 2026-08-31T17:14:43.374948802+02:00
completed: 2026-08-31T17:14:43.374948802+02:00
assignee: akar
tags:
    - infra
depends_on:
    - 29
    - 26
    - 27
    - 34
    - 38
    - 44
class: standard
---

## Ziel

Belegen, dass das gebaute Image tut, was der Plan verspricht.

## Eigene Dateien

Keine - dieses Ticket prueft und meldet, es baut nicht.

## Vorgaben

Der Abschnitt "Pruefung am Ende" des Plans, vollstaendig durchlaufen:

- pytest mit und ohne `-m slow`
- die curl-Beispiele fuer Einzeldatei, Stapel-ZIP und die Fehlerpfade 413/415/400
- `make up`, dann `/api/health`, `/docs/`, `/docs/versions.json`, `/api/docs`
- `docker compose ... config` ueber alle drei Dateien: kein `${...}`, kein leerer
  Wert
- ein Build mit absolut gesetztem `KAIMARKIT_BUILD_CONTEXT`

Von Hand: ein gescanntes PDF mit und ohne OCR, ein PDF mit breiter Tabelle ueber
MarkItDown und Docling im Vergleich, ein ePub ueber Pandoc, ein Durchlauf im
Browser mit gemischten Dateien.

Nach einem zweiten `make docs-release`: zwischen den Versionen umschalten und
pruefen, dass die Links auf `/docs/<version>/` zeigen und nicht auf die Wurzel.

## Pruefung

Jeder Punkt oben abgehakt. Was nicht gelingt, wird als eigenes Ticket angelegt,
nicht stillschweigend uebergangen.


## Nachtrag aus DOC-2 (#21) und IN-4 (#25)

- `docs/schnellstart.md` enthaelt einen `!!! info`-Kasten, der sagt, dass die
  Oberfläche noch das Geruest ist. Sobald INT-1 (#29) `App.vue` verdrahtet hat,
  gehoert der Kasten weg.
- Die Anmeldung im Browser gegen ein echtes Authelia ist nie gelaufen. IN-4 hatte
  weder Image noch Netz dafuer und hat den Nachweis hierher uebergeben.

[[2026-08-31]] Mon 13:38
PO: depends_on um #34 und #38 ergaenzt. INT-2 prueft das Abbild, das IN-6 gerade veraendert, und die OCR-Sprachen, die DOC-6 gerade korrigiert. Die Reihenfolge steht damit im Board statt in einer Absprache. Entschieden auf akars Meldung hin.

[[2026-08-31]] Mon 14:43
Abgebrochen am 31.08.2026 gegen 14:45 auf Wunsch des Nutzers, nicht wegen eines Fehlers. akar-18 stand beim zweiten vollstaendigen Imagebau (Pruefpunkt "zweites make docs-release, zwischen den Versionen umschalten"), Worktree `.worktrees/task-30` auf Branch `task/30-e2e`, Ankercommit 87ed9d9. Der Build lief nachweislich — der Build-Cache wuchs in 25 Sekunden von 5,3 auf 8,4 GB —, er hing nicht. Grund des Abbruchs ist IN-7 (#44): Dockers Datenplatte liegt auf einem zu 97 Prozent vollen C:, und die Reorganisation haelt Docker an. Deshalb haengt INT-2 jetzt auch per depends_on an #44. **Beim Wiederaufsetzen laeuft INT-2 vollstaendig neu**, nicht ab der Abbruchstelle: Ein Ende-zu-Ende-Bericht ueber einen halb geprueften Zustand belegt nichts. Vorher `git worktree list` pruefen — steht `.worktrees/task-30` noch, laesst er sich weiterverwenden, sonst neu anlegen. Bis zum Abbruch waren gelaufen: pytest mit und ohne -m slow, die curl-Fehlerpfade, `make up`, drei `compose config`-Laeufe und ein Durchgang der Traefik/Authelia-Schicht (Container `kaimarkit` healthy, ohne veroeffentlichten Port — die beabsichtigte Wirkung von IN-3). Keiner dieser Punkte wurde als bestanden gemeldet; alle sind erneut zu belegen.


## Was der abgebrochene Lauf gemeldet hat (kein Nachweis)

akar-18 wurde auf Wunsch des Nutzers gestoppt, nicht wegen eines Fehlers. Seine
letzte Meldung, woertlich sinngemaess: Abbild gebaut, Stack lief durch (`make up`,
alle curl-Pfade, OCR mit und ohne, Browser-Durchlauf, **Authelia-Anmeldung im
Browser erfolgreich**); offen war allein der letzte Punkt, die Pruefung der zwei
`make docs-release`-Versionen im Container.

**Das ist ein Bericht, kein Beleg.** Die Einzelheiten stehen nirgends — keine
Ausgaben, keine Zeilen, kein Anker. Der naechste Lauf faengt vollstaendig neu an
und belegt alles selbst, auch die Authelia-Anmeldung. Der Vermerk steht hier nur,
damit bekannt ist, wie weit es getragen hatte und wo es zuletzt stand: Der Rest
der Kette hatte offenbar funktioniert, der Abbruch kam am letzten Pruefpunkt.

Ankercommit des Laufs: 87ed9d9. Worktree `.worktrees/task-30` bleibt stehen.

[[2026-08-31]] Mon 15:02
Verweis nachgezogen: Der "Abschnitt 'Pruefung am Ende' des Plans" aus den Vorgaben liegt jetzt im Repo, in `ENTWURF.md` (merge c2900a7). Vorher zeigte er auf `~/.claude/plans/…`, also auf eine Datei ausserhalb des Repos und ausserhalb jeder Sicherung. Der Abschnitt selbst ist unveraendert.


## Durchlauf akar-19, 31.08.2026 — vollstaendig neu belegt

Ankercommit `66156e1`, Merge `9017e27`, Branch `task/30-e2e` (entfernt). Aus dem
Lauf von akar-18 wurde nichts uebernommen; jeder Punkt unten ist in diesem Lauf
selbst entstanden.

### Voraussetzung: Docker nach der Reorganisation

`df -h /mnt/c` meldet 184 GB frei (vorher 17). `docker info` laeuft, der Bestand
ist vollstaendig: `kaimarkit:local`, `authelia/authelia:4.38`, `traefik:v3.6`,
beide `postgres`, `wikijs`, `planka`, `alpine`, dazu die vier Container aus dem
Bestand. Nichts fehlte, nichts wurde repariert.

### Was bestanden hat

**Tests.** `pytest -q` -> 107 passed, 3 deselected. `pytest -q -m slow` auf dem
Rechner -> 3 skipped (docling fehlt dort; siehe PROC-4/#49). Im Abbild ausgefuehrt
-> **3 passed** in 46 s.

**Einzelne Datei.** `bericht.docx` -> `content-disposition: attachment;
filename="bericht.md"`, `x-engine: markitdown`, `content-type: text/markdown`, im
Rumpf das erwartete Markdown. Nicht nur 200, sondern der Inhalt geprueft.

**Stapel-ZIP.** vier Dateien -> vier `.md`. Mit einer wirklich scheiternden Datei
(`kaputt.odt`, `.odt` kann nur pandoc, also kein Ausweichen) -> 200, zwei `.md`
und `_errors.txt` mit einer Zeile. Als JSON: `total=3 succeeded=2 failed=1`.
Namenskollisionen: 20-mal dieselbe Datei -> `liste.md` bis `liste-20.md`.

**Fehlerpfade, jeder mit Gegenprobe.**

| Fall | Ergebnis | Gegenprobe |
| --- | --- | --- |
| 413 `file_too_large` | 74-MB-PDF -> 413 | 19-MB-PDF -> 200 |
| 413 `too_many_files` | 21 Dateien -> 413 | 20 Dateien -> 200, ZIP mit 20 |
| 415 `unsupported_format` | `.xyz` -> 415 | — |
| 400 `engine_unsuitable` | `engine=pandoc` auf PDF -> 400 | — |
| 500 `conversion_failed` | beschaedigtes `.odt` -> 500 | — |

Das Ausweichen greift und meldet sich: beschaedigtes PDF bei `engine=auto` ->
docling scheitert, markitdown uebernimmt, der Wechsel steht in `warnings`. Mit
`engine=docling` ausdruecklich -> 500, keine stille Ersetzung.

**Container.** `make up` -> healthy. `/api/health` 200, `/docs/` 200,
`/docs/versions.json` gefuellt, `/api/docs` 200, `/` liefert die SPA.
`/api/capabilities` nennt alle drei Engines als `ready`, `ocr_available: true`.

**compose config** ueber alle drei Dateien: kein `${...}`, kein leerer Wert.
Gegenprobe: `KAIMARKIT_OCR_LANGS` geleert -> `grep` findet
`KAIMARKIT_OCR_LANGS: ""`. Der Test schlaegt also an.

**Absoluter Build-Kontext.** `KAIMARKIT_BUILD_CONTEXT=/home/kai/.../kaimarkit`
gesetzt, `make up` laeuft durch, `KAIMARKIT_DOCKERFILE` bleibt `docker/Dockerfile`.

**OCR von Hand.** Ein gescanntes PDF ohne Textebene, `engine=docling`:
`ocr=true` -> 143 Zeichen erkannt; `ocr=false` -> **0 Zeichen**. Die Gegenprobe
zeigt, dass der Schalter wirkt und nicht etwa eine Textebene gelesen wird.

**Breite Tabelle im Vergleich.** siehe BE-14 (#47) — markitdown liefert sie
vollstaendig, docling ersetzt sie durch `<!-- image -->`.

**ePub ueber Pandoc.** `buch.epub` -> `engine: pandoc`, 32 ms, erwartetes Markdown.

**Browser, gemischte Dateien.** Chrome kopflos ueber das DevTools-Protokoll, vier
Dateien in die Dropzone: `breit.pdf` fertig (docling, 17379 ms), `buch.epub`
fertig (pandoc, 27 ms), `bericht.docx` fertig (markitdown, 35 ms), `kaputt.odt`
fehlgeschlagen mit lesbarer Meldung in der eigenen Zeile. Die `aria-live`-Region
sagte jeden Schritt an und schloss mit "Alle Dateien sind fertig: 3 gelungen, 1
fehlgeschlagen." Vorschau, Herunterladen je Zeile und die ZIP-Schaltflaeche sind
da; Gegenprobe, dass die Vorschau wirklich rendert: bei `liste.csv` steht ein
`<table>` im DOM, bei `breit.pdf` keines — weil docling keine Tabelle geliefert
hat, nicht weil die Vorschau nichts kann.

**Zwei Dokumentationsversionen.** `mike deploy 0.1`, dann Aenderung, dann
`0.2`. Im Abbild: `/opt/kaimarkit/docs` enthaelt `0.1`, `0.2`, `latest`,
`versions.json`. Das Auswahlmenue, im Browser gelesen, nennt beide und verlinkt
`http://127.0.0.1:8080/docs/0.2/` und `/docs/0.1/` — **unter `/docs/`, nicht in der
Wurzel**. Das ist der Punkt, an dem `site_url` in `mkdocs.yml` haengt. Gegenprobe
am Inhalt: `/docs/0.1/schnellstart/` enthaelt noch den alten Geruest-Kasten,
`/docs/0.2/` und `/docs/latest/` nicht mehr. Die Versionen unterscheiden sich also
wirklich.

**Traefik-Schicht.** Container haengt in `traefik-web`, `ports=[8000/tcp]` — keine
Veroeffentlichung auf dem Host. Vorher, mit der Basisdatei allein,
`127.0.0.1:8080->8000/tcp`. `ports: !reset []` wirkt. Beide Router `enabled`,
Prioritaet 100 gegen 29.

**Authelia im Browser — der Nachweis, den IN-4 (#25) hierher uebergeben hat.**
Gegen Authelia 4.38.19 hinter Traefik 3.6, beides als Wegwerf-Aufbau ausserhalb des
Repos (das Repo startet Authelia bewusst nicht mit):

1. `https://kaimarkit.example.com/` ohne Sitzung -> 302 auf
   `https://auth.example.com/?rd=https%3A%2F%2Fkaimarkit.example.com%2F&rm=GET`
2. Anmeldung mit Benutzername und Passwort im Formular -> Ruecksprung auf
   `https://kaimarkit.example.com/`, Titel `kaimarkit`, Vue eingehaengt, Dropzone
   da, Enginewahl `auto, markitdown, docling, pandoc` aus `/api/capabilities`
   geladen — der Aufruf kam also durch dieselbe Middleware
3. `/api/health` im angemeldeten Browser -> `200 {"status":"ok",...}`
4. Gegenprobe: Sitzungscookie geloescht -> `/api/health` liefert die
   Weiterleitung, ein Neuladen landet wieder auf der Anmeldeseite

**Der Schalter `KAIMARKIT_API_MIDDLEWARES`**, wie `docs/betrieb/authelia.md` ihn
beschreibt: leer gesetzt -> Router `kaimarkit-api` bleibt `enabled` ohne
Middleware, `/api/health` -> 200, `/` weiterhin -> 302. Wieder auf
`kaimarkit-auth@docker` -> `/api/health` wieder 302.

### Was in diesem Merge an der Dokumentation korrigiert wurde

- `docs/schnellstart.md`: Der Kasten "Die Oberflaeche wird noch zusammengesetzt"
  ist weg. INT-1 (#29) hat `App.vue` verdrahtet, und der Browserlauf oben belegt
  es. An seiner Stelle steht, was die Oberflaeche wirklich tut.
- `docs/betrieb/authelia.md`: Der Kasten "Die Anmeldung im Browser ist noch nicht
  erprobt" ist weg, ersetzt durch das Ergebnis des Durchlaufs.

`docker/.env.example` und `docs/betrieb/konfiguration.md` wurden gegeneinander
gehalten (Konvention 6): Jede der 32 Variablen aus der einen steht in der anderen.
Die drei zusaetzlichen Namen dort — `DOCLING_ARTIFACTS_PATH`, `HF_HOME`,
`HF_HUB_OFFLINE` — sind die vom Abbild gesetzten und ausdruecklich so vermerkt.
Nichts zu aendern.

### Was nicht gelang — als eigene Tickets

- **#45 IN-8** (high) — Der Bau scheitert, wenn der Kontext ein Git-Worktree ist.
  `git config --global --add safe.directory /src` endet mit 128, weil `.git` dort
  eine Datei mit `gitdir:`-Zeiger ist. Trifft die Arbeitsweise dieses Projekts:
  kein Subagent kann aus seinem eigenen Verzeichnis bauen. INT-2 ist ueber
  `KAIMARKIT_BUILD_CONTEXT` auf den Haupt-Checkout ausgewichen.
- **#46 BE-13** (high) — `ocr` und `KAIMARKIT_OCR_LANGS` wirken nur auf PDF. Bei
  Bildern laeuft die Texterkennung immer und mit Doclings Vorgabemaschine
  (RapidOCR), nicht mit dem in BE-12 (#37) ausdruecklich gewaehlten EasyOCR.
  Beleg: dieselbe Seite als PDF -> `ocr=false` liefert 0 Zeichen, als PNG ->
  `ocr=false` liefert denselben Text wie `ocr=true`.
  Ursache: `docling.py:80-82`, `format_options` deckt nur `InputFormat.PDF` ab.
- **#47 BE-14** (medium) — Docling ersetzt die Tabelle aus `breit.pdf` durch
  `<!-- image -->`, meldet `status: ok` und laesst `warnings` leer. markitdown
  liefert dieselbe Tabelle vollstaendig. Der Vertrag sieht eine Platzhalterwarnung
  vor (`contracts/api.md:158`), gebaut ist sie nicht (`docling.py:86`).
- **#48 BE-15** (low) — Fehlermeldungen reichen den internen Tempfile-Pfad bis in
  `detail`, `_errors.txt` und die Browserzeile durch.
- **#49 PROC-4** (low) — `pytest -q -m slow` ueberspringt auf dem
  Entwicklungsrechner still und meldet 0. `CLAUDE.md` und das Makefile
  versprechen dort Docling-Abdeckung, die es nicht gibt.

### Aufgeraeumt

Der Wegwerf-Aufbau (Traefik, Authelia, Netz `traefik-web`, `curlimages/curl`,
`alpine/git`) ist entfernt; Abbild-, Container- und Netzbestand stehen wieder
genau wie vor dem Lauf. Der Zweig `gh-pages` aus den beiden `mike deploy` ist
**geloescht**: 0.1 und 0.2 waren Pruefstaende, keine Veroeffentlichungen, und ein
stehengelassener Zweig haette jedem spaeteren Bau diese Fassung statt der aktuellen
untergeschoben. Das Repo hat nun wieder keinen `gh-pages`, wie vor dem Lauf.
