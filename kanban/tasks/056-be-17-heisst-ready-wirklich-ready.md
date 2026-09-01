---
id: 56
title: BE-17 · Heisst ready wirklich ready?
status: backlog
priority: medium
created: 2026-09-01T10:24:25.93867698+02:00
updated: 2026-09-01T10:24:25.93867698+02:00
assignee: sophie
tags:
    - backend
    - bug
class: standard
---

## Befund (01.09.2026, aus IN-9 im laufenden Container)

Der Container galt **nach 9 Sekunden** als `healthy`, und `/api/capabilities` meldete
von Anfang an alle drei Engines auf `ready`. Der erste Docling-Aufruf danach brauchte
trotzdem 32 Sekunden.

Die Dokumentation beschreibt etwas anderes: `docs/betrieb/lokal.md` nennt das Warten
als dritten Schritt und sagt, `/api/capabilities` melde Docling so lange als
`warming`. Dieser Zustand war nie zu sehen.

## Die Frage

Ist Docling nach 9 Sekunden wirklich geladen, oder heisst der Zustand nur so? Zwei
Faelle mit verschiedenen Folgen:

- **Der Zustand stimmt**, und die 32 Sekunden gehen auf den ersten Aufruf selbst.
  Dann ist die Doku zu aendern, nicht der Code.
- **Der Zustand stimmt nicht** — `ready` wird gemeldet, bevor der Konverter steht.
  Dann verspricht `/api/capabilities` etwas, das es nicht halten kann, und ein
  Frontend, das sich darauf verlaesst, schickt zu frueh.

Was von beidem zutrifft, entscheidet die Messung, nicht die Vermutung.

## Eigene Dateien

- `backend/app/` — die Stelle, die `warming` und `ready` setzt
- `backend/tests/` — der zugehoerige Test
- `docs/betrieb/lokal.md` (Abschnitte "Drei Schritte" und "Was vorher da sein muss")

Nicht der Abschnitt "Pruefen, ob der Dienst antwortet" — der gehoert DOC-11 (#57).

## Pruefung

- Gemessen ist, wann der Konverter tatsaechlich bereit ist, und wann
  `/api/capabilities` es sagt. Beide Zahlen stehen in der Ticketnotiz.
- Gehen sie auseinander, meldet `/api/capabilities` `warming`, bis der Konverter
  steht — mit einem Test, der ohne die Korrektur fehlschlaegt.
- Stimmen sie ueberein, ist `docs/betrieb/lokal.md` berichtigt und sagt nicht mehr
  Warten voraus, wo keines noetig ist.

## Zurueckgestellt

Vom Nutzer zurueckgestellt, bis die Abnahmefassung steht (01.09.2026).
