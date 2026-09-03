---
id: 120
title: FE-25 · Vorgelesen wird die Zahl, nicht die Warnung
status: done
priority: medium
created: 2026-09-03T14:59:45.209459852+02:00
updated: 2026-09-03T15:48:27.492736431+02:00
started: 2026-09-03T15:48:09.632242445+02:00
completed: 2026-09-03T15:48:09.632242445+02:00
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

Uebernommen von zwei serverfehler-beendeten Vorgaengern (Code stand fertig auf 2de54cd,
Worktree sauber). Rebase auf main (2x noetig, main zog waehrenddessen zwei weitere
CLAUDE.md-Commits nach) blieb konfliktfrei -- der fehlende Commit fasste kein Frontend an.

Mehrfachwarnung, aus dem Diff abgelesen (FileQueue.vue:44-51,54-63): Bei mehreren
Warnungen liest die Ansage jede einzelne vor (mit Leerzeichen verkettet), nicht die erste
mit einem Zusatz. Begruendung steht im Docstring: die uebrigen Warnungen liessen sich sonst
nur dort nachlesen, wo der Zuhoerer gerade nicht hinsieht -- ein Zusatz waere fuer ihn eine
Sackgasse.

Vitest: 10 Testdateien / 140 Tests gruen (Basislinie vor FE-25: 10/137; FE-25 fuegt drei
Tests hinzu: zwei in FileQueue.test.ts, einen in App.test.ts). typecheck und build gruen.

FE-22-Test bereits vom Vorgaenger billiger gemacht (App.test.ts, "nimmt nur so viele
Eintraege an ..."): convertFile/convertUrl liefern jetzt ein nie aufloesendes Promise, die
Zusicherung bleibt auf die Aufnahme beschraenkt (kein Warten auf zwanzig fertige
Konvertierungen). Laufzeit im Gesamtlauf 10,3 s (Zeitueberschreitung) -> 0,7-0,8 s
(gemessen: 704 ms).

Zwei Antworten fuer den Handtest-Tag:
(a) Nein. FileQueue.test.ts ("laesst den sichtbaren Wortlaut genau einmal an der Zeile
stehen") belegt, dass der Warnungstext genau einmal im DOM steht und kein aria-label ihn
verdoppelt. Die beiden Live-Bereiche (App.vue:301 data-test="app-log" und der sr-only
role="log" in FileQueue.vue) sagen zudem verschiedenen Text an -- App nennt nur, dass und
an wie vielen Eintraegen Warnungen vorliegen (App.vue:127-134), die Zeile liest den
Wortlaut (FileQueue.vue:54-63). Keine doppelte Ansage desselben Textes durch Quellcode
belegbar; ob ein konkreter Screenreader bei Entfernen alter log-Eintraege erneut vorliest,
bleibt unsicher -- das haengt vom AT ab, nicht vom Quelltext.
(b) Ohne Screenreader ist der Effekt nicht sichtbar -- die sichtbare Anzeige aendert sich
laut Vorgabe nicht, und das stimmt: FileRow.vue:213-224 (amber Warnungsbox) ist unveraendert.
Im DOM-Inspektor sieht man es dennoch: im sr-only-Bereich role="log" in FileQueue.vue steht
nach Abschluss einer Datei mit Warnung jetzt der volle Satz ("... ist fertig, mit 1 Warnung:
<Wortlaut>.") statt nur der Zahl, und in [data-test="app-log"] (App.vue) haengt am
Abschlusssatz "Warnungen stehen an einem Eintrag." (bzw. "an N Eintraegen").

Merge: 5771e68 (--no-ff auf main). Worktree .worktrees/task-120 entfernt.
Fremder Worktree .worktrees/task-121 (andere Lane) unangetastet gelassen.

[[2026-09-03]] Thu 15:48
**Berichtigung des Rumpfs (katche).** Im Ziel steht: "Und die Zahl ist genau die
Auskunft, aus der der Nutzer bei GitHub-Issue #2 nicht klueger wurde - mit dem
Unterschied, dass er den Text daneben wenigstens lesen konnte." Der Satz ist falsch.
Der Nutzer hat inzwischen geantwortet, seine Erinnerung an eine Warnung sei falsch
gewesen; es stand gar keine da. Seine Datei war ein Word-Dokument, und MarkItDown warnt
dort nicht.
Der Satz ist gestrichen zu lesen. Am Ticket aendert das nichts: FE-25 steht aus eigenem
Recht - vorgelesen wird die Zahl statt des Wortlauts, das betrifft jede Warnung und
jeden, der zuhoert statt zu lesen. Es gehoert nicht zu Issue #2 und traegt deshalb auch
kein gh-2.
Befund von benny, der den Satz beim Verteilen bemerkt hat.
