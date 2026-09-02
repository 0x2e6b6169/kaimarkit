---
id: 99
title: IN-19 · git describe als KAIMARKIT_VERSION in das Abbild
status: done
priority: high
created: 2026-09-02T16:38:27.503502943+02:00
updated: 2026-09-02T17:00:23.000512605+02:00
started: 2026-09-02T17:00:22.621214584+02:00
completed: 2026-09-02T17:00:22.621214584+02:00
assignee: akar
depends_on:
    - 98
class: standard
---

## Ziel

Der Bau schreibt den Stand des Arbeitsbaums in das Abbild. `git describe` läuft
einmal beim Bauen auf der Maschine, die das `.git` hat; der Container bekommt
das Ergebnis als Umgebungsvariable und muss nie selbst nach Git fragen.

## Eigene Dateien

- `Makefile`
- `docker/Dockerfile`
- `docker/docker-compose.yml`
- `docker/.env.example`
- `docs/betrieb/konfiguration.md`

Nicht `docker-compose.traefik.yml` und nicht `docker-compose.authelia.yml`: Die
Bau-Angaben stehen in der Basis, die Schichten erben sie.

## Vorgaben

**Die Form ist die von `git describe`,** vom Nutzer am 2026-09-02 entschieden:

    git describe --tags --always --dirty

Auf dem Tag `v0.1.0`, zwölf Commits dahinter `v0.1.0-12-ga22a6c5`, mit
Änderungen im Arbeitsbaum zusätzlich `-dirty`.

**Der Weg ist Makefile → Bau-Argument → `ENV` im Abbild.** In
`docker-compose.yml` steht unter `build.args` schon `PANDOC_VERSION`; daneben
kommt `KAIMARKIT_VERSION`. Das Makefile berechnet den Wert und übergibt ihn an
jedes Ziel, das baut — `build`, `up`, `up-traefik`, `up-authelia`. Kein Aufruf
von `git` im Dockerfile: Die Docs-Stufe hängt `.git` nur als Bind-Mount ein, die
Laufzeit-Stufe sieht es nie, und das soll so bleiben.

