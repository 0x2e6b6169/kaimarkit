---
id: 50
title: 'IN-9 · Abnahmefassung: laufender Dienst, im Browser des Hosts pruefbar'
status: done
priority: high
created: 2026-09-01T08:52:15.226215349+02:00
updated: 2026-09-01T11:42:54.319663242+02:00
started: 2026-09-01T11:42:06.323336252+02:00
completed: 2026-09-01T11:42:06.323336252+02:00
assignee: akar
tags:
    - infra
    - release
class: standard
---

## Ziel

Der Nutzer soll kaimarkit auf seinem Rechner starten und im Browser des
Windows-Hosts bedienen koennen. Heute ist der Dienst nur aus WSL heraus geprueft.

## Ausgangslage

INT-2 (#30) hat den Container Ende zu Ende geprueft — mit `curl` aus WSL. Das
belegt den Container, nicht den Weg dorthin. Zwei Annahmen stehen dazwischen und
sind nie geprueft worden:

- `KAIMARKIT_BIND_ADDR` steht auf `127.0.0.1`. Ob Docker Desktop einen so
  gebundenen Port an Windows weiterreicht, hat hier noch niemand nachgesehen.
- Die Oberfläche kommt aus derselben Herkunft wie die API. Ein Browser prueft
  Dinge, die `curl` nicht prueft.

## Eigene Dateien

- `docs/betrieb/lokal.md` (Abschnitt "Docker Desktop unter Windows", neu)

Sonst nichts. `docker/Dockerfile` gehoert IN-8 (#45): Wer beim Bauen auf einen
Fehler stoesst, meldet ihn, statt ihn hier zu beheben.

## Vorgaben

Aus dem **Haupt-Checkout** auf dem Stand von `main` bauen und starten
(`cp docker/.env.example docker/.env`, `make up`), bis
`docker inspect -f '{{.State.Health.Status}}' kaimarkit` `healthy` meldet.

Am Gegenstand pruefen, nicht am Werkzeug: den Textinhalt der Antworten ansehen,
nicht den Statuscode.

Was der Weg ueber Docker Desktop zusaetzlich verlangt, gehoert als eigener
Abschnitt nach `docs/betrieb/lokal.md` — Bindeadresse, Port, unter welcher Adresse
die Oberfläche im Browser des Hosts erscheint. Verlangt er nichts weiter, sagt der
Abschnitt genau das in zwei Saetzen.

Die letzte Meile geht der Nutzer: Ein Subagent in WSL kann keinen Browser unter
Windows bedienen. Deshalb endet dieses Ticket auf `review`, nicht auf `done`, und
die Ticketnotiz enthaelt eine kurze Abnahmeliste — die Adresse und drei Handgriffe,
die der Nutzer nacheinander macht.

Was dabei auffaellt, wird gemeldet und nicht behoben. Daraus schneidet der PO
Tickets.

## Pruefung

- Der Container meldet `healthy`.
- `curl -sf localhost:8080/` liefert das HTML der Oberfläche, nicht nur einen
  Statuscode; `curl -sf localhost:8080/api/capabilities` nennt alle drei Engines.
- Eine Umwandlung von der Kommandozeile liefert sichtbaren Text: das Ergebnis
  enthaelt Woerter aus der Vorlage, nicht nur eine leere Antwort.
- `docs/betrieb/lokal.md` hat den neuen Abschnitt.
- Das Ticket steht auf `review`, der Container laeuft weiter, und die Notiz nennt
  die Adresse und die Abnahmeliste fuer den Nutzer.


---

## Ergebnis (akar-21)

Merge `c478d38`, Zweig `task/50-abnahmefassung`, ein Commit `c3a1d3d`.

### Die Adresse

**<http://127.0.0.1:8080>** — im Browser unter Windows, ohne weitere Einstellung.

`http://localhost:8080` kommt am selben Ziel an, aber nur ueber IPv4. Wer sich die
Frage sparen will, tippt die Zahlen.

### Abnahmeliste — drei Handgriffe

1. **<http://127.0.0.1:8080> oeffnen.** Der Titel im Reiter lautet `kaimarkit`, die
   Dropzone steht da, und die Enginewahl ist mit `auto, markitdown, docling, pandoc`
   gefuellt — die Liste kommt aus `/api/capabilities`, sie belegt also den Weg vom
   Browser zur API.
2. **`backend/tests/fixtures/bild.png` in die Dropzone ziehen, Engine `docling`, OCR
   ausgeschaltet, umwandeln — dann dieselbe Datei noch einmal mit eingeschaltetem
   OCR.** Ohne OCR bleibt das Ergebnis leer, mit OCR steht `Kaimarkit Fixture / Ein
   Bild aus dem Fixturebestand.` in der Vorschau. Das ist BE-13 (#46) am Gegenstand:
   Der Schalter wirkt jetzt auch auf Bilder. Der Lauf mit OCR dauert rund 30 Sekunden.
3. **`backend/tests/fixtures/tabelle.pdf` mit `docling` umwandeln und das Markdown
   herunterladen.** Die Tabelle enthaelt beide Zeilen (`pdf | docling`,
   `odt | pandoc`). Der Download belegt zugleich den Rueckweg ueber den Browser.

### Der Stand, aus dem gebaut ist

Abbild `kaimarkit:local`, ID `25b89531abf8`, gebaut aus dem Haupt-Checkout auf dem
Codestand von **`6f9cafc`** (BE-14). Seither sind nur Board-Commits dazugekommen;
`git diff --name-only 6f9cafc..b9b9aeb` nennt allein `kanban/`.

Der erste Bau lief auf `ed56300` los und war veraltet, bevor er fertig war. Nach
`make down` ist neu gebaut worden. Belegt ist der Codestand nicht am Datum, sondern
am Inhalt: `sha256sum` von `app/converters/docling.py` und `registry.py` im Container
stimmt mit dem Arbeitsbaum ueberein (`3b238dba…` bzw. `a185b322…`), waehrend dieselbe
Datei aus `ed56300` `f175489f…` ergibt.

### Der Weg von Windows nach WSL — belegt, nicht angenommen

Docker Desktop veroeffentlicht den Port **auf Windows selbst**, nicht in der
Distribution. `KAIMARKIT_BIND_ADDR=127.0.0.1` (`docker/.env.example:98`) landet ueber
`ports: "${KAIMARKIT_BIND_ADDR}:${KAIMARKIT_HOST_PORT}:8000"`
(`docker/docker-compose.yml:46`) auf dem Windows-Loopback:

- `netstat.exe -ano` zeigt `TCP 127.0.0.1:8080 ABHOEREN 13628`; PID 13628 ist
  `com.docker.backend`.
- `curl.exe` — ein Windows-Prozess, also der Windows-Netzstack — liefert an
  `http://localhost:8080/api/health` `200 {"status":"ok","version":"0.1.0"}` und an
  `/` das HTML mit `<title>kaimarkit</title>`.
- Ein Multipart-POST aus demselben Windows-Prozess an `/api/convert` liefert
  `{"filename":"seite.html","status":"ok","markdown":"# Kaimarkit Fixture …",
  "engine":"markitdown", …}`. Der Upload-Weg, den der Browser nimmt, ist damit
  geprueft.
- Gegenprobe: `http://[::1]:8080` wird abgewiesen (curl-Exitcode 7), ebenso die
  WSL-Adresse `http://172.31.35.132:8080`. Veroeffentlicht ist allein IPv4-Loopback.
- `localhost` loest Windows auf beide Adressen auf (beide Zeilen in der
  `hosts`-Datei sind auskommentiert, die Aufloesung macht die DNS-Schicht);
  `curl.exe` verbindet sich nach `127.0.0.1`. Deshalb nennt die Doku die Zahlen als
  sichere Adresse.

WSL laeuft im Netzmodus `nat` (`wslinfo --networking-mode`). Fuer diesen Weg spielt
das keine Rolle: Der Listener steht auf Windows, nicht in der Distribution.

### Die Pruefung aus dem Ticketrumpf

- `docker inspect -f '{{.State.Health.Status}}' kaimarkit` -> `healthy`.
- `curl -sf localhost:8080/` -> 552 Byte HTML, `<title>kaimarkit</title>`,
  `<div id="app">`, Verweise auf `/assets/index-D8ohNKuN.js` (318 828 Byte, 200) und
  `/assets/index-CA9HL6HI.css` (13 151 Byte, 200).
- `curl -sf localhost:8080/api/capabilities` -> `engines` nennt alle drei, jede auf
  `ready`: `{"markitdown":"ready","docling":"ready","pandoc":"ready"}`. Dazu 17
  Endungen in `formats`, `ocr_available: true`, `default_engine: auto`.
- Umwandlung mit sichtbarem Text: `bericht.docx` enthaelt laut `word/document.xml`
  die Zeichenketten `Kaimarkit Fixture` und `Ein Absatz aus dem Fixturebestand.`; die
  Antwort liefert genau diese beiden Zeilen als Markdown, mit `x-engine: markitdown`
  und `content-disposition: attachment; filename="bericht.md"`.
- `/docs/` im Container antwortet mit 200 und 20 572 Byte.
- `docs/betrieb/lokal.md` hat den neuen Abschnitt „Docker Desktop unter Windows"
  (Zeilen 50-68), eingefuegt zwischen den drei Schritten und „Pruefen, ob der Dienst
  antwortet".

### Die beiden frischen Korrekturen sind im Abbild

- **BE-13 (#46)** — `bild.png`, Engine `docling`: `ocr=false` -> `markdown` leer
  (8,5 s); `ocr=true` -> `## Kaimarkit Fixture` und `## Ein Bild aus dem
  Fixturebestand-` (32,0 s). Der Schalter wirkt auf Bilder.
- **BE-14 (#47)** — Ein von Hand gesetztes PDF mit 11 Spalten und 14 Zeilen (nach dem
  Muster von `build_fixtures.py:build_pdf`, im Scratchpad, nicht im Repo) macht
  Docling zum Platzhalter: `markdown` = `## Kaimarkit Fixture` plus `<!-- image -->`,
  und `warnings` enthaelt jetzt `Docling hat in breit.pdf ein Bild durch einen
  Platzhalter ersetzt. Sein Inhalt fehlt im Markdown.` Die Warnung aus
  `docling.py:53-70` greift. Die Fixtures im Repo loesen sie nicht aus:
  `tabelle.pdf` liefert unter `docling` die vollstaendige Tabelle und keine Warnung.

### Befunde — gemeldet, nicht behoben

1. **Der Bau dauert 29 Minuten und nutzt den Cache kaum** (Sache von IN-8/#45 und
   IN-10). Beim zweiten Lauf, an dem sich nur `backend/app/` geaendert hatte, liefen
   die Builder-Stufe (Torch, opencv, tree-sitter erneut geladen) **und** die
   Modell-Stufe komplett neu — 1223 s allein fuer `docling-tools models download` im
   ersten Lauf, erneut mehrere Minuten im zweiten. Eine Aenderung an einer
   Python-Datei sollte diese beiden Stufen nicht anfassen.
2. **Der Container gilt schon nach 9 Sekunden als `healthy`.** Falsch ist das nicht,
   aber `docs/betrieb/lokal.md` beschreibt das Warten als den dritten Schritt und
   `/api/capabilities` als „Docling meldet `warming`". Beides war hier nie zu sehen:
   Der erste Healthcheck innerhalb der `start_period` gelang sofort, und
   `capabilities` meldete von Anfang an dreimal `ready`. Ob Docling wirklich schon
   geladen ist oder der Zustand nur so heisst, gehoert nachgesehen — der erste
   Docling-Aufruf brauchte danach 32 Sekunden.
3. **`/api/convert` liefert ohne `Accept: application/json` reines Markdown**, kein
   JSON. So steht es im Vertrag (`contracts/api.md:138-152`), aber
   `docs/betrieb/lokal.md` zeigt nur die Datei-Variante mit `-o`. Wer die Warnungen
   sehen will, braucht `-H 'Accept: application/json'` oder die Kopfzeile
   `X-Warnings`. Ein Satz dazu unter „Pruefen, ob der Dienst antwortet" wuerde helfen.

### Zustand am Ende

Der Container laeuft weiter (`kaimarkit`, `healthy`, Port `127.0.0.1:8080`),
`docker/.env` liegt als Kopie von `docker/.env.example` im Arbeitsbaum. Der Worktree
`.worktrees/task-50` ist entfernt, der Zweig gemergt. Das Ticket steht auf `review`:
Die letzte Meile — der Browser unter Windows — geht der Nutzer.

[[2026-09-01]] Tue 11:42
Vom Nutzer abgenommen (01.09.2026): "Fuer den aktuellen Stand ist #50 okay, das heisst aber nicht, dass wir statisch bleiben."

Die Abnahme lief ueber echte Dokumente, nicht ueber die Abnahmeliste: eine Bahnrechnung (docling, 103,5 s, beide Tabellen vollstaendig) und eine Anmeldung (docling, 326,1 s, drei Platzhalter mit Warnung — die Mehrzahlform der BE-14-Warnung damit am echten Fall belegt). Ein drittes Dokument scheiterte zuerst an der Zeitgrenze von 120 s und lief nach dem Quick-Fix des Nutzers auf 600 s durch.

Der Weg von Windows nach WSL ist damit an echtem Gebrauch belegt, nicht nur an curl. Der Container laeuft weiter; `docker/.env` traegt jetzt die hoehere Zeitgrenze.

Aus der Abnahme sind sechs Befunde als Tickets entstanden: #55, #56, #57, #58, #59, #60. Dazu eine offene Produktfrage, die kein Ticket ist, weil sie dem Nutzer gehoert: ob `engine=auto` fuer `.pdf` weiterhin docling zuerst nennen soll.
