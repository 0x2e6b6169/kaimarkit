# kaimarkit

Wandelt Dokumente (PDF, ePub, docx und weitere) nach Markdown, damit man den Kontext
sieht und prüfen kann, den man einem LLM gibt. FastAPI-Backend mit drei
austauschbaren Engines, Vue-Frontend, ein Docker-Image, das beides ausliefert.

Alles, was dieses Projekt braucht, liegt im Repo. Verbindlich sind
`contracts/api.md` für die Schnittstelle, diese Datei für Befehle und
Konventionen, das Board unter `kanban/` für die Arbeit und `docs/` für Betrieb und
Bedienung. `ENTWURF.md` hält den ursprünglichen Entwurf fest — die Herkunft, nicht
die Vorschrift: Wo er und der Quelltext auseinandergehen, gilt der Quelltext.

---

## Befehle

**Python niemals global.** Immer zuerst die pyenv-Umgebung aktivieren:

```bash
pyenv activate claude-code
```

```bash
# Backend
cd backend && uvicorn app.main:app --reload    # laeuft auch ohne Frontend und Docs
pytest -q                                       # ohne Docling-Modelle
pytest -q -m slow                               # mit Docling, dauert
ruff check .

# Frontend
cd frontend && npm run dev                      # Proxy auf localhost:8000, Backend noetig
npm run test                                    # vitest
npm run build
npm run typecheck

# Dokumentation
make docs-serve                                 # Vorschau auf :8001
make docs-release VERSION=0.3                   # mike deploy, erst beim Release

# Betrieb
make help                                       # alle Ziele
make up | make up-traefik | make up-authelia
```

`kanban-md` liegt unter `~/go/bin/kanban-md` und ist nicht im PATH.

---

## Verbindliche Konventionen

Sechs Regeln, die zwischen den Strängen gelten. Jede einzelne ist leicht zu
verletzen, und jede Verletzung fällt erst viel später auf.

**1. Der Schnittstellen-Dreiklang.** `contracts/api.md`, `backend/app/models.py` und
`frontend/src/types.ts` beschreiben dieselbe Schnittstelle. Wer eine der drei Dateien
ändert, ändert alle drei im selben Commit. Sonst laufen Backend und Frontend
auseinander, ohne dass es jemand merkt.

**2. Engines bleiben gekapselt.** Außerhalb von `backend/app/converters/` importiert
nichts `markitdown` oder `docling` und ruft nichts `pandoc` auf.

**3. Fehler werden übersetzt.** Jede Engine wandelt ihre eigenen Ausnahmen in
`ConversionError` aus `errors.py`. Bibliotheksspezifische Fehler dringen nicht bis in
die API.

**4. Konfiguration kommt aus der Umgebung.** Ausschließlich `KAIMARKIT_*`-Variablen
über `config.py`. Keine Konstante wird im Code festgeschrieben, die im Betrieb
umgestellt werden soll.

**5. Der Dienst speichert nichts.** Jede hochgeladene Datei bekommt ein eigenes
`TemporaryDirectory`, das im `finally` mitsamt Inhalt verschwindet — auch im
Fehlerfall.

**6. Eine Quelle für den Betrieb.** `docker/.env.example` und
`docs/betrieb/konfiguration.md` beschreiben dieselben Variablen und werden gemeinsam
geändert. Die Dokumentation ist die einzige Quelle für Betrieb und Bedienung; es gibt
kein zweites README daneben.

---

## Arbeitsweise mit mehreren Agenten

Vier langlebige Sitzungen teilen sich die Arbeit nach Fachgebiet. Jede fährt ihre
eigene **Lane** und verteilt Tickets an kurzlebige Subagenten, damit ihr eigener
Kontext schlank bleibt. Die Sitzung wird beim Start benannt (`claude -n <name>`);
`~/.claude/bin/session-name` löst den Namen zur Laufzeit auf. Der Skill
`/work-lane` fährt die eigene Lane leer, `/loop /work-lane` hält sie am Laufen.

### Rollen und Lanes

- **`benny`** — Frontend. Vue-Komponenten, Dropzone und Warteschlange, Vorschau,
  Optionen, Download, Gestaltung und Barrierefreiheit.
- **`sophie`** — Backend. FastAPI, Converter-Engines, Registry, Uploads und
  Grenzen, ZIP-Bau, Tests.
- **`akar`** — Infrastruktur, Dokumentation, Organisatorisches und alles Übrige.
  Dockerfile, Compose-Schichten, Makefile, MkDocs, Planung.
