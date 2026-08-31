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
| `frontend/src/` | Vue 3 mit TypeScript und Tailwind. Komponenten, Composables, der API-Client und der Mock für die Entwicklung. |
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
make dev            # Backend auf :8000 und Frontend auf :5173, beide mit Reload
make test           # pytest ohne die Docling-Modelle
make test-slow      # pytest mit Docling, dauert
make lint           # ruff über das Backend
make docs-serve     # Vorschau dieser Seiten auf :8001
```

Im Frontend kommen `npm run typecheck` und `npm run test` dazu. Der Dev-Server
schickt `/api` per Proxy an `localhost:8000`.

Wer am Frontend arbeitet und kein Backend starten will, nimmt den Mock:

```bash
cd frontend && VITE_KAIMARKIT_MOCK=1 npm run dev
```

Der Mock hängt sich als Middleware in den Dev-Server und beantwortet `/api` selbst.
In dieser Betriebsart richtet Vite den Proxy gar nicht erst ein — sonst liefe jede
Anfrage, die der Mock nicht kennt, still in ein Backend, das niemand gestartet hat.

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
und lädt im Hintergrund.

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
