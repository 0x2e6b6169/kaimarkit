# Entwicklung

Wie das Projekt aufgebaut ist, wie man eine weitere Engine ergänzt und wie das
Board die Arbeit verteilt.

## Der Aufbau

Ein Repository, zwei Anwendungen, ein Abbild. Das Backend liefert die API und hängt
das gebaute Frontend und diese Dokumentation als statische Dateien daneben ein.

| Verzeichnis | Was darin liegt |
| --- | --- |
| `backend/app/` | Die FastAPI-Anwendung: `main.py`, `config.py`, `models.py`, `errors.py`, die Router unter `api/` und die Engines unter `converters/`. |
| `backend/tests/` | pytest. Was die Docling-Modelle braucht, ist mit `slow` markiert. |
| `frontend/src/` | Vue 3 mit TypeScript und Tailwind. Komponenten, Composables, der API-Client und der Download. |
| `contracts/` | `api.md`, der verbindliche Wortlaut der Schnittstelle. |
| `docker/` | Dockerfile, die drei Compose-Schichten und `.env.example`. |
| `docs/` | Diese Seiten. `mkdocs.yml` steht in der Wurzel. |
| `kanban/` | Das Board. |

Drei Dinge hängt `main.py` ein, und die Reihenfolge entscheidet, weil die letzte
Einhängung alles auffängt, was übrig bleibt: `/api` für die Router, `/docs` für
diese Dokumentation, `/` für das Frontend. Deshalb liegt FastAPIs eigene Oberfläche
unter `/api/docs`. Fehlt eines der beiden statischen Verzeichnisse, hängt das
Backend es nicht ein und läuft trotzdem — genau das ist der Zustand in der
Entwicklung.

## Die Umgebung einrichten

Python läuft nie global, sondern in der pyenv-Umgebung `claude-code`:

```bash
pyenv activate claude-code
cd backend && pip install -e '.[dev,docs]'
cd ../frontend && npm install
```

Die Gruppe `docs` bringt MkDocs und mike. Sie steht getrennt von der Laufzeit,
damit MkDocs nicht im Container landet.

## Die Befehle

Alle `make`-Ziele laufen aus dem Wurzelverzeichnis; `make help` listet sie.

```bash
make dev             # Backend auf :8000 und Frontend auf :5173, beide mit Reload
make test            # pytest ohne die Docling-Modelle
make test-slow-image # dieselben Tests mit Docling, im Abbild, dauert
make lint            # ruff über das Backend
make docs-serve      # Vorschau dieser Seiten auf :8001
```

Im Frontend kommen `npm run typecheck` und `npm run test` dazu. Der Dev-Server
schickt `/api` per Proxy an `localhost:8000`; das Frontend braucht also ein
laufendes Backend.

```bash
cd backend && uvicorn app.main:app --reload    # in einem Fenster
cd frontend && npm run dev                     # im anderen
```

Welche Engines dabei zur Wahl stehen, hängt daran, was in der Umgebung installiert
ist. Fehlt eine, meldet `/api/capabilities` sie als `unavailable`, und die Auswahl
bietet sie nicht an — die Oberfläche verspricht nie mehr, als der Dienst halten
kann.

Das Archiv baut das Frontend selbst, im Browser und nicht über
`/api/convert/batch`. Die Ergebnisse liegen dort ohnehin schon; sie für das Paket
ein zweites Mal durch eine Engine zu schicken wäre doppelte Arbeit. Die Namensregeln
im Archiv sind deshalb in `frontend/src/download.ts` nachgebaut und stammen aus
`backend/app/packaging.py`.

## Das Abbild bauen

`make build` baut nur, `make up` baut und startet. Der erste Bau installiert Torch
und Docling und lädt anschließend die Docling-Modelle herunter; wie viel davon ein
zweites Mal anfällt, entscheidet die Schichtung im Dockerfile.

