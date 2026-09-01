---
id: 59
title: IN-11 · 120 Sekunden Zeitgrenze sind fuer Docling zu knapp
status: backlog
priority: high
created: 2026-09-01T10:40:33.636401513+02:00
updated: 2026-09-01T11:07:41.776548575+02:00
assignee: akar
tags:
    - infra
    - config
depends_on:
    - 56
class: standard
---

## Befund (01.09.2026, erste echte Datei des Nutzers)

Eine einseitige Rechnung, `engine=auto` (also `docling`), auf dem Entwicklungsrechner:

    Finished converting document DB_Rechnung_647052188315.pdf in 103.51 sec.
    POST /api/convert HTTP/1.1 200 OK

Durchgelaufen — bei **86 Prozent** der Voreinstellung `KAIMARKIT_CONVERSION_TIMEOUT=120`
(`docker/.env.example:48`). Waehrenddessen: CPU 238 Prozent, RAM 1,77 von 6 GB, also
kein Speicherdruck. Die Zeit geht in Rechenarbeit, nicht ins Warten.

Ein alltaegliches Dokument — eine Rechnung, eine Seite — landet damit knapp unter der
Grenze. Das naechste ist darueber, und der Nutzer bekommt einen Abbruch fuer etwas,
das kein Sonderfall ist.

## Was die Zahl noch nicht trennt

Es war der **erste Docling-Aufruf nach dem Start**. Aus IN-9 ist belegt, dass der
extra kostet: dort 32 Sekunden fuer ein Bild, das spaeter schneller ging. Wie viel
der 103 Sekunden auf das Laden entfaellt und wie viel auf das Dokument, ist offen.

Deshalb haengt dieses Ticket mit BE-17 (#56) zusammen: Klaert sich dort, ob `ready`
wirklich `ready` heisst, aendert sich womoeglich auch diese Zahl. Die Entscheidung
ueber die Voreinstellung faellt erst nach der zweiten Messung.

## Eigene Dateien

- `docker/.env.example`
- `docs/betrieb/konfiguration.md`

Konvention 6 gilt: beide im selben Commit.

## Vorgaben

Dasselbe Dokument zweimal hintereinander umwandeln und beide Zeiten messen. Die
zweite ist die Arbeitszeit, die Differenz das Laden.

Danach die Voreinstellung so setzen, dass ein alltaegliches Dokument nicht an ihr
scheitert — mit der Messung als Begruendung, nicht mit einer runden Zahl. Und
`docs/betrieb/konfiguration.md` sagt, woran man merkt, dass die Grenze zu knapp ist:
Der Abbruch sieht fuer den Nutzer aus wie ein Fehler des Dienstes.

## Pruefung

- Beide Messungen stehen in der Ticketnotiz, aus dem Log abgeschrieben.
- Die neue Voreinstellung laesst dieselbe Rechnung mit Abstand durchlaufen.
- Gegenprobe: Eine Datei, die die Grenze wirklich reissen soll, bricht weiterhin
  sauber mit einer Fehlermeldung ab und haengt nicht.

## Zurueckgestellt

Vom Nutzer zurueckgestellt, bis die Abnahme abgeschlossen ist (01.09.2026).

[[2026-09-01]] Tue 11:07
Eingetreten, am selben Tag: **`TeleTrusT-T.I.S.P._T.P.S.S.E._CM_2026_Anmeldung.pdf` ist an der Grenze gescheitert.**

    Die Umwandlung hat die Zeitgrenze von 120 s ueberschritten

Damit steht das Ticket nicht mehr auf einer Vorhersage, sondern auf einem Vorfall. Von drei Dokumenten, die der Nutzer bei der Abnahme durchgeschickt hat, lag eines bei 86 Prozent der Grenze und eines darueber. Das ist keine Randlage, das ist der Alltag.

Der Dienst selbst hat sich richtig verhalten: Er bricht sauber ab, die Meldung nennt die Grenze und den Grund, und die Oberflaeche zeigt sie an der Datei an. Der Fehler liegt allein im Wert.

Was die Messung noch nicht hergibt: **Wie lange das Dokument gebraucht haette, ist unbekannt** — der Abbruch hat es abgeschnitten. Ohne diese Zahl laesst sich keine begruendete Voreinstellung waehlen, nur eine geratene. Wer das Ticket umsetzt, faehrt es zuerst mit einer weit gesetzten Grenze durch und misst.

Vom PO auf `high` gehoben.
