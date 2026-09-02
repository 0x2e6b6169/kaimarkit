---
id: 99
title: IN-19 · git describe als KAIMARKIT_VERSION in das Abbild
status: in-progress
priority: high
created: 2026-09-02T16:38:27.503502943+02:00
updated: 2026-09-02T16:45:48.853932863+02:00
assignee: akar
depends_on:
    - 98
claimed_by: akar-32
claimed_at: 2026-09-02T16:45:48.853932863+02:00
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
