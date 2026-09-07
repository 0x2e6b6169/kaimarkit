---
id: 130
title: 'FE-27 · Der Knopf heisst Vorschau, nicht Aufklappen (GitHub #6)'
status: done
priority: medium
created: 2026-09-07T10:36:04.682327835+02:00
updated: 2026-09-07T10:40:48.628454141+02:00
started: 2026-09-07T10:40:48.050828748+02:00
completed: 2026-09-07T10:40:48.050828748+02:00
assignee: benny
tags:
    - frontend
    - gh-6
class: standard
---

## Ziel

GitHub-Issue #6: Das Wort "Aufklappen" im GUI stört, "Vorschau" trifft die Sache. Der
Knopf an jeder Zeile der Warteschlange zeigt oder verbirgt die Markdown-Vorschau; sein
Text soll das auch so nennen.

## Eigene Dateien

- `frontend/src/components/FileRow.vue` und der Test dazu
- `frontend/src/App.test.ts` — Zeile 156 sucht den Knopf über den Text "Aufklappen"
  und würde sonst falsch grün bleiben, statt mit dem geänderten Text zu brechen

Nicht hier: `frontend/src/components/MarkdownPreview.vue` und sein Test. Das Wort
"Aufklappen" steht dort nur in einer Kommentarzeile und einem Testnamen, nicht im GUI
— Issue #6 meint den sichtbaren Text, dort ist keiner.

## Vorgaben

- Der Knopftext im eingeklappten Zustand wird "Vorschau" (statt "Aufklappen").
- Der Text im aufgeklappten Zustand (aktuell "Zuklappen") passt dazu — Wortlaut nach
  Ermessen der Lane, z. B. "Vorschau schließen" oder "Ausblenden"; wichtig ist, dass
  beide Zustände weiterhin eindeutig zueinander gehören.
- `aria-expanded` und `aria-controls` bleiben unverändert; nur der sichtbare Text
  ändert sich.
- Den alten Wortlaut über alle Tests greppen (nicht nur die eigene Datei), bevor die
  Dateiliste als vollständig gilt.

## Prüfung

- Rot vor grün: ein Test, der den neuen Knopftext prüft, fällt vor der Arbeit durch.
- Kein Test bricht durch den geänderten Text unbemerkt (App.test.ts angepasst).
- `npm run test`, `npm run typecheck` sauber.

## Ergebnis (benny-31)

Knopftext: „Vorschau“ eingeklappt, „Vorschau schließen“ aufgeklappt. Das Substantiv
bleibt in beiden Zuständen stehen; wer den einen Text gelesen hat, erkennt den anderen
als dieselbe Sache wieder, und „schließen“ benennt die Handlung.

Rot vor grün, zweimal belegt:

1. Neuer Test `nennt den Knopf nach dem, was er zeigt` in `FileRow.test.ts` vor der
   Änderung an `FileRow.vue`:
   `AssertionError: expected 'Aufklappen' to be 'Vorschau'` — 1 failed | 144 passed (145).
2. Nach der Änderung an `FileRow.vue`, mit dem noch alten Suchtext in `App.test.ts`:
   `App.test.ts:157 AssertionError: expected undefined to be defined` — der Knopf war
   über `button.text() === 'Aufklappen'` nicht mehr zu finden. Erst danach den Suchtext
   auf 'Vorschau' gezogen.

Grep über das ganze Arbeitsverzeichnis (ohne node_modules, .git, kanban) nach
Aufklappen/Zuklappen: `FileRow.vue` (Knopftext Zeile 171, Kommentar Zeile 47),
`App.test.ts` (Kommentar Zeile 153, Suchtext Zeile 156), `FileRow.test.ts` (Kommentar,
Testname), `MarkdownPreview.vue` (Zeile 13, im JSDoc-Block), `MarkdownPreview.test.ts`
(Zeile 75, Testname), `ENTWURF.md` Zeile 262. Der Ausschluss von `MarkdownPreview.vue`
und seinem Test hat gestimmt: dort steht das Wort nur im Blockkommentar und in einem
Testnamen, keine sichtbare Zeichenkette. Kein Schnittfehler.

Gemeldet statt geändert: `ENTWURF.md` Zeile 262 („Fertige Zeilen lassen sich
aufklappen…“) beschreibt das Verhalten, nicht den Knopftext, und bleibt damit richtig.
Die Kommentare in `FileRow.vue` (Zeile 47), `FileRow.test.ts` und `App.test.ts` reden
weiter vom Auf- und Zuklappen; das ist die Bewegung, nicht die Beschriftung, und stand
nicht im Ticket.

aria-expanded und aria-controls unverändert. Tests: Test Files 10 passed (10),
Tests 145 passed (145). `npm run typecheck` und `npm run build` sauber.
Branch task/130-preview-button-label, Merge 
4574b0d.
