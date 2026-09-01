---
id: 80
title: BE-30 · Gibt ein abgebrochener Aufruf seinen Semaphor-Platz frei?
status: in-progress
priority: high
created: 2026-09-01T16:01:34.880218284+02:00
updated: 2026-09-01T16:18:04.110228222+02:00
assignee: sophie
tags:
    - backend
    - bug
claimed_by: sophie-29
claimed_at: 2026-09-01T16:18:04.110228222+02:00
class: standard
---

## Die Frage (01.09.2026, aus der Frage des Nutzers nach der Zeitgrenze)

`KAIMARKIT_MAX_CONCURRENT=2` — zwei gleichzeitige Umwandlungen, mehr nicht.
`uploads.py:115` nimmt den Platz über `async with _semaphore():`.

**Bricht der Client die Verbindung ab, gibt der Platz dann frei?** Die Umwandlung
läuft über `anyio.to_thread`, und ein Thread lässt sich nicht abbrechen. Denkbar ist
also, dass der Aufruf für den Nutzer beendet ist, während der Platz weiter belegt
bleibt, bis die Umwandlung von selbst endet oder in die Zeitgrenze läuft.

Bei zwei Plätzen entscheidet das darüber, ob ein einziges zähes Dokument den halben
Dienst blockiert.

## Warum das jetzt zählt

Der Nutzer hat gefragt, ob die Zeitgrenze noch nötig ist, wo er die verstrichene Zeit
sieht. Die Antwort hängt an dieser Messung:

- **Gibt der Abbruch den Platz frei**, ist die Zeitgrenze nur noch ein Notnagel
  gegen ein Dokument, das nie endet — und darf großzügig stehen, weil der Nutzer
  seinen eigenen Ausweg hat.
- **Gibt er ihn nicht frei**, ist die Zeitgrenze das einzige, was den Platz je
  zurückholt. Dann bleibt sie an der Größenordnung echter Dokumente und der Abbruch
  im Frontend (#79) ist eine reine Anzeigesache.

## Eigene Dateien

- `backend/app/uploads.py`
- `backend/tests/test_uploads.py` oder die Datei, die den Semaphor prüft

## Vorgaben

Zuerst **messen, nicht ändern**: Einen Aufruf starten, die Verbindung clientseitig
schließen, und feststellen, ob ein zweiter und dritter Aufruf durchkommen. Das
Ergebnis gehört wörtlich in die Ticketnotiz — es entscheidet über #79 und über die
Zeitgrenze.

Erst wenn feststeht, dass der Platz hängen bleibt, ist zu entscheiden, was zu tun
ist. Das ist dann womöglich ein eigenes Ticket, kein Nachtrag.

## Prüfung

- Die Messung steht in der Notiz: Wie viele Aufrufe kommen nach einem abgebrochenen
  durch, und wie lange bleibt der Platz belegt.
- Ein Test hält das gemessene Verhalten fest — auch wenn es das unerwünschte ist.
- `pytest -q -rs` bleibt grün, Sammelzahl in der Notiz.
