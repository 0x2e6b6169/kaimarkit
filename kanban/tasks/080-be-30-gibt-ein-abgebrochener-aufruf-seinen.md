---
id: 80
title: BE-30 · Gibt ein abgebrochener Aufruf seinen Semaphor-Platz frei?
status: done
priority: high
created: 2026-09-01T16:01:34.880218284+02:00
updated: 2026-09-01T16:26:56.085130256+02:00
started: 2026-09-01T16:25:25.02386752+02:00
completed: 2026-09-01T16:25:25.02386752+02:00
assignee: sophie
tags:
    - backend
    - bug
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

[[2026-09-01]] Tue 16:25
## Messung (sophie-29)

Eigene uvicorn-Instanz auf freiem Port, echter `/api/convert`, Attrappe als Engine
mit bekannter Dauer, Client schliesst mit RST. Kein Container, kein laufender
Dienst beruehrt.

**Lauf 1** — `MAX_CONCURRENT=2`, Zeitgrenze 120 s, Umwandlung 10,0 s, Abbruch nach 2,0 s:

| t (s) | Ereignis |
|---|---|
| 0,0 | A: Engine startet, nimmt Platz 1 |
| 2,0 | A: Client bricht die Verbindung ab (RST) |
| 3,0 | B startet sofort — Platz 2 war frei; C wartet |
| 10,0 | A: Engine endet von selbst, **erst jetzt wird der Platz frei** |
| 10,0 | C: Engine startet, exakt in derselben Sekunde |

B fertig nach 10,05 s, C nach 17,03 s statt 10 s. Der Platz blieb nach dem Abbruch
weitere **8,0 s** belegt, also die volle Restdauer. Nach dem abgebrochenen Aufruf kam
nur ein zweiter durch; der dritte wartete 7,0 s.

**Lauf 2** — dasselbe, aber `CONVERSION_TIMEOUT=5` und Umwandlung 20 s, Abbruch nach
2,0 s: A nimmt den Platz bei 0,0, Abbruch bei 2,0, Platz frei bei **5,0** — an der
Zeitgrenze. Der Handler endete mit `ConversionTimeout`, nicht mit `CancelledError`.

## Antwort

**Nein.** Ein abgebrochener Aufruf gibt seinen Semaphor-Platz nicht frei. Die Ursache
liegt nicht in `run_conversion`: uvicorn bricht die ASGI-Aufgabe beim
Verbindungsabbruch gar nicht erst ab. `async with _semaphore()` wird deshalb nie
vorzeitig verlassen, und `abandon_on_cancel=True` kommt nie zum Zuge. Der Platz kehrt
nur zurueck, wenn die Umwandlung von selbst endet oder in die Zeitgrenze laeuft.

## Folgen fuer die zwei offenen Entscheidungen

- Die Zeitgrenze ist **kein Notnagel**, sondern das einzige Mittel, das einen Platz
  zuverlaessig zurueckholt. Sie bleibt an der Groessenordnung echter Dokumente.
- Der Abbruch im Frontend (#79) ist bis auf Weiteres eine **reine Anzeigesache**: Er
  beendet die Wartezeit des Nutzers, nicht die Arbeit im Dienst. Bei zwei Plaetzen
  blockiert ein zaehes Dokument weiter den halben Dienst, bis zu
  `KAIMARKIT_CONVERSION_TIMEOUT` lang.

## Abhilfe wurde nicht gebaut

So beauftragt. Sie waere ein eigenes Ticket: die Verbindung ueberwachen
(`http.disconnect` lesen und die Aufgabe selbst abbrechen), damit der Semaphor-Platz
frueher zurueckkommt. Der Thread laeuft dann trotzdem weiter und belegt einen Platz im
Threadpool — das bleibt die bekannte Einschraenkung.

## Test

`tests/test_uploads.py::test_an_aborted_call_keeps_its_semaphore_slot` haelt den
gemessenen **Ist**-Zustand fest, nicht den gewuenschten. Der Kommentarblock darueber
sagt das ausdruecklich und nennt die Zahlen. Faellt der Test eines Tages, ist das die
gute Nachricht. Dazu zwei Saetze in der Docstring von `run_conversion`.

## Pruefung

Sammelzahl **137/143 vorher, 138/144 nachher** (6 deselected, `slow`).
`pytest -q -rs`: 138 passed. `ruff check .`: sauber. Test dreimal wiederholt, stabil,
2,7-2,9 s Laufzeit.

[[2026-09-01]] Tue 16:26
## Entscheidung des PO aus dieser Messung (01.09.2026)

**Kein Folgeticket, das den Platz beim Abbruch freigibt.** Die naheliegende Abhilfe — `http.disconnect` überwachen und die Aufgabe selbst abbrechen — wird nicht gebaut, und zwar nicht wegen des Aufwands.

Der Semaphor begrenzt die **tatsächliche Last**, nicht die Zahl der offenen HTTP-Aufrufe. Der Thread läuft nach einem Abbruch weiter; ihn kann niemand beenden. Den Platz trotzdem freizugeben hieße, eine dritte Umwandlung auf einer Maschine zu starten, die bereits zwei rechnet — bei zwei physischen Kernen (gemessen in #59) das Gegenteil dessen, wofür die Grenze da ist. Die Abhilfe sähe aus wie eine Verbesserung und wäre eine Verschlechterung.

Eine echte Lösung müsste die Umwandlung selbst abbrechbar machen — eigener Prozess statt Thread. Das ist ein anderes Vorhaben und lohnt sich heute nicht.

**Zwei Folgen, die daraus feststehen:**

1. **Die Zeitgrenze bleibt an der Größenordnung echter Dokumente.** Sie ist kein Notnagel, sondern das einzige Mittel, das einen Platz je zurückholt. Der Gedanke, sie großzügig zu setzen, weil der Nutzer abbrechen kann, ist damit erledigt — er kann es nicht, jedenfalls nicht für den Dienst. Die 600 s aus #59 bleiben, wie sie sind.
2. **Der Abbruch in #79 ist reine Anzeige** und wird auch so beschriftet: „Nicht mehr warten", nicht „Umwandlung stoppen". benny ist unterrichtet.

Bemerkenswert an der Messung: Die Ursache lag nicht dort, wo der Ticketrumpf sie vermutet hat. Nicht `anyio.to_thread` und nicht `run_conversion` — **uvicorn bricht die ASGI-Aufgabe beim Verbindungsabbruch überhaupt nicht ab**, `abandon_on_cancel=True` kommt nie zum Zuge. Hätte der Subagent die Vermutung des Rumpfes bestätigt statt gemessen, stünde jetzt eine plausible und falsche Ursache im Board.
