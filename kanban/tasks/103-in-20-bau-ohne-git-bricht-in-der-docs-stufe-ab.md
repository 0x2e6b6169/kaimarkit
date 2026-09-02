---
id: 103
title: IN-20 · Bau ohne .git bricht in der Docs-Stufe ab
status: todo
priority: medium
created: 2026-09-02T17:01:31.820069248+02:00
updated: 2026-09-02T17:01:31.820069248+02:00
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