**Drei Fälle, in denen `git describe` nichts liefert,** und alle drei kommen
vor: ein Bau aus einem Tarball ohne `.git`, ein Klon ohne Tags
(`--depth 1` ohne `--tags`), und `git` gar nicht installiert. In jedem Fall darf
der Bau **nicht** abbrechen. Der Wert bleibt dann leer, und das Backend fällt
auf `__version__` zurück — das regelt BE-33 (#98). Im Makefile also so
schreiben, dass ein Fehlschlag von `git` die leere Zeichenkette ergibt, nicht
einen Abbruch.

**`KAIMARKIT_VERSION` ist überschreibbar, aber keine gewöhnliche Einstellung.**
Wer aus einem Tarball baut, will den Wert von Hand setzen können. In
`docker/.env.example` gehört die Variable deshalb hinein — auskommentiert, mit
zwei Sätzen: dass sie im Normalfall aus `git describe` kommt und nur für einen
Bau ohne Git-Verlauf von Hand zu setzen ist.

**Konvention 6 gilt.** `docker/.env.example` und
`docs/betrieb/konfiguration.md` beschreiben dieselben Variablen und ändern sich
im selben Commit. In der Dokumentation gehört die Rückfallkette hin: Umgebung,
sonst `__version__` aus dem Quelltext.

## Prüfung

1. Vor der Arbeit: `docker compose --env-file … config` nennt unter `build.args`
   kein `KAIMARKIT_VERSION`. Belegen.
2. Danach nennt dieselbe Ausgabe es, und der Wert ist genau das, was
   `git describe --tags --always --dirty` im Arbeitsbaum ausgibt.
3. `make build` läuft durch, und
   `docker run --rm --entrypoint sh <abbild> -c 'echo $KAIMARKIT_VERSION'`
   gibt denselben Wert aus.
4. Der Rückfall ist belegt, nicht behauptet: In einem Verzeichnis ohne `.git`
   denselben Bau-Aufruf machen. Er läuft durch und setzt die Variable leer.
   Ein Wegwerf-Klon genügt, `git archive HEAD | tar -x` in ein leeres
   Verzeichnis ist schneller.
5. `make help` nennt kein neues Ziel — es kommt keines dazu.


---

## Ergebnis (akar-32, Zweig task/99-build-version, gemerged)

Das Makefile ermittelt `git describe --tags --always --dirty` einmal beim Parsen und
exportiert den Wert nur, wenn er nicht leer ist — sonst überschriebe die leere
Zeichenkette einen Eintrag, den jemand für einen Bau ohne Git-Verlauf von Hand in
`docker/.env` gesetzt hat. In `docker-compose.yml` steht das Argument als
`KAIMARKIT_VERSION: ${KAIMARKIT_VERSION-}`; die Bindestrich-Form gibt den leeren
Vorgabewert und erspart Compose die Warnung bei jedem Aufruf. Im Dockerfile stehen
`ARG` und `ENV` bewusst ganz unten in der Laufzeitstufe, nach allen COPY-Zeilen: Der
Wert ändert sich bei jedem Commit, und weiter oben hätte er die Pandoc-Installation
und die COPY-Schichten aus dem Zwischenspeicher geworfen.

### Die fünf Prüfpunkte

1. **Rot belegt.** Vor der Arbeit nannte `docker compose -f docker/docker-compose.yml
   config` unter `build.args` allein `PANDOC_VERSION: 3.6.4`.
2. **Grün.** Danach steht dort `KAIMARKIT_VERSION: v0.1.0-21-geab120d-dirty` — genau
   das, was `git describe --tags --always --dirty` im Arbeitsbaum ausgab.
3. **`make build` durchgelaufen** (7 min 9 s, Abbild `kaimarkit:in19`, damit das
   laufende `kaimarkit:local` des Nutzers unberührt blieb). `docker run --rm
   --entrypoint sh kaimarkit:in19 -c 'printf "%s" "$KAIMARKIT_VERSION"'` gab denselben
   Wert aus.
4. **Der Rückfall ist belegt, aber auf anderem Weg als im Rumpf vorgeschlagen** —
   siehe den Befund unten. Belegt wurde er über den dritten der drei Fälle, eine
   Maschine ohne `git`: Mit einem PATH-Shim, der `git` mit 127 beendet, lief
   `make build` durch, das Abbild trug ein leeres `KAIMARKIT_VERSION`, und
   `get_settings().service_version` meldete darin `0.1.0` aus `__version__` — gegen
   `v0.1.0-21-geab120d-dirty` im Abbild mit Git. Für den ersten Fall, den Baum ohne
   `.git`, ist wenigstens die Makefile-Seite belegt: Dort ergibt `compose config`
   `KAIMARKIT_VERSION: ""`, ohne Abbruch und ohne Warnung.
5. **`make help`** nennt dieselben vierzehn Ziele wie vorher.

Zusätzlich: `mkdocs build --strict` läuft ohne Warnung, der Verweis auf `../api.md`
in der neuen Passage stimmt.

### Befund, nicht von diesem Ticket verursacht

**Ein Bau aus einem Baum ohne `.git` scheitert heute, unabhängig von IN-19.** Die
Docs-Stufe im Dockerfile hängt `.git` als Bind-Mount ein
(`RUN --mount=type=bind,source=.git,target=/src/.git`). Fehlt das Verzeichnis im
Kontext, bricht BuildKit schon beim Berechnen des Cache-Schlüssels ab:

    failed to solve: failed to compute cache key: failed to calculate checksum
    of ref …: "/.git": not found

Die Wache `[ -d /src/.git ] || exit 0` in derselben Zeile kommt dafür zu spät: Sie
fängt den Worktree-Fall ab, in dem `.git` eine Datei ist, nicht den fehlenden. Mit
`git archive HEAD | tar -x` geprüft, und zwar zweimal — mit dem Stand nach IN-19 und
mit dem Stand davor (`eab120d`). Beide Male dieselbe Meldung. Der Weg über
`KAIMARKIT_VERSION` bleibt davon unberührt, und die Dokumentation beschreibt den
Tarball-Fall weiterhin richtig, sobald der Bau ihn wieder zulässt. Gehört in ein
eigenes Ticket für `docker/Dockerfile` (Stufe „Dokumentation").
