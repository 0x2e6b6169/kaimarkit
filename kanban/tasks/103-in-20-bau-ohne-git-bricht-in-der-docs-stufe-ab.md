---
id: 103
title: IN-20 · Bau ohne .git bricht in der Docs-Stufe ab
status: done
priority: medium
created: 2026-09-02T17:01:31.820069248+02:00
updated: 2026-09-02T17:10:24.572828618+02:00
started: 2026-09-02T17:10:18.936544486+02:00
completed: 2026-09-02T17:10:18.936544486+02:00
assignee: akar
class: standard
---

## Ziel

Ein Bau aus einem Baum ohne `.git` soll durchlaufen. Heute bricht er ab, bevor
irgendein Skript etwas prüfen kann.

## Der Befund

Gemeldet von akar aus IN-19 (#99), und **älter als IN-19**: akar-32 hat den
Stand vor und nach dem Merge geprüft, der Abbruch steht in beiden.

Die Docs-Stufe des `docker/Dockerfile` hängt `.git` als Bind-Mount ein
(`--mount=type=bind,source=.git,target=/src/.git`). BuildKit löst den Mount
schon beim Bilden des Cache-Schlüssels auf und bricht mit `"/.git": not found`
ab. Die Wache `[ -d /src/.git ] || exit 0` im Skript steht innerhalb des `RUN`
und kommt damit zu spät — sie läuft nie.

Betroffen sind zwei der drei Fälle, die IN-19 als Rückfall verlangt hatte: der
Bau aus einem Tarball und der aus einem flachen Klon ohne `.git`. Der dritte
Fall — `git` nicht installiert, `.git` vorhanden — ist belegt und läuft.

**Der Versionsstempel aus IN-19 ist davon nicht betroffen** und richtig gebaut.
Es fehlt der Weg dorthin: Wer aus einem Tarball baut, kommt gar nicht so weit.

## Eigene Dateien

- `docker/Dockerfile` (Docs-Stufe)

Falls die Lösung eine Angabe in `docker/docker-compose.yml` oder im `Makefile`
braucht, ist das ein Befund und gehört gemeldet — der Entwurf geht davon aus,
dass die Docs-Stufe allein genügt.

## Vorgaben

**Die Docs-Stufe braucht `.git` nur für eines:** die veröffentlichte
Dokumentation aus `gh-pages` zu holen. Ohne `.git` gibt es nichts zu holen, und
das ist kein Fehler, sondern der Normalfall für jeden, der aus einem Tarball
baut. Das Abbild bekommt dann nur die Dokumentation des aktuellen Standes.

**`.git` bleibt draußen.** Was IN-13 erreicht hat, bleibt: kein `COPY` von
`.git`, keine Schicht mit dem Verlauf darin. Die Lösung ist nicht, den Mount
durch eine Kopie zu ersetzen.

**Kein neues Bau-Argument, das jemand von Hand setzen muss.** Der Bau erkennt
selbst, ob `.git` da ist. Ein Schalter, den man kennen muss, verschiebt das
Problem auf den, der ihn nicht kennt.

## Prüfung

1. Vor der Arbeit: In einem Verzeichnis ohne `.git` schlägt der Bau fehl, und
   zwar mit `"/.git": not found`. Die Meldung wörtlich in die Notiz. So entsteht
   das Verzeichnis:
   `git archive HEAD | (mkdir -p /tmp/kmk-tar && tar -x -C /tmp/kmk-tar)`
2. Nach der Arbeit läuft derselbe Bau in demselben Verzeichnis durch.
3. Der gebaute Container liefert unter `/docs/` eine Seite. Dass die
   Versionsweiche fehlt, ist erwartet und gehört in die Notiz — nicht als
   Fehler, sondern als beschriebenes Verhalten.
4. Der gewöhnliche Bau aus dem Klon bleibt, wie er war: `make build` läuft
   durch, und `/docs/` zeigt weiterhin, was es vorher zeigte.
5. Die Bauzeit des gewöhnlichen Falls verschlechtert sich nicht wesentlich.
   Vorher und nachher messen, beide Zahlen nennen — und **nicht** gleichzeitig
   mit einem anderen Bau auf derselben Maschine.


---

## Ergebnis (akar-33, Zweig task/103-build-without-git, gemergt als 27cdf38)

**Die Ursache liegt vor dem RUN, nicht darin.** BuildKit löst die Quelle eines
Bind-Mounts schon auf, wenn es den Cache-Schlüssel bildet. Eine Wache im Skript
kommt deshalb nie an die Reihe. Die Lösung hängt den Mount eine Ebene höher ein:
`--mount=type=bind,source=.,target=/ctx`. Die Wurzel des Bau-Kontextes gibt es
immer; ob `.git` darin liegt, entscheidet erst das Skript
(`[ -d /ctx/.git ] || exit 0`). Die Git-Aufrufe laufen jetzt mit `git -C /ctx`,
`safe.directory` zeigt auf `/ctx`.

Kein `COPY` von `.git`, kein neues Bau-Argument. `docker/docker-compose.yml` und
`Makefile` blieben unberührt — die Docs-Stufe genügte, wie der Entwurf annahm.

### Die fünf Prüfpunkte

1. **Rot vor der Arbeit.** Bau aus `/tmp/kmk-tar` (aus `git archive HEAD`), Ziel
   `docs`, Rückgabewert 1. Wörtlich:
   `ERROR: failed to build: failed to solve: failed to compute cache key: failed to calculate checksum of ref 7dfb7b0d-c3ee-4223-a443-852309fb38e8::qi5r4vjisqkl14skp0m10rkte: "/.git": not found`
2. **Grün danach.** Dasselbe Verzeichnis, neu aus dem berichtigten Stand
   entpackt, voller Bau: Rückgabewert 0. Die Docs-Stufe lief in 0,3 Sekunden
   durch und stieg an der Wache aus.
3. **Der Container liefert `/docs/`.** Aus dem Tarball-Abbild gestartet auf
   127.0.0.1:18080: `GET /docs/` gibt 200 und 20 572 Byte, Titel „kaimarkit".
   `/api/health` meldet `{"status":"ok","version":"0.1.0"}` — der Rückfall auf
   `__version__`, weil ohne `.git` kein `git describe` läuft. Die Versionsweiche
   von mike fehlt in der Seite, weil es ohne `gh-pages` keine zweite Fassung
   gibt. Beides ist das beschriebene Verhalten, kein Fehler.
4. **Der gewöhnliche Bau bleibt, wie er war.** In einem frischen Klon mit echtem
   `.git`: `make build` läuft durch. Die Dokumentation im Abbild ist Byte für
   Byte dieselbe wie vorher — 57 Dateien, gleiche Dateiliste, gleiche Prüfsumme
   der `index.html` (c1e21c5ae53c23aab11680f21c13ec5b) für den Bau mit dem alten
   und dem neuen Dockerfile.
5. **Die Bauzeit.** Gemessen wurde der Alltagsfall: warmer Zwischenspeicher, ein
   Commit auf `README.md`, dann bauen — derselbe Klon, dieselbe Reihenfolge,
   einmal mit dem alten und einmal mit dem neuen Dockerfile.
   **vorher 1,831 s, nachher 1,914 s.** Die Docs-Stufe kostete in beiden Fällen
   0,2 Sekunden. Vor jeder der beiden Messungen war die Maschine frei: nur der
   Container des Nutzers lief (healthy), kein `buildkit`- oder `buildx`-Prozess,
   Last 0,46 beziehungsweise 0,58.

### Was der Mount am Zwischenspeicher ändert

Ein Bind-Mount geht mit seinem Inhalt in den Cache-Schlüssel ein. Bisher verwarf
jeder Commit die letzte Schicht der Docs-Stufe, jetzt tut es jede Änderung am
Kontext. Beides kostet Sekundenbruchteile: `pip install` und `mkdocs build`
stehen oberhalb des Mounts und bleiben erhalten. Der Kommentar im Dockerfile
sagt das so.

### Keine Änderung an der Dokumentation nötig

`docs/betrieb/konfiguration.md` sagt über die drei Rückfälle „Keiner davon
bricht den Bau ab" — das stimmte vorher nicht und stimmt jetzt.
`docs/entwicklung.md` beschreibt den Worktree-Fall (`.git` als Datei); die Wache
fängt ihn weiterhin ab, der Satz bleibt richtig.