Diese beiden Schritte kosten fast die ganze Zeit — gemessen 210 und 173 Sekunden.
Beide hängen allein an `backend/pyproject.toml`. Wer nur Quelltext ändert, bekommt
sie aus dem Cache zurück: 86 Sekunden für einen Bau, der vorher 485 gebraucht hat.
Wer eine Abhängigkeit ergänzt, bezahlt sie zu Recht ein zweites Mal.

Damit das aufgeht, darf nichts in den Build-Kontext geraten, was sich bei jedem
Testlauf ändert. `.dockerignore` schließt `__pycache__`, `.pytest_cache` und
`.ruff_cache` deshalb mit dem Präfix `**/` aus. Das Präfix ist nötig: Ein Muster
ohne Schrägstrich vergleicht nur die oberste Ebene des Kontextes und ließe
`backend/app/__pycache__` durch.

## Tests

Die Suite läuft aus `backend/` heraus, in der pyenv-Umgebung `claude-code`:

```bash
pytest -q -rs          # der Standardlauf, ohne Docling
pytest -q -rs -m slow  # nur die Tests, die die Docling-Modelle brauchen
```

Der Standardlauf blendet die Marke `slow` aus; das steht in `backend/pyproject.toml`
und gilt damit auch für jeden Aufruf ohne Argumente. Wer `-m slow` angibt,
überschreibt die Einstellung und bekommt genau die ausgeblendeten Tests. Sie laden
die Modelle und dauern deshalb; ohne Docling überspringen sie sich.

Genau deshalb belegt der zweite Aufruf auf dem Entwicklungsrechner nichts. Docling
steht nicht in der pyenv-Umgebung, sondern nur im Abbild; der Lauf meldet lauter
Übersprungenes und Rückgabewert 0. Wirklich laufen die Tests unter
`make test-slow-image`. Das Ziel startet das gebaute Abbild, hängt `backend/` lesend
hinein, installiert dort pytest und httpx und wirft den Container danach weg. Ein
laufender Dienst bleibt unberührt; `make build` muss vorher gelaufen sein.

`-rs` gehört an jeden Aufruf. Der Schalter nennt jeden übersprungenen Test mit
Grund. Ohne ihn fällt eine fehlende Abhängigkeit nur als kleinere Sammelzahl auf,
denn `pytest.importorskip` auf Modulebene macht aus einem ganzen ausgefallenen Modul
eine einzige Zeile. Die pyenv-Umgebung teilen sich alle Lanes; wer eine Zahl
weitergibt, nennt deshalb die Sammelzahl mit.

Die meisten Enginetests arbeiten mit Attrappen und prüfen den Adapter. Die
Smoketests in `backend/tests/test_converters.py` tun das Gegenteil: Sie lassen jede
Engine eine echte Datei lesen und prüfen, dass der erwartete Textbaustein im
Markdown steht und die richtige Engine gearbeitet hat.

## Beispieldateien

Unter `backend/tests/fixtures/` liegt je eine möglichst kleine Datei für PDF, docx,
epub, pptx, xlsx, HTML, CSV, odt und PNG. Alle enthalten den Baustein
`Kaimarkit Fixture`, auf den sich die Smoketests verlassen.

Ein zweites PDF kommt dazu: `breit.pdf` setzt elf Spalten auf vierzehn Zeilen.
Diese Form ordnet Docling als Bild ein und ersetzt sie durch einen Platzhalter —
der Fall, den der Adapter meldet. Der Test dazu braucht die Modelle und steht
deshalb hinter der Marke `slow`.

Die Dateien sind selbst erzeugt, keine fremden Inhalte. `build_fixtures.py` im selben
Verzeichnis baut sie neu:

```bash
python tests/fixtures/build_fixtures.py
```

Acht der zehn Dateien entstehen mit der Standardbibliothek — die OOXML- und
ODF-Formate sind von Hand geschriebene ZIP-Archive, die beiden PDF ein von Hand
gesetzter Inhaltsstrom mit gezeichneter Tabelle. Nur `tabelle.xlsx` braucht openpyxl
und `bild.png` braucht Pillow; beide Pakete kommen mit `markitdown[all]`.

