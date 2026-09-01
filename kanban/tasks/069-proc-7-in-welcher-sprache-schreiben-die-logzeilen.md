---
id: 69
title: PROC-7 · In welcher Sprache schreiben die Logzeilen?
status: backlog
priority: low
created: 2026-09-01T12:27:39.711725977+02:00
updated: 2026-09-01T12:27:39.711725977+02:00
assignee: akar
tags:
    - process
    - backend
class: standard
---

## Die Frage (aufgeworfen von sophie in BE-22, 01.09.2026)

`backend/app/converters/docling.py:163` protokolliert
`log.warning("Docling ist nicht verfuegbar: %s")` — deutsch, in ASCII-Umschrift. Es
ist keine Meldung an den Nutzer, sondern eine Zeile für den Betreiber, und blieb in
BE-22 deshalb zu Recht draußen.

Damit steht eine Entscheidung offen, die alle `log.*`-Aufrufe im Backend betrifft.

## Warum das keine Umschrift-Sache ist

`CLAUDE.md` trennt Code und deutsche Prosa. Eine Logzeile liegt dazwischen: Sie ist
kein Bezeichner, aber auch kein Text für den Nutzer. Wer sie liest, liest sie neben
Meldungen von uvicorn, docling und torch — die alle englisch sind.

Drei Antworten sind vertretbar:

1. **Englisch**, wie der übrige Code und wie die Bibliotheken daneben. Eine Logdatei
   liest sich dann in einer Sprache.
2. **Deutsch mit Umlauten**, wie die Meldungen an den Nutzer. Eine Regel für alles,
   was ein Mensch liest.
3. **So lassen.** Dann bleibt die Umschrift dort stehen, wo sie heute ist, und
   wächst bei jeder neuen Logzeile nach.

Der PO hält 1 für richtig — aber es ist eine Entscheidung des Nutzers, nicht des
Boards, weil sie die Prosa-Regel berührt.

## Reichweite

Alle `log.*`-Aufrufe unter `backend/app/`, dazu ein Satz in `CLAUDE.md`, Abschnitt
"Prosa". Fällt die Entscheidung für 1 oder 2, gehört sie außerdem in die Vorlage
`assets/claude-md-abschnitte.md` in dot-claude.

## Prüfung

Der Nutzer hat sich entschieden, `CLAUDE.md` sagt es ausdrücklich, und die Logzeilen
folgen der Entscheidung einheitlich.

## Zurückgestellt

Vom PO zurückgestellt: Es hält niemanden auf und betrifft keinen Nutzer.
