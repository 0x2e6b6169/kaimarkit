---
id: 59
title: IN-11 · 120 Sekunden Zeitgrenze sind fuer Docling zu knapp
status: in-progress
priority: high
created: 2026-09-01T10:40:33.636401513+02:00
updated: 2026-09-01T12:07:51.017454037+02:00
assignee: akar
tags:
    - infra
    - config
depends_on:
    - 45
claimed_by: akar-23
claimed_at: 2026-09-01T12:07:51.017454037+02:00
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

[[2026-09-01]] Tue 11:19
Zwei Messungen zur Ursache, damit das Ticket nicht nur die Grenze hochsetzt (01.09.2026, im laufenden Container):

- **Torch benutzt zwei Threads**, nicht vier: `torch.get_num_threads()` -> `2`, `torch.cuda.is_available()` -> `False`. Der Rechner hat vier logische Kerne (`nproc`), waehrend der Umwandlung stand die CPU bei 238 Prozent. Torch waehlt die Zahl nach physischen Kernen; ob hier vier logische auf zwei physische kommen, ist nicht geprueft. Ein Versuch mit `torch.set_num_threads(4)` oder `OMP_NUM_THREADS=4` kostet nichts und liefert eine Zahl.
- **Der Container hat keine CPU-Grenze.** `docker/docker-compose.yml` setzt nur `mem_limit`, kein `cpus`. Die zwei Threads kommen also von Torch, nicht von Docker.

Damit hat dieses Ticket zwei Wege, und der zweite ist der bessere: die Grenze hochsetzen behandelt das Symptom, mehr Threads die Sache. Beide messen, dann entscheiden.

Nicht die Ursache sind die Anreicherungsmodelle: `_build_pipeline` schaltet weder Code- noch Formel- noch Bildklassifikation ein. `CodeFormulaV2` und `DocumentFigureClassifier` liegen im Abbild, laufen aber nicht — das ist Ballast in der Groesse, nicht in der Zeit.

[[2026-09-01]] Tue 11:22
Die fehlende Zahl ist da (01.09.2026, nach dem Quick-Fix des Nutzers auf 600 s): **`TeleTrusT-T.I.S.P._T.P.S.S.E._CM_2026_Anmeldung.pdf` brauchte 326 062 ms — 5 Minuten 26 Sekunden.** Mit `docling`, OCR aus.

Die Voreinstellung von 120 Sekunden liegt damit bei **37 Prozent** dessen, was dieses Dokument braucht. Es war nicht knapp daneben, sondern um das Zweieinhalbfache zu klein.

Damit steht die Entscheidungsgrundlage: Eine Voreinstellung, die alltaegliche Dokumente durchlaesst, liegt oberhalb von fuenf Minuten — oder die Sache wird an der Ursache angefasst (Threads, Enginewahl), statt die Grenze immer weiter hochzusetzen. Beide Wege stehen im Ticket; diese Zahl sagt, dass der zweite der wichtigere ist.

[[2026-09-01]] Tue 12:06
Abhaengigkeit auf #56 wieder entfernt (PO, 01.09.2026). Sie war verkehrt herum gesetzt.

Die Ueberlegung beim Anlegen war: Klaert sich in BE-17, ob `ready` wirklich `ready` heisst, aendert sich womoeglich diese Zahl. Richtig ist das Gegenteil. Die Vorgabe dieses Tickets lautet, dasselbe Dokument **zweimal hintereinander** zu messen; die zweite Zeit ist die Arbeitszeit, die Differenz das Laden. Genau diese Differenz ist die Zahl, die #56 braucht. Dieses Ticket liefert den Messwert, es wartet nicht darauf.

Ausserdem haette die Sperre eine `high`-Sache mit sichtbarer Wirkung fuer den Nutzer hinter einer `medium`-Untersuchung in einer anderen Lane angehalten — und akars Lane damit ganz.

Bleibt die Abhaengigkeit auf #45, und die ist erfuellt.
