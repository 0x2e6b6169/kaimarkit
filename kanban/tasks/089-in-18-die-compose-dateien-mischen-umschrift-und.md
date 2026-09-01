---
id: 89
title: IN-18 · Die Compose-Dateien mischen Umschrift und Umlaute
status: backlog
priority: low
created: 2026-09-01T18:28:03.783151797+02:00
updated: 2026-09-01T21:31:57.845608821+02:00
assignee: akar
tags:
    - infra
    - docs
class: standard
---

## Befund (01.09.2026, gemeldet von akar beim Abschluss von IN-17)

Die vier Dateien unter `docker/` stehen vollständig in ASCII-Umschrift. IN-17 hat dort neue Sätze mit Umlauten ergänzt — die Dateien sind seither **gemischt**, und das ist schlechter als beides einheitlich.

Betroffen: `docker/docker-compose.yml`, `docker/docker-compose.traefik.yml`, `docker/docker-compose.authelia.yml`, `docker/.env.example`.

## Abgrenzung zu BE-21/22/23

Dort ging es um Zeichenketten, die der **Nutzer** liest — Fehlermeldungen, Feldbeschreibungen. Hier geht es um **Kommentare** in Konfigurationsdateien. Der Leser ist ein Betreiber, kein Anwender.

Nach `CLAUDE.md` gilt trotzdem dasselbe: Deutsche Fließtexte folgen `SPRACHE.md`, und ein erklärender Kommentar ist Fließtext. Diese Dateien sind bewusst erklärend geschrieben; ihre Kommentare sind ihr halber Zweck.

## Warum es nicht drängt

Keine Wirkung auf Verhalten, keine auf den Nutzer. Es ist eine Frage der Einheitlichkeit — mit dem Zusatz, dass gemischte Schreibung schlechter ist als konsequente Umschrift.

## Eigene Dateien

- `docker/docker-compose.yml`
- `docker/docker-compose.traefik.yml`
- `docker/docker-compose.authelia.yml`
- `docker/.env.example`

Alle vier zusammen — getrennt geschnitten bliebe die Mischung bestehen.

## Vorgaben

Nur Kommentare und Hinweistexte. **Keine Variablennamen, keine Werte, keine Zeichenkette, die Compose liest.** Ein Umlaut in einem Wert wäre eine Verhaltensänderung.

Von Hand prüfen statt ersetzen zu lassen — dieselbe Auflage wie bei BE-21.

## Prüfung

- `docker compose -f … config` liefert vor und nach der Änderung **byteweise dieselbe Ausgabe**, in allen drei Kombinationen. Das ist der Beleg, dass nur Kommentare betroffen sind.
- `git diff` zeigt ausschließlich Kommentarzeilen.
- Keine der vier Dateien enthält noch gemischte Schreibung.

[[2026-09-01]] Tue 21:31
**Berichtigung der Vorgabe (PO, 01.09.2026).** Im Rumpf stand „von Hand prüfen statt ersetzen zu lassen". Das ist missverständlich formuliert und klingt nach Misstrauen gegen Werkzeuge oder gegen UTF-8. Beides ist nicht gemeint.

**Die Kodierung ist kein Thema.** Die Dateien sind UTF-8, `docs/` benutzt seit dem ersten Tag Umlaute, Compose liest sie ohne Weiteres.

**Der Grund ist die Ersetzung selbst: `ae`, `oe`, `ue`, `ss` sind Buchstabenpaare, keine Umschriftmarken.** Sie stehen in diesen vier Dateien in Wörtern, die unverändert bleiben müssen — und zwar nicht nur in Kommentaren:

    TRAEFIK_NETWORK, TRAEFIK_ENTRYPOINT, TRAEFIK_CERTRESOLVER
    traefik.http.routers…, traefik.docker.network, traefik.enable
    docker-compose.traefik.yml

Ein blindes `ae` -> `ä` macht daraus `TRÄFIK` und `träfik.http.routers` — Variablennamen und Label-Schlüssel, keine Prosa. Das bricht den Aufbau, und zwar still: Compose meldet nichts, Traefik sieht den Container einfach nicht mehr.

Bei `ss` gibt es überhaupt keine mechanische Regel. In denselben Dateien stehen nebeneinander:

    Groesse   -> Größe        (ersetzen)
    Schluessel -> Schlüssel   (ue, nicht ss)
    besser, dass, anpassen, Adresse, address, Gemessen, Unterprozess  (bleiben)

Ob `ss` zu `ß` wird, entscheidet das Wort, nicht das Muster.

**Die Vorgabe lautet deshalb genauer:** Jeder Treffer wird einzeln entschieden. Ob das im Editor mit Bestätigung je Fund geschieht, mit einer Wortliste oder mit einem Skript, ist gleichgültig — ein ungeprüfter Durchlauf über die Datei ist es, was nicht geht.

Die Prüfung fängt es ohnehin ab: `docker compose … config` muss vor und nach der Änderung **byteweise dieselbe Ausgabe** liefern. Ein verunstaltetes `TRAEFIK_NETWORK` fällt dort sofort auf.