Fehlt ein Paket aus `markitdown[all]`, überspringt sich der betroffene Smoketest,
statt zu scheitern — im Skelett ohne Extras bleibt so nur die Prüfung übrig, die
dort auch laufen kann.

## Die Schnittstelle steht an drei Stellen

`contracts/api.md`, `backend/app/models.py` und `frontend/src/types.ts` beschreiben
dieselbe Schnittstelle. Wer eine der drei Dateien ändert, ändert alle drei im selben
Commit. Sonst laufen Backend und Frontend auseinander, ohne dass es jemand bemerkt —
und zwar so lange, bis eine Antwort ein Feld enthält, das der Client nicht kennt.

Verbindlich ist `contracts/api.md`. Weicht der Code davon ab, ist der Code falsch.

## Eine vierte Engine ergänzen

Die Engines sind hinter dem Protokoll `Converter` in
`backend/app/converters/base.py` versteckt. Außerhalb von `converters/` importiert
nichts `markitdown` oder `docling` und ruft nichts `pandoc` auf. Wer diese Kapselung
einhält, ergänzt eine Engine in sieben Schritten.

**1. Das Modul anlegen.** `backend/app/converters/<name>.py` mit einer Klasse, die
`name`, `extensions`, `available()` und `convert()` mitbringt, und einer Funktion
`get_converter()` auf Modulebene. Mehr verlangt das Protokoll nicht.

**2. Die Bibliothek verzögert importieren.** Der Import gehört in die Funktion, die
ihn braucht, nicht an den Dateikopf. Nur so lässt sich das Modul auch ohne die
Bibliothek laden, und ein fehlendes Paket endet in `EngineUnavailable` statt in
einem `ImportError` beim Start des Dienstes.

**3. Fehler übersetzen.** Jede Ausnahme der Bibliothek wird zu einer Klasse aus
`errors.py`: `EngineUnavailable`, wenn die Engine nicht arbeiten kann,
`EngineFailed`, wenn sie an dieser Datei gescheitert ist. Bibliotheksspezifische
Fehler dringen nicht bis in die API.

**4. `available()` darf nicht werfen.** Die Registry fragt damit ab, ob die Engine
jetzt einsatzbereit ist, und `/api/capabilities` baut darauf seine Auskunft. Braucht
die Engine eine Vorbereitung wie Docling seine Modelle, meldet sie so lange `False`
und lädt im Hintergrund. Der Lifespan in `main.py` stößt dieses Laden beim Hochfahren
an: Er ruft `start_warmup()` im Adaptermodul auf, und der Aufruf kehrt sofort zurück,
weil er nur einen Daemon-Thread startet. `/api/health` wartet deshalb nie auf die
Modelle, und `state()` meldet `warming`, bis der Konverter steht. Wer eine Engine mit
Vorbereitung ergänzt, hängt sie ebenso in den Lifespan ein.

**5. Sich in die Registry eintragen.** In `backend/app/converters/registry.py` kommt
der Name in `ENGINE_NAMES`, und in `PREFERENCES` steht er bei jeder Endung, die er
bedienen soll — dort, wo er zum Zug kommen soll, denn die Reihenfolge ist die
Präferenz. Die Registry lädt das Modul erst beim ersten Zugriff.

**6. Die Abhängigkeit nachziehen.** Ein Python-Paket gehört nach
`backend/pyproject.toml`, ein Programm in `docker/Dockerfile`. Braucht die Engine
eine Einstellung, kommt sie als `KAIMARKIT_*`-Variable in `config.py`, in
`docker/.env.example` und in [Konfiguration](betrieb/konfiguration.md) — die drei
gehören zusammen.

**7. Prüfen und beschreiben.** Ein Test unter `backend/tests/` mit einer Attrappe
statt der echten Bibliothek; was die echten Modelle braucht, bekommt die Markierung
`slow`. Und die Matrix in [Formate](formate.md) nennt danach die neue Engine, sonst
weiß niemand, dass es sie gibt.

