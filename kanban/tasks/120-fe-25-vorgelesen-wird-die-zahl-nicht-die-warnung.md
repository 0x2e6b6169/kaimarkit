---
id: 120
title: FE-25 · Vorgelesen wird die Zahl, nicht die Warnung
status: todo
priority: medium
created: 2026-09-03T14:59:45.209459852+02:00
updated: 2026-09-03T14:59:45.209459852+02:00
assignee: benny
tags:
    - frontend
depends_on:
    - 119
class: standard
---

## Ziel

Nebenbefund aus bennys Leseauftrag zur Warnungsanzeige (03.09.2026): Der Wortlaut einer
Warnung steht ausgeschrieben in der Warteschlange — `FileRow.vue:216-226`, Text in Zeile
224, ohne Klick, außerhalb des aufklappbaren Teils. **Vorgelesen wird er nicht.**

Die Ansage der Warteschlange nennt nur die Zahl: „… ist fertig, mit 1 Warnung."
(`FileQueue.vue:48-52`, vorgelesen im `role="log"`-Bereich, Zeilen 92-94). Die
Abschlussansage der Anwendung erwähnt Warnungen überhaupt nicht (`App.vue:104-116`). Der
Text steht im DOM, aber außerhalb jedes Live-Bereichs.

Wer sieht, liest den vollen Text. Wer nur zuhört, erfährt eine Zahl. Und die Zahl ist
genau die Auskunft, aus der der Nutzer bei GitHub-Issue #2 nicht klüger wurde — mit dem
Unterschied, dass er den Text daneben wenigstens lesen konnte.

## Eigene Dateien

- `frontend/src/components/FileQueue.vue` und `FileQueue.test.ts`
- `frontend/src/App.vue` und `App.test.ts`

Nicht hier: `FileRow.vue` — die sichtbare Anzeige stimmt und wird nicht angefasst.
Nicht hier: `types.ts`, `api.ts`, `useConversion.ts`, `download.ts`. Die Warnungen liegen
im Eintrag bereits vor (`types.ts:52` → `useConversion.ts:110,296` → `App.vue:265` →
`FileQueue.vue:99-102`); es fehlt allein die Ansage.

Wartet auf FE-24 (#119): Das Ticket ändert `App.vue` und darf nicht gleichzeitig laufen.

## Vorgaben

- Die Ansage nennt den Wortlaut, nicht nur die Zahl. Bei mehreren Warnungen an einer
  Datei entscheidet die Umsetzung, ob sie alle vorgelesen werden oder die erste mit einem
  Zusatz — begründet in der Notiz, nicht stillschweigend.
- Die sichtbare Anzeige ändert sich nicht. Wer sieht, sieht danach dasselbe wie vorher.
- Die Abschlussansage der Anwendung sagt, ob Warnungen vorliegen. Sie muss sie nicht
  aufzählen; sie darf sie nur nicht verschweigen.
- Kein `aria-label`, das den sichtbaren Text verdoppelt und ihn zweimal vorlesen lässt.

## Prüfung

- Rot vor grün: Ein Test, der einen Eintrag mit einer Warnung fertigstellt und den
  Wortlaut im `role="log"`-Bereich erwartet, fällt vor der Arbeit durch und nennt als
  Ist-Wert die Fassung mit der bloßen Zahl.
- Ein Test belegt, dass die Abschlussansage das Vorliegen von Warnungen erwähnt.
- Ein Test belegt, dass der sichtbare Text an der Zeile unverändert genau einmal vorkommt.
- `npm run test`, `npm run typecheck`, `npm run build` grün; Basislinie in die Notiz.