- **`katche`** — nur Koordination, als **Product Owner und Scrum Master**: pflegt
  und priorisiert das Board, verteilt Lanes, hält Standup, koordiniert Merges,
  räumt Hindernisse weg und legt Produktentscheidungen dem Nutzer vor. katche baut
  nichts und hat keine eigene Lane. Als PO-Pflicht läuft ein leichtes
  **Board-Sync**: von Zeit zu Zeit *nur* das Board committen
  (`git add kanban/ && git commit -m "chore(board): sync"`), damit das Fenster
  nicht committeter gemeinsamer Board-Zustände klein bleibt. Dazu gehört,
  **Befunde aufzufangen**: Was ein Subagent meldet, statt es selbst zu ändern,
  wird ein Ticket. Sonst hängt der Befund daran, dass zufällig ein Ticket auf
  dieser Datei offen steht.

**Lane ist das Feld `assignee`, keine Spalte.** Die Status bleiben der Lebenszyklus
(backlog → todo → in-progress → review → done). Jede Sitzung arbeitet nur ihre
eigene Lane, höchste Priorität zuerst:

```bash
K=~/go/bin/kanban-md
$K list --assignee <self> --unblocked --not-blocked --status todo --sort priority -r
$K move <ID> in-progress --claim <self>-NN
```

**Beide Filter sind nötig und meinen Verschiedenes.** `--unblocked` blendet
Tickets aus, deren `depends_on`-Vorgänger noch offen sind; `--not-blocked` blendet
solche mit einem ausdrücklichen `--block` aus. Dieses Board ist über `depends_on`
verdrahtet — `--not-blocked` allein listet die ganze Lane als startbereit.

**Nur `todo` wird automatisch gezogen.** `backlog` ist der Ideenspeicher des PO.
Ein Ticket nach `todo` zu schieben ist katches ausdrückliches „das wird gebaut".

### Subagenten — einer je Ticket

Eine Sitzung verteilt ihre Lane an benannte Subagenten `<self>-NN` (`benny-01`,
`benny-02`, …). Ein Subagent nimmt sein **einziges** Ticket durch die
Standardschleife (claimen als `<self>-NN` → Worktree → umsetzen → die **Prüfung**
aus dem Ticketrumpf bestehen → Doku im selben Merge → `--no-ff` merge → Worktree
entfernen → Ticket auf `done` und Claim freigeben) und endet dann.

Mehrere Subagenten dürfen gleichzeitig laufen, **zwei bis drei**. Die Eltern-Sitzung
haftet dafür, dass das sinnvoll bleibt: nur so viele wie es kollisionsfreie
startbereite Tickets gibt, **niemals zwei Subagenten an derselben Datei**, Merges
nach `main` nacheinander, Worktrees nach Abschluss aufräumen.

Dass das aufgeht, hängt am Ticketschnitt: **Jeder Ticketrumpf nennt die Dateien,
die er besitzt, und keine zwei offenen Tickets besitzen dieselbe Datei.** Finden
sich zwei startbereite Tickets, die sich eine Datei teilen, ist das ein Schnittfehler
— melden statt parallel laufen lassen.

### Alle Ticketarbeit läuft in einem Worktree

```bash
git worktree add .worktrees/task-NN -b task/NN-slug
```

Der Haupt-Checkout (**Board-Home**) ist gemeinsam und bleibt Board-Operationen
(`kanban-md`), Merges und den Board-/Prozess-Commits von PO/SM vorbehalten —
**niemals Ticketcode von hier aus ändern oder committen**. Das gilt auch für
Subagenten: Die **erste** Handlung eines Subagenten ist, seinen Worktree anzulegen
und hineinzuwechseln. Ein `PreToolUse`-Hook
(`.claude/hooks/guard-worktree.sh`) setzt das durch; er blockiert Edit und Write
auf Board-Home-Pfade außerhalb von `.worktrees/` und lässt nur `kanban/**`,
`CLAUDE.md`, `CHANGELOG.md`, `.gitattributes` und `.claude/**` durch.

**Eigene Artefakte gezielt stagen — niemals `git add -A` oder `git add .`.** Der
gemeinsame Checkout hält fast immer den `kanban/`- und Code-Zustand anderer
Sitzungen. Nur die Dateien stagen, die das eigene Ticket anfasst.
`kanban/activity.jsonl` wird per `.gitattributes` union-gemerged, damit parallele
Anhänge nie kollidieren.