## Dark Mode und die Farbpalette

Der dunkle Modus hat keinen Schalter. Er folgt der Einstellung des Systems, und
alles dazu steht in `frontend/src/style.css`. Dort steht keine zweite Gestaltung,
sondern eine neue Belegung: Tailwind 4 übersetzt jede Farbklasse in eine Variable —
aus `bg-white` wird `var(--color-white)`, aus `text-slate-600` wird
`var(--color-slate-600)` —, und der Block unter `prefers-color-scheme: dark` belegt
diese Variablen um. Damit kippen alle Flächen und alle Schriften auf einmal, ohne
dass eine Komponente davon weiß. Der Block steht außerhalb jeder `@layer` und
schlägt deshalb die Vorgaben aus `@layer theme`. Wer eine Ansicht ergänzt, schreibt
also gewöhnliche Farbklassen, und der dunkle Modus stellt sich von selbst ein. Eine
`dark:`-Klasse braucht nur, wer dort etwas anderes will als das Gegenstück der
hellen Ansicht; im ganzen Frontend tut das bisher allein `MarkdownPreview.vue`.

Dafür gilt eine Bedingung. Wer eine Farbklasse ergänzt, liest vorher
`frontend/src/style.css`, denn jede Stufe der Skala dient dort genau einer Sache.
`white`, `slate-50`, `slate-100` und `slate-200` füllen Flächen. `slate-300`,
`slate-400` und `slate-700` zeichnen Linien. `slate-500` und `slate-600` setzen
Schrift. Die Akzentfarben sind ebenso aufgeteilt: `sky-50`, `red-50` und `amber-50`
füllen, `sky-500`, `red-300` und `amber-300` zeichnen, `sky-700`, `sky-900`,
`red-700`, `red-900`, `amber-900` und `emerald-700` schreiben. Der Grund ist die
Umbelegung selbst: Eine Stufe bekommt im dunklen Modus einen einzigen neuen Wert,
und der passt entweder als Fläche oder als Schrift, nie als beides. Wer eine neue
Farbklasse einführt, prüft deshalb erst, ob ihre Stufe schon anders belegt ist, und
weicht im Zweifel auf eine freie Stufe aus.

`slate-800` ist die einzige Ausnahme und zeigt, was ein Verstoß kostet.
`FileDropZone.vue` nimmt `text-slate-800` für die Schrift der Dropzone,
`MarkdownPreview.vue` nimmt `dark:bg-slate-800` für den gewählten Reiter. Im
dunklen Modus ist `slate-800` die helle Schriftfarbe — der Reiter bekäme eine helle
Füllung unter heller Schrift. Deshalb steht am Ende von `style.css` eine Sonderregel,
die `[role="tab"][aria-selected="true"]` im dunklen Modus wieder dunkel füllt. Es soll bei
dieser einen Ausnahme bleiben.

## Das Board

Die Arbeit steht in `kanban/` und wird mit `kanban-md` bewegt. Das Programm liegt
unter `~/go/bin/kanban-md` und ist nicht im PATH.

Der Status sagt, wie weit ein Ticket ist: `backlog` → `todo` → `in-progress` →
`review` → `done`. Wer daran arbeitet, steht nicht in der Spalte, sondern im Feld
`assignee` — dem Fachgebiet. `benny` macht das Frontend, `sophie` das Backend,
`akar` Infrastruktur und Dokumentation, `katche` koordiniert und baut nichts.

Automatisch gezogen wird nur `todo`. `backlog` ist der Ideenspeicher; ein Ticket
dorthin zu schieben heißt „später vielleicht“, eines nach `todo` zu schieben heißt
„das wird gebaut“.

```bash
K=~/go/bin/kanban-md
$K list --assignee sophie --unblocked --not-blocked --status todo --sort priority -r
$K move <ID> in-progress --claim sophie-01
```

