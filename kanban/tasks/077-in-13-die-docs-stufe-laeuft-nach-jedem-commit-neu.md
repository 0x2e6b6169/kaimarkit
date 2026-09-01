---
id: 77
title: IN-13 · Die Docs-Stufe laeuft nach jedem Commit neu
status: done
priority: low
created: 2026-09-01T13:50:30.694332269+02:00
updated: 2026-09-01T17:25:48.597856331+02:00
started: 2026-09-01T17:05:50.415518255+02:00
completed: 2026-09-01T17:25:40.415746869+02:00
assignee: akar
tags:
    - infra
    - performance
class: standard
---

## Befund (01.09.2026, gemessen von akar beim Abschluss von IN-10)

Die Docs-Stufe kopiert mit `COPY . .` (Zeile 107) den gesamten Bau-Kontext samt
`.git`. Weil `.git` sich bei jedem Commit ändert, läuft die Stufe nach **jedem**
Commit neu — gemessen 20 bis 23 Sekunden.

Seit IN-10 (#55) den Bau von 485 s auf 86 s gebracht hat, sind das rund ein Viertel
der verbleibenden Zeit. Vorher ging es im Rauschen unter.

## Die Vorgeschichte, damit niemand denselben Weg zweimal geht

Bei der Suche nach der Cache-Ursache in #55 stand `COPY . .` als Verdächtiger im
Raum. Der PO hat sie ausgeschlossen — richtig: Sie gehört zur Docs-Stufe mit eigenem
`FROM` und kann die Installationsschicht der Builder-Stufe nicht verwerfen. Die
eigentliche Ursache lag in den `.dockerignore`-Mustern.

**Ihre eigene Schicht verwirft sie aber sehr wohl.** Der Verdächtige war unschuldig
für die große Tat und schuldig für eine kleinere.

## Warum `.git` nicht einfach hinausfliegt

`.dockerignore` nennt den Grund im Kopf: Die Docs-Stufe holt die veröffentlichte
Dokumentation mit `git archive gh-pages` aus dem Repo. Ohne `.git` fällt sie auf
`mkdocs build` zurück und liefert nur die aktuelle Fassung. Wer `.git` ausschließt,
löst dieses Ticket und bricht das, wofür IN-8 (#45) gebaut wurde.

## Eigene Dateien

- `docker/Dockerfile` (Stufe `docs`)
- `.dockerignore`, falls die Lösung dort ansetzt

## Vorgaben

Die Stufe kopiert, was sie braucht, statt alles. Sie braucht `.git` und die
mkdocs-Eingaben — nicht `backend/`, nicht `frontend/`, nicht `docker/`.

Ob das über gezielte `COPY`-Anweisungen geht oder über einen anderen Weg an die
veröffentlichte Fassung, entscheidet die Lane am Gegenstand.

## Prüfung

- Ein Commit, der weder `docs/` noch `mkdocs.yml` anfasst, lässt die Docs-Stufe
  `CACHED` melden.
- Gegenprobe: Eine Änderung an `docs/` lässt sie zu Recht neu laufen.
- Der Rückfall bleibt heil: Aus einem Checkout mit `gh-pages` landet die
  veröffentlichte Fassung weiterhin im Abbild, aus einem ohne greift `mkdocs build`.
- Die gemessene Bauzeit vorher und nachher steht in der Ticketnotiz.

[[2026-09-01]] Tue 14:10
## Mitzunehmen: zwei Messungen für #56 (Auflage des PO, 01.09.2026)

Dieses Ticket baut und startet den Dienst neu. Das **ist** der kontrollierte Neustart, den zwei offene Zahlen aus BE-17 (#56) brauchen — sie im selben Zug zu nehmen spart einen zweiten und, wichtiger, liefert beide aus demselben Lauf.

Vorschlag von akar, Bedingungen von ihm und hier eingelöst: Es steht im Rumpf und nicht nur in einer Nachricht, und der Subagent **misst und trägt ein, er entscheidet nichts.**

### Was zu messen ist

Am frischen Container, unmittelbar nacheinander:

1. **Zeit bis `healthy`** — vom Start bis zum ersten gelungenen Healthcheck. **Gleich beim Start abgreifen**, nicht nachträglich: `docker inspect` hält nur die letzten Einträge, und bei einem Container, der eine Stunde läuft, ist der erste herausgerollt. Die Auskunft ist einmal da und danach weg.
2. **Speicher im Ruhezustand** — `docker stats --no-stream`, bevor irgendetwas umgewandelt wird.
3. **Speicher während einer Umwandlung** — dieselbe Messung, während ein Dokument durch `docling` läuft, am **selben** Container, unmittelbar danach.

### Was ausdrücklich nicht zu tun ist

**Kein Vergleich mit und ohne Vorladen.** Dafür bräuchte es ein zweites Abbild ohne `_warmup`, und das ist den Aufwand nicht wert. Die Entscheidung in #56 hängt an absoluten Werten, nicht an einem Verhältnis: Die Zeit bis `healthy` muss deutlich unter `KAIMARKIT_HEALTH_START_PERIOD` (180 s) liegen, der Speicher deutlich unter `KAIMARKIT_MEM_LIMIT` (6 GB).

Fällt eines von beidem knapp aus, ist das ein Befund und geht als Notiz zurück — hier wird nichts umgebaut.

### Wohin die Zahlen gehören

Als Notiz an **#56**, mit dem Abbildstand. Die Folgerung daraus zieht sophies Lane, nicht dieses Ticket. Ein Satz in der Notiz dieses Tickets genügt als Verweis.

### Warum das keine Vermischung ist

Es ändert nichts am Gegenstand von #77 und besitzt keine zusätzliche Datei. Es nutzt nur einen Neustart, der ohnehin stattfindet. Ein eigenes Ticket dafür bräuchte denselben Neustart und könnte deshalb nie neben diesem laufen.

[[2026-09-01]] Tue 17:05
**Vom Nutzer freigegeben (01.09.2026): „Ja, das passt jetzt. Baue mit #77 neu."**

Der Bau ersetzt seinen laufenden Dienst — das ist ihm gesagt und von ihm abgenommen. Er wartet auf das neue Abbild; seit dem laufenden Stand `bbf7180` sind sechs Merges dazugekommen (FE-14, FE-15, BE-29, BE-30, BE-31, PROC-4).

**Zwei Erwartungen an diesen Lauf, die zugleich Prüfungen sind:**

1. **Der Cache aus #55 wird zum ersten Mal im Ernstfall geprüft.** Die sechs Merges fassen `backend/app/` und `frontend/src` an, aber **nicht** `backend/pyproject.toml`. `pip install` und der Modell-Download müssen also `CACHED` melden. Tun sie es nicht, ist das ein Befund und wiegt schwerer als dieses Ticket — dann greift die Korrektur aus #55 im Alltag nicht.
2. **Das VPN des Nutzers steht weiterhin.** Solange die ladenden Stufen `CACHED` sind, spielt das keine Rolle. Läuft eine davon doch neu, kriecht sie bei rund 0,5 MB/s — dann ist die Bauzeit kein Beleg für irgendetwas und gehört mit Vorbehalt notiert, nicht als Messwert.

Am Ende steht ein gesunder Dienst aus dem Haupt-Checkout auf dem aktuellen Stand. `docker/.env` bleibt unangetastet — dort steht die Zeitgrenze des Nutzers.

## Erledigt (akar-27, 01.09.2026) — Merge `6b4c3b4`, Zweig `task/77-docs-stage-cache`

### Was geaendert wurde

`docker/Dockerfile`, Stufe `docs`, einzige geaenderte Datei. `COPY . .` ist weg.
Die Eingaben kommen jetzt einzeln herein, geordnet danach, wie oft sie sich
aendern:

1. `backend/pyproject.toml` → `pip install` der Gruppe `docs`
2. `mkdocs.yml`, `docs/` → `mkdocs build --site-dir /docs-site`
3. `.git` → falls `gh-pages` da ist, ersetzt die veroeffentlichte Fassung die eben
   gebaute

`.dockerignore` blieb unangetastet: Der Kopfkommentar dort begruendet, warum
`.git` im Kontext bleibt, und das gilt unveraendert.

`.git` haengt als Bind-Mount ein statt kopiert zu werden — es wird nur gelesen und
legt so keine Schicht von zwoelf Megabyte an.

### Die Falle, und warum sie nicht umgangen wurde

`.git` auszuschliessen loest dieses Ticket und bricht IN-8 (#45). Getan wurde das
nicht. Beide Rueckfaelle sind belegt, siehe Pruefung unten.

### Abweichung von der Pruefung — die vierte Zeile stimmt nicht ganz

Der Rumpf verlangt: „Ein Commit, der weder `docs/` noch `mkdocs.yml` anfasst,
laesst die Docs-Stufe `CACHED` melden." **Vollstaendig `CACHED` ist nicht
erreichbar**, solange die Stufe `gh-pages` aus dem Repo holt — und das verlangt
#45.

Gemessen statt vermutet: Ein Bind-Mount geht mit dem Inhalt seiner Quelle genauso
in den Cache-Schluessel ein wie ein `COPY`. Belegt an einem Wegwerf-Dockerfile:
Quelle geaendert → die `RUN`-Zeile laeuft neu; Quelle unveraendert → `CACHED`.
`.git` aendert sich bei jedem Commit, also laeuft jede Schicht neu, die `.git`
liest, egal ob per `COPY` oder per Mount.

Erreichbar — und erreicht — ist das, worum es der Sache nach geht: **Von neun
Schichten der Stufe melden acht `CACHED`, die neunte laeuft 0,3 bis 0,4 s.** Die
teuren beiden, `pip install` und `mkdocs build`, sind darunter.

### Pruefung

Kontrollierter Versuch in einem Wegwerf-Klon. **Der musste sein:** Im Worktree ist
`.git` eine Datei und aendert sich nie — der Befund tritt dort gar nicht auf und
jede Messung waere schon vorher gruen gewesen. Gebaut mit
`docker build --target docs`.

| | Altstand `COPY . .` | Neustand |
|---|---|---|
| erster Lauf | 44,5 s | 39,7 s |
| **nach einem leeren Commit** | **39,4 s** — Stufe laeuft ganz neu (`DONE 32,8 s`) | **3,4 s** — acht Schichten `CACHED`, die neunte `DONE 0,4 s` |
| nach einer Aenderung an `docs/` | — | 4,1 s: `COPY docs/` und `mkdocs build` laufen zu Recht neu (`DONE 1,6 s`), `pip install` bleibt `CACHED` |

Rot vor Gruen ist damit belegt: Zeile zwei, Spalte eins ist der Fehlschlag vor der
Arbeit.

**Gegenprobe Rueckfall, beide Richtungen:**

- *Mit* `gh-pages` (im Klon einen Waisenzweig angelegt, wie mike ihn hinterlaesst —
  `0.3/index.html`, `index.html`, `versions.json`): Alt- und Neustand liefern
  **denselben** Inhalt in `/docs-site`, naemlich genau diese drei Eintraege. Keine
  Reste des mkdocs-Baus daneben.
- *Ohne* `gh-pages`: `/docs-site` enthaelt `index.html`, `404.html`, `sitemap.xml`,
  `assets/` und die acht Navigationszweige — `mkdocs build` hat gegriffen, keine
  `versions.json`.
- *Aus einem Worktree* (`.git` ist dort eine Datei): Bau laeuft durch, `rc=0`,
  Rueckfall auf `mkdocs build`. Der Bind-Mount einer Datei bricht die Pruefung
  `[ -d /src/.git ]` nicht.

**Im echten Bau aus dem Haupt-Checkout** auf `6b4c3b4`, also mit einem `.git` als
Verzeichnis und auf einem Commit, den kein vorheriger Bau gesehen hatte:
`[docs 1/9]` bis `[docs 8/9]` `CACHED`, `[docs 9/9] DONE 0,3 s`.

### Bauzeit vorher und nachher

Der Vergleich, um den es geht, ist der der Docs-Stufe nach einem Commit ohne
Doku-Aenderung: **39,4 s → 0,4 s.**

Die Gesamtzeiten daneben sind zwei verschiedene Faelle und kein Vorher-Nachher:

- Voller Bau vor der Aenderung, aus dem Haupt-Checkout auf `e66795f`, mit den sechs
  Merges seit `bbf7180` im Gepaeck: **199 s**, davon 42,8 s Docs-Stufe (21 %),
  29,7 s `COPY --from=builder`, 12,2 s `COPY --from=models`.
- Voller Bau nach der Aenderung, auf `6b4c3b4`: **4 s** — alles andere lag schon im
  Zwischenspeicher.

Die 42,8 s der Docs-Stufe liegen ueber den 20 bis 23 s aus dem Befund. Der Grund
steht jetzt als Kommentar im Dockerfile: `PIP_NO_CACHE_DIR=1` laedt
mkdocs-material bei jedem Lauf neu, und wie lange das dauert, haengt an der
Leitung. Der Kommentar nennt deshalb die Spanne 20 bis 43 s.

### Die beiden vorrangigen Erwartungen aus dem Nachtrag

1. **Der Cache aus IN-10 (#55) haelt im Ernstfall.** Im vollen Bau auf `e66795f`,
   nach sechs Merges an `backend/app/` und `frontend/src`: `[deps 5/5] pip install
   --extra-index-url .../cpu` meldet **CACHED**, `[models 2/2] docling-tools models
   download` meldet **CACHED**. Die Korrektur aus #55 greift im Alltag.
2. **Zum VPN:** Weil beide ladenden Stufen `CACHED` waren, hing keine Zahl an der
   Leitung. Eine Uebertragung gab es doch: `pip install` in der Docs-Stufe lief mit
   1,9 MB/s (mkdocs-material, 9,3 MB) — nicht die 0,5 MB/s des befuerchteten Falls.
   Die 42,8 s sind damit ein brauchbarer Messwert, aber einer mit einem
   Netzanteil; die 39,4 s / 0,4 s aus dem kontrollierten Versuch sind der harte
   Vergleich, weil beide Seiten dieselbe Leitung hatten.

### Messwerte fuer BE-17 (#56)

Der Neustart ist genutzt worden. Die drei Zahlen — 6,3 s bis `healthy`, 294 MiB im
Ruhezustand, rund 1 GiB waehrend einer Umwandlung mit docling — stehen mitsamt
Abbildstand und zwei Nebenbefunden als Notiz an **#56**. Keines der Ergebnisse
faellt knapp aus.

### Zustand am Ende

`kaimarkit:local` aus dem Haupt-Checkout auf `6b4c3b4`, Container laeuft und meldet
`healthy`. `/api/health` antwortet, `/docs/` liefert HTTP 200. `docker/.env` nicht
angefasst.