### Kontexthygiene

Der Kontext je Ticket verschwindet von selbst, weil jeder Subagent in seinem
eigenen Fenster läuft — ein `/clear` je Ticket ist deshalb unnötig. Damit das so
bleibt:

1. **Die Eltern-Sitzung bleibt dünn.** Sie verteilt und liest das Board. Sie liest
   keine Dateien und führt keine Tests oder Builds selbst aus.
2. **Ein Subagent gibt nur ein kurzes Ergebnis zurück** (Ticket, done/blocked,
   Branch, eine Zeile Notiz). Das Ausführliche gehört in die Board-Notiz, nicht in
   die Antwort.
3. **Jeder Subagent bekommt einen selbsttragenden Auftrag** — er sieht die
   Vorgeschichte der Eltern-Sitzung nicht.
4. **Das Board ist die einzige Quelle der Wahrheit.** Eine Eltern-Sitzung darf
   zwischen zwei Wellen `/clear`en und sich aus `kanban-md list` neu orientieren —
   nie mitten in der Verteilung.

---

## Der Ticketschnitt

**Jedes Ticket nennt in seinem Rumpf die Dateien, die es besitzt, und keine zwei
offenen Tickets besitzen dieselbe Datei.** Das ist die Regel, auf der das parallele
Arbeiten ruht — ohne sie kollidieren genau die Tickets, die gleichzeitig laufen
sollen.

