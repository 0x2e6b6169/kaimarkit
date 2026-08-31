---
id: 44
title: IN-7 · Docker nach der Datenplatten-Reorganisation belegen
status: archived
priority: high
created: 2026-08-31T14:42:10.57703712+02:00
updated: 2026-08-31T16:30:53.293807682+02:00
started: 2026-08-31T16:30:53.296441911+02:00
completed: 2026-08-31T16:30:53.296441911+02:00
assignee: akar
tags:
    - infra
class: standard
---

## Ziel

Docker laeuft auf diesem Rechner als Docker Desktop. Seine Datenplatte liegt auf
`C:`, und `C:` ist zu 97 Prozent voll. Jeder Imagebau arbeitet gegen diese Grenze.

## Befund (gemessen 2026-08-31, 14:38 Uhr)

```
/dev/sdd   1007G   103G   854G   11%   /          <- hier war nie eng
C:\         470G   454G    17G   97%   /mnt/c     <- hier liegt Docker
D:\         1.3T   347G   941G   27%   /mnt/d     <- hier waere Platz
```

- Datenplatte: `C:\Users\jendrian\AppData\Local\Docker\wsl\disk\docker_data.vhdx`,
  **82,5 GB**.
- `docker system df` meldet zugleich nur **8,6 GB** tatsaechlichen Inhalt
  (5,9 GB Abbilder, 2,7 GB Build-Cache, 590 MB Volumes).
- Rund **74 GB sind toter Raum** aus frueher geloeschten Layern. Eine VHDX
  waechst, schrumpft aber nie von selbst.
- Ein `/var/lib/docker` gibt es in dieser Distribution nicht — deshalb sagt
  `df -h /` nichts ueber Dockers Platz. `apt clean` und `apt autoremove` haben
  `/dev/sdd` aufgeraeumt, wo 854 GB frei waren, und an `C:` nichts geaendert.
- `docker system prune` holt hier fast nichts, weil innen kaum etwas zu loeschen
  ist. Das Mittel ist Umzug oder Kompaktierung, nicht Aufraeumen.

## Eigene Dateien

Keine. Die Arbeit liegt auf der Windows-Seite und beim Nutzer; dieses Ticket
haelt den Befund fest, nennt die Wege und prueft das Ergebnis.

## Vorgaben

Zwei Wege, in dieser Reihenfolge zu erwaegen. **Vorher pruefen, dass kein Build
und kein Agent laeuft.**

1. **Umzug nach `D:`** (941 GB frei) — Docker Desktop, Settings → Resources →
   Advanced → *Disk image location*. Dauerhaft geloest; Docker haelt waehrend des
   Umzugs an. Der empfohlene Weg.
2. **Kompaktierung an Ort und Stelle** — PowerShell als Administrator, Docker
   Desktop beendet: `wsl --shutdown`, dann
   `Optimize-VHD -Path "<pfad>\docker_data.vhdx" -Mode Full`. Holt die toten
   ~74 GB zurueck, verschiebt aber nichts; `C:` bleibt der Engpass.

Weg 1 macht Weg 2 ueberfluessig. Wer beides tut, kompaktiert zuerst und zieht
dann die kleinere Datei um.

## Pruefung

- `df -h /mnt/c` meldet deutlich mehr als 17 GB frei.
- `docker info` laeuft, `docker images` zeigt die Abbilder von vorher — nach
  einem Umzug also `kaimarkit:local`, `authelia`, `traefik`, die beiden
  `postgres`, `wikijs`, `planka`.
- Die sieben Container aus dem Bestand starten wieder (`docker ps`).
- Ein `make up` im Projekt baut und startet durch.

## Herkunft

Aufgefallen waehrend INT-2 (#30), als der Nutzer `apt clean` gegen einen
vermuteten Platzmangel laufen liess und `/` daraufhin 854 GB frei meldete. Der
Widerspruch fuehrte auf die richtige Platte.

[[2026-08-31]] Mon 14:43
Zuschnitt geschaerft (31.08.2026): **Der Nutzer fuehrt die Reorganisation selbst und parallel durch** — Umzug oder Kompaktierung auf der Windows-Seite, danach ein WSL-Neustart. Fuer die Agenten ist das transparent: Nach dem Neustart liegen dieselben Pfade und dieselbe Docker-Schnittstelle vor, nur mit Platz. Dieses Ticket ist deshalb **kein Auftrag zum Umziehen**, sondern der Beleg danach: Ein Subagent fuehrt allein den Abschnitt Pruefung aus und meldet das Ergebnis. Faellt dabei etwas aus dem Bestand (ein Abbild, ein Volume, ein Container), gehoert das als eigenes Ticket ins Board, nicht in eine stille Reparatur. Die Wege unter Vorgaben bleiben als Beschreibung dessen stehen, was geschehen ist — nicht als Arbeitsanweisung.
