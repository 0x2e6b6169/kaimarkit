---
id: 130
title: 'FE-27 · Der Knopf heisst Vorschau, nicht Aufklappen (GitHub #6)'
status: todo
priority: medium
created: 2026-09-07T10:36:04.682327835+02:00
updated: 2026-09-07T10:36:04.682327835+02:00
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
