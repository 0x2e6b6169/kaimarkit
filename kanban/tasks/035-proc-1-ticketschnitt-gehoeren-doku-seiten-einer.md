---
id: 35
title: 'PROC-1 · Ticketschnitt: gehoeren Doku-Seiten einer Lane?'
status: backlog
priority: low
created: 2026-08-31T11:46:15.810335482+02:00
updated: 2026-08-31T14:05:11.336719456+02:00
assignee: akar
tags:
    - process
class: standard
---

## Ziel

BE-9 (Commit `cdd5509`, sophies Lane) hat die Abschnitte "Tests" und
"Beispieldateien" an `docs/entwicklung.md` angehaengt — eine Datei, die der
Ticketschnitt DOC-2 (#21) zuweist. Beim Merge gab es einen Konflikt; akar hat
ihn verlustfrei aufgeloest, beide Haelften stehen in der Datei.

Kein Schaden also, aber genau die Kollision, die das Dateieigentum ausschliessen
soll. Zweimal hat es gehalten, weil jemand von Hand aufgeraeumt hat.

Gemeldet von akar.

## Die offene Frage

Der Ticketschnitt in CLAUDE.md sagt: "Jedes Ticket nennt in seinem Rumpf die
Dateien, die es besitzt." Er sagt nicht ausdruecklich, dass Doku-Seiten ebenso
besessene Dateien sind wie Code. Ein Backend-Ticket, das seine Tests
beschreibt, greift deshalb naheliegend zu `docs/entwicklung.md`, ohne die Regel
verletzen zu wollen.

Zwei Wege stehen offen:

1. **Die Regel schaerfen.** In CLAUDE.md festhalten, dass `docs/`-Seiten Dateien
   mit Eigentuemer sind. Wer aus einer fremden Lane etwas beizutragen hat,
   uebergibt es per Ticketnotiz an den Eigentuemer, statt selbst zu schreiben.
   Kostet einen Umweg, macht die Konflikte aber unmoeglich.
2. **Die Ausnahme benennen.** Anhaengen an eine fremde Doku-Seite bleibt erlaubt,
   solange es ein eigener Abschnitt am Ende ist. Das ist der Zustand von heute —
   er hat funktioniert, aber nur, weil `.gitattributes` und ein wacher Mensch
   den Merge gerettet haben.

Ein dritter Weg waere, `docs/` wie `kanban/activity.jsonl` per `.gitattributes`
union-zu-mergen. Das loest den Konflikt technisch und erzeugt dafuer stumme
Dopplungen — deshalb hier nur der Vollstaendigkeit halber.

## Eigene Dateien

- `CLAUDE.md` (Abschnitt "Der Ticketschnitt")

Die Aenderung an CLAUDE.md liegt beim Nutzer, nicht bei einer Lane. Dieses
Ticket haelt den Fall fest, bis er entschieden ist.

## Pruefung

Der Nutzer hat sich fuer einen der Wege entschieden, und CLAUDE.md sagt
danach ausdruecklich, wie ein Ticket mit einer Doku-Seite umgeht, die einer
anderen Lane gehoert.

Erfasst via /findings (Test-Pass 2026-08-31)

## Zweiter Fall, gemeldet von sophie

Derselbe Schnittfehler ist schon einmal aufgetreten, und zwar andersherum.
`docs/formate.md` gehoert DOC-2 (#21), wurde aber von BE-2 bis BE-9 laufend
ergaenzt — jede Engine trug ihre Formate nach. BE-3 musste dort einen
Merge-Konflikt mit BE-4 von Hand aufloesen.

Das ist nicht der Fall aus dem Abschnitt oben. Dort haben zwei Tickets dieselbe
Codedatei angefasst, weil die Regel eine Luecke hat. Hier hat der Schnitt eine
Datei einem Eigentuemer zugewiesen, die jedes andere Ticket zwangslaeufig
anfassen muss: Wer eine Engine baut, weiss als Einziger, welche Formate sie
kann. Die Doku-Lane kann es erst hinterher abschreiben.

## Was der zweite Fall an der Frage aendert

Beide Wege oben passen darauf nicht. Ein Uebergabeweg macht aus jedem
Engine-Ticket eine Wartezeit auf die Doku-Lane; die Ausnahme "eigener Abschnitt
am Ende" erzeugt genau die Konflikte, die BE-3 von Hand aufgeloest hat.

Ein dritter Weg liegt naeher: Eine Seite, die mit jedem Ticket waechst, gehoert
keinem einzelnen Ticket. Entweder besitzt jedes Engine-Ticket sein eigenes
Bruchstueck und die Seite wird daraus gebaut, oder die Seite entsteht erst, wenn
alle Engines stehen — als eigenes Ticket am Ende der Welle, nicht mittendrin.

Welcher der drei Wege in CLAUDE.md landet, entscheidet der Nutzer. Dieses Ticket
sammelt die Faelle, bis er entschieden hat.

## Dritter Fall, waehrend dieses Ticket offen lag

BE-11 (#33, sophies Lane) hat `docs/grenzen.md` korrigiert — die Seite behauptete,
Docling lade erst beim ersten Zugriff, was nach dem Einhaengen des Lifespan nicht
mehr stimmte. `grenzen.md` gehoert dem Schnitt nach DOC-2 (#21).

Die Korrektur war richtig. Eine Seite, die nach dem Merge etwas Falsches ueber
das Verhalten sagt, ist schlimmer als eine Regelverletzung, und wer die Aenderung
gebaut hat, weiss als Einziger, dass die Aussage gekippt ist. Genau darin liegt
der Punkt: Die Regel verlangt hier etwas, das dem Ticket schadet.

Damit stehen drei Faelle nebeneinander, und alle drei zeigen dasselbe. Wer Code
aendert, weiss zuerst, was in der Doku nicht mehr stimmt. Wer die Doku besitzt,
erfaehrt es zuletzt. Der Schnitt stellt es andersherum.


## Vierter Fall: die Bedingung, unter der die Regel funktioniert

DOC-7 (#36) hat beim wiederholten Grep eine zweite Stelle gefunden —
`docs/betrieb/konfiguration.md:83` sagt weiterhin, Docling lade die Modelle „beim
ersten Aufruf". Die Datei gehoert DOC-6 (#34). akar-12 hat sie nicht angefasst,
sondern gemeldet.

Das ist regelkonform, und es hat funktioniert. Aber es hat nur funktioniert, weil
#34 offen war und den Befund aufnehmen konnte. Haette es kein offenes Ticket auf
dieser Datei gegeben, waere die einzige regelkonforme Handlung „melden und
hoffen" gewesen — und ein Befund, der niemandem gehoert, verfaellt.

Die ersten drei Faelle zeigen, dass Wissen und Dateieigentum auseinanderfallen.
Dieser zeigt, woran die Regel haengt: dass jemand den Befund auffaengt. Solange
ein PO die Meldungen liest und daraus Tickets schneidet, geht es auf. Ohne diese
Stelle ist die Regel eine Sackgasse, kein Weg.

## Stand der Faelle

Vier Faelle, vier Formen desselben Problems:

1. `docs/entwicklung.md` — fremdes Ticket schreibt hinein (BE-9), Merge-Konflikt.
2. `docs/formate.md` — eine Datei, die sieben Tickets anfassen mussten (BE-2..BE-9).
3. `docs/grenzen.md` — Code-Ticket korrigiert eine Aussage, die es selbst
   ungueltig gemacht hat (BE-11). Die Regel haette verlangt, die falsche Aussage
   stehen zu lassen.
4. `docs/betrieb/konfiguration.md` — Doku-Ticket findet und meldet; getragen hat
   es nur der Zufall eines offenen Zieltickets.

[[2026-08-31]] Mon 13:41
Fuenfter Fall, und er zeigt die Kehrseite des vierten. DOC-6 (#34) foerderte einen Fehler in `docs/grenzen.md:58` zutage — dieselbe falsche OCR-Schreibweise. Diesmal gab es kein offenes Ticket, das den Befund haette auffangen koennen: `grenzen.md` gehoert DOC-2 (#21), und das ist geschlossen. Der Subagent liess die Stelle richtigerweise stehen, weil die Datei ihm nicht gehoert. Ohne die Meldung an den PO waere der Befund verloren gewesen; er liegt jetzt als DOC-9 (#42) vor. Fall vier zeigte, dass ein offenes Nachbarticket den Befund auffaengt; Fall fuenf zeigt, dass es das nur zufaellig tut. Gemeldet von akar.

[[2026-08-31]] Mon 14:05
Verwandt: PROC-3 (#43) sammelt eine andere Bauart desselben Tages — die Pruefung, die unter der zu pruefenden Annahme geschrieben wurde. PROC-1 fragt, wem eine Datei gehoert; PROC-3 fragt, was gilt, wenn eine Pruefung abweicht.