**In `docs/` gilt das Eigentum je Abschnitt, nicht je Seite.** Eine Doku-Seite ist
nach Lesern gegliedert, nicht nach Erbauern; jede Lane braucht ein Stück davon. Ein
Ticket nennt deshalb den Abschnitt mit: `docs/formate.md` (Abschnitt „Docling").
Wer eine Seite anlegt, besitzt ihren Aufbau; wer den Gegenstand baut, besitzt die
Aussagen über ihn. Zwei offene Tickets im selben Abschnitt bleiben ein Schnittfehler.
Ein Abschnitt, den jedes Ticket anfassen müsste, folgt der Engpassdatei, zu der er
gehört: `docs/formate.md` (Abschnitt „Die Matrix") gehört `BE-2`, so wie `registry.py`.

**Wer ein Verhalten ändert, berichtigt im selben Merge, was dadurch falsch wird** —
auch auf einer Seite, die ein anderes Ticket angelegt hat. Was schon vorher falsch
war, wird gemeldet statt geändert. Eine Seite, die nach dem Merge etwas Unwahres
über das Verhalten sagt, ist schlimmer als eine Regelverletzung.

Drei Stellen sind gegen den naheliegenden Schnitt gebaut, damit das aufgeht:

- `main.py` gehört allein `BE-1`. Die Router-Module existieren zunächst als Stümpfe,
  die `BE-7` und `BE-8` füllen.
- `registry.py` gehört allein `BE-2`. Es nennt alle drei Enginenamen und lädt die
  Module verzögert; `BE-3` bis `BE-5` liefern nur ihr eigenes Modul und tragen sich
  nirgends ein.
- `pyproject.toml` gehört allein `BE-1`, einschließlich der Abhängigkeitsgruppe
  `docs` — sonst kollidierte `DOC-1` damit.

Jeder Ticketrumpf hat denselben Aufbau: **Ziel**, **Eigene Dateien**, **Vorgaben**,
**Prüfung**. Der letzte Abschnitt ist der wichtigste: Er ist es, der einen Subagenten
allein entscheiden lässt, ob er fertig ist, statt zurückzufragen.

**Weicht die Prüfung ab, ist zuerst die Prüfung verdächtig, nicht die Arbeit.** Wer
eine Vorgabe nicht erfüllen kann, meldet die Abweichung und übergibt das Ticket,
statt die Zahl passend zu machen. Gemeint ist die Annahme hinter der Prüfung; ein
Fehler im eigenen Code bleibt ein Fehler im eigenen Code und wird behoben.

Eine verfehlte Prüfung und ein fehlendes Stück aus einer anderen Lane enden beide
nicht im Stillstand, sondern mit einer Übergabe:

```bash
~/go/bin/kanban-md handoff <ID> --claim <self>-NN \
    --block "Grund" --note "Was fehlt, naechster Schritt" -t --release
```

Eine Ausnahme, die quer zu den Lanes liegt: der **Schnittstellen-Dreiklang**
(Konvention 1). Ändert ein Ticket ihn, fasst es alle drei Dateien im selben Commit
an und vermerkt das in der Ticketnotiz, damit die andere Lane es sieht.

---

## Prosa

Deutsche Fließtexte — Dokumentation, Kommentare, Ticket-Rümpfe — folgen
`~/.claude/rules/SPRACHE.md`. Code, Bezeichner, Variablennamen und Commit-Messages
bleiben englisch.

**Ein Wortlaut, den ein Ticket vorschlägt, steht darin in richtiger Schreibung.** Ein
Subagent übernimmt einen vorgeschlagenen Meldungstext wörtlich — schreibt der Rumpf
ihn in ASCII-Umschrift, landet die Umschrift im Quelltext und damit vor dem Nutzer.
Genau so ist die Warnung aus BE-19 entstanden, Minuten nachdem BE-21 dieselbe
Umschrift an anderer Stelle beseitigt hatte. Das Board verträgt Umlaute; die
Gewohnheit, ohne sie zu schreiben, war nie nötig.

<!-- BEGIN kanban-md context -->
## Board: kaimarkit

**28 tasks** | 27 active | 0 blocked | 0 overdue

### In Progress

- **#22** IN-2 · Compose-Basis und .env.example mit Quellenverweis ueber Variablen (high, @akar)
- **#13** FE-1 · Vite, Vue 3, TypeScript, Tailwind und ein Mock-Server fuer /api (high, @benny)
- **#23** IN-1 · docker/Dockerfile: fuenf Stufen, Torch aus dem CPU-Index, Modelle vorgebacken (high, @akar)
- **#4** BE-1 · FastAPI-Geruest, config.py, /api/health, Einhaengen von SPA und /docs (high, @sophie)
- **#20** DOC-1 · MkDocs, Material-Theme und mike: mkdocs.yml, Navigation, Seitengeruest (high, @akar)
- **#5** BE-2 · Converter-Protokoll, Faehigkeitsmatrix, Auswahl und Fallback (high, @sophie)
- **#10** BE-7 · Endpunkte /api/convert und /api/capabilities (high, @sophie)
- **#14** FE-2 · API-Client und die Composables useConversion und useCapabilities (high, @benny)
- **#11** BE-8 · Endpunkt /api/convert/batch und ZIP-Bau (medium, @sophie)
- **#25** IN-4 · Authelia-Ergaenzung: ForwardAuth-Middleware und API-Router (medium, @akar)
- **#16** FE-4 · Vorschau mit markdown-it und DOMPurify, Rohtext, Kopieren (medium, @benny)
- **#18** FE-6 · Download einzeln und als ZIP ueber jszip (medium, @benny)
- **#9** BE-6 · Upload-Strom mit Groessenlimit, Tempfiles, Semaphor, Zeitgrenze (medium, @sophie)
- **#30** INT-2 · Ende-zu-Ende-Pruefung im Container (medium, @akar)
- **#15** FE-3 · Dropzone und Warteschlange mit Status je Datei (medium, @benny)
- **#19** FE-7 · Gestaltung, Dark Mode, Tastaturbedienung, aria-live (medium, @benny)
- **#8** BE-5 · Pandoc-Adapter mit --sandbox und Zeitgrenze (medium, @sophie)
- **#21** DOC-2 · Inhalte: Schnellstart, Formate, API, Entwicklung, Grenzen (medium, @akar)
- **#7** BE-4 · Docling-Adapter mit vorgeladenem Konverter und OCR-Schalter (medium, @sophie)
- **#6** BE-3 · MarkItDown-Adapter (medium, @sophie)
- **#24** IN-3 · Traefik-Ergaenzung: Labels in Map-Form, externes Netz, ports reset (medium, @akar)
- **#12** BE-9 · Testfixtures und Engine-Smoketests (medium, @sophie)
- **#26** IN-5 · Makefile mit allen Zielen einschliesslich docs-serve und docs-release (medium, @akar)
- **#27** DOC-3 · Inhalte Betrieb: Konfiguration, lokal, Traefik, Authelia (medium, @akar)
- **#17** FE-5 · Optionen: Enginewahl und OCR-Schalter aus /api/capabilities (medium, @benny)
- **#29** INT-1 · Frontend gegen das echte Backend, Mock entfernen (medium, @benny)
- **#28** DOC-4 · Wurzel-README.md (low, @akar)

### Recently Completed

- **#3** SETUP-1 · Verzeichnisgeruest und Schnittstellenvertrag festschreiben (critical, @akar) — completed 2026-08-31
<!-- END kanban-md context -->
