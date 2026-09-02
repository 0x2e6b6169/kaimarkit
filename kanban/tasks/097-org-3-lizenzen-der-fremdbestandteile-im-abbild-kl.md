---
id: 97
title: ORG-3 · Lizenzen der Fremdbestandteile im Abbild klären
status: backlog
priority: medium
created: 2026-09-02T16:36:23.290248393+02:00
updated: 2026-09-02T16:36:23.290248393+02:00
assignee: akar
class: standard
---

## Ziel

Klären, welche Lizenzpflichten die mitgelieferten Fremdbestandteile auslösen, und
das Ergebnis aufschreiben. Erst danach entscheidet der PO, ob eine NOTICE-Datei
entsteht.

**Dies ist ein Rechercheticket.** Es liefert eine Empfehlung mit Belegen, keinen
Umbau. Wer beim Recherchieren merkt, dass etwas zu tun ist, meldet es, statt es
zu tun.

## Herkunft

Gemeldet von akar aus ORG-1 (#95). ORG-1 hat das Projekt selbst unter MIT
gestellt und die Frage der Fremdbestandteile ausdrücklich nicht angefasst.

## Die Frage hinter der Frage

**Wird das Abbild überhaupt weitergegeben?** Davon hängt alles ab. Wer ein Abbild
nur auf der eigenen Maschine baut, gibt nichts weiter; die Pflichten aus den
Lizenzen der Fremdbestandteile treffen erst den, der es an andere ausliefert.
Heute baut jeder Nutzer selbst aus dem Quelltext, und es gibt keine Registry.
Das ist zu belegen, nicht zu vermuten — auch für die Zukunft: Ein späterer Push
nach ghcr.io ändert die Lage schlagartig.

## Was zu prüfen ist

**Pandoc ist der schärfste Punkt.** Es kommt als `.deb` aus dem offiziellen
Release ins Abbild (`docker/Dockerfile`, `PANDOC_VERSION`) und steht unter GPL.
Eine GPL-Binärdatei weiterzugeben verlangt mehr als eine Namensnennung — dazu
gehört ein Angebot des Quelltexts. Zu klären: welche GPL-Fassung genau, und was
sie bei einem Abbild verlangt, in dem Pandoc als eigenständiges Programm neben
dem Dienst liegt und nur als Unterprozess aufgerufen wird.

**Die vorgebackenen Modelle.** `/opt/docling-models` entsteht in einer eigenen
Bau-Stufe. Modelle haben eigene Lizenzen, und nicht jede erlaubt jede Nutzung —
manche schließen den gewerblichen Einsatz aus. Zu nennen ist für jedes Modell:
Herkunft, Lizenz, und ob sie den Betrieb dieses Dienstes deckt.

**Die Python-Abhängigkeiten.** docling, markitdown, Torch und was sie
mitziehen. Hier geht es um Namensnennung, nicht um Quelltextpflichten; eine
erzeugte Liste genügt, keine Einzelprüfung von Hand.

## Eigene Dateien

Keine. Das Ergebnis steht in der Ticketnotiz. Was daraus folgt, schneidet der PO
danach.

## Prüfung

1. Für jeden der drei Blöcke steht eine Aussage mit Beleg in der Notiz —
   Lizenzname und Fundstelle, nicht „vermutlich MIT".
2. Die Frage „wird weitergegeben?" ist mit Ja oder Nein beantwortet, mit
   Begründung aus dem Repository (Makefile, Compose-Dateien, CI).
3. Die Notiz endet mit einer Empfehlung in einem Satz: NOTICE nötig, nicht nötig,
   oder nötig erst ab dem Tag, an dem das Abbild veröffentlicht wird.