Beide Filter sind nötig und meinen Verschiedenes. `--unblocked` blendet Tickets aus,
deren Vorgänger aus `depends_on` noch offen sind; `--not-blocked` blendet solche
aus, die jemand ausdrücklich blockiert hat.

### Jedes Ticket bekommt einen eigenen Worktree

```bash
git worktree add .worktrees/task-NN -b task/NN-slug
```

Der Haupt-Checkout bleibt Board-Operationen und Merges vorbehalten. Ticketcode
entsteht dort nie — ein `PreToolUse`-Hook setzt das durch. Wer committet, nennt die
eigenen Dateien einzeln und niemals `git add -A`: Der gemeinsame Checkout hält fast
immer den Board- und Codezustand anderer Sitzungen.

### Das Abbild wird aus dem Worktree gebaut

`make up` und `make build` laufen aus dem Worktree, nicht aus dem Haupt-Checkout.
Der Grund ist nicht die Bequemlichkeit, sondern der feste Stand. Der Haupt-Checkout
gehört allen Sitzungen: Während dort ein Bau läuft, mergen fremde Tickets nach
`main` — in genau das Verzeichnis, aus dem Docker gerade liest. Nichts am Vorgang
meldet das. Kein Fehler, keine Warnung, kein sichtbarer Unterschied — **ein falscher
Bau sieht aus wie ein richtiger.** Am 1. September 2026 ist das passiert, und
aufgefallen ist es nur, weil jemand die Merges nebenher mitgelesen hat. Ein Worktree
steht auf einem eigenen Zweig, den fremde Merges nicht bewegen.

`docker/.env` liegt nicht im Git und wird in jedem Worktree einmal angelegt:

```bash
cd .worktrees/task-NN
cp docker/.env.example docker/.env
make up
```

Containername und Port stehen dort und sind in jedem Checkout dieselben. Zwei Läufe
gleichzeitig gehen deshalb nicht; wer baut, hält den Dienst des anderen an.

Ein Unterschied bleibt und ist gewollt. Die Docs-Stufe des Abbilds holt die
veröffentlichte Dokumentation mit `git archive gh-pages` aus dem Repo. Dafür braucht
sie das Objektlager, und das steht im Worktree nicht zur Verfügung: `.git` ist dort
kein Verzeichnis, sondern eine Datei mit einem Zeiger auf den Haupt-Checkout, und im
Container läuft dieser Zeiger ins Leere. Die Stufe erkennt das und baut die aktuelle
Fassung selbst — derselbe Weg wie in einem frischen Klon vor dem ersten Release. Ein
Abbild mit allen veröffentlichten Versionen entsteht nur aus dem Haupt-Checkout, und
das ist Sache des Release, nicht der Entwicklung.

### Der Ticketschnitt entscheidet über die Gleichzeitigkeit

Jeder Ticketrumpf hat denselben Aufbau: **Ziel**, **Eigene Dateien**, **Vorgaben**,
**Prüfung**. Der zweite Abschnitt nennt die Dateien, die das Ticket besitzt, und
keine zwei offenen Tickets besitzen dieselbe Datei. Ohne diese Regel kollidieren
genau die Tickets, die gleichzeitig laufen sollen.

Der letzte Abschnitt ist der wichtigste. Er beschreibt, woran man erkennt, dass die
Arbeit fertig ist, und lässt damit jemanden allein entscheiden, statt zurückzufragen.

Fehlt einem Ticket etwas aus einem anderen Fachgebiet, endet die Arbeit nicht im
Stillstand, sondern mit einer Übergabe:

```bash
~/go/bin/kanban-md handoff <ID> --claim sophie-01 \
    --block "Grund" --note "Was fehlt, naechster Schritt" -t --release
```

## Prosa

Deutsche Fließtexte — diese Dokumentation, Kommentare, Ticketrümpfe — folgen den
Regeln aus `~/.claude/rules/SPRACHE.md`. Code, Bezeichner, Variablennamen und
Commit-Messages bleiben englisch.
