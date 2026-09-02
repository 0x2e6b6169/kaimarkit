---
id: 93
title: FE-16 · Verweis auf das GitHub-Repository im Kopf
status: done
priority: medium
created: 2026-09-02T15:29:39.533322182+02:00
updated: 2026-09-02T16:42:18.410869025+02:00
started: 2026-09-02T15:40:41.143566091+02:00
completed: 2026-09-02T15:40:41.143566091+02:00
assignee: benny
class: standard
---

## Ziel

Die Oberfläche verweist auf das Repository. Oben rechts im Kopf steht das
GitHub-Zeichen als Verweis auf `https://github.com/0x2e6b6169/kaimarkit`; wer
darauf zeigt oder mit der Tastatur dorthin springt, erfährt, wohin er kommt.

## Eigene Dateien

- `frontend/src/App.vue`
- `frontend/src/App.test.ts`

Keine weiteren. Das Zeichen kommt als eingebettetes SVG in die Vorlage, nicht als
Datei unter `public/` und nicht als Abhängigkeit.

## Vorgaben

**Die Adresse steht fest im Quelltext.** Konvention 4 gilt für Betriebsgrößen;
die eigene Repository-Adresse ist keine. Keine `VITE_`-Variable dafür anlegen.

**Das Zeichen ist Octicons `mark-github`** (24x24, ein einzelner `<path>`, MIT).
Als `fill="currentColor"` mit `aria-hidden="true"` einbetten, damit es die
Vordergrundfarbe des Kopfes erbt und im Dark Mode ohne Zutun stimmt.

**Der Verweis trägt den zugänglichen Namen.** Das SVG ist versteckt, also gehört
der Name an das `<a>`:

    aria-label="kaimarkit auf GitHub"

Dazu `target="_blank"` und `rel="noopener noreferrer"`. Sichtbarer Text ist nicht
nötig, ein `title` ersetzt den `aria-label` nicht.

**Platz.** Der Kopf ist heute `flex flex-col gap-2` mit `<h1>` und Absatz. Das
Zeichen steht auf der Höhe der Überschrift, rechts außen — also eine Zeile aus
Überschrift und Verweis, darunter der Absatz unverändert. Der Beschreibungstext
bleibt Wort für Wort, wie er ist.

**Fokus sichtbar.** Der Verweis bekommt denselben sichtbaren Fokusring wie die
übrigen Bedienelemente der Seite; nicht neu erfinden, sondern die vorhandene
Klasse übernehmen.

## Prüfung

1. Neuer Test in `App.test.ts`: Der Verweis wird über seinen zugänglichen Namen
   gefunden und sein `href` ist genau `https://github.com/0x2e6b6169/kaimarkit`.
   Der Test fällt vor der Änderung durch — einmal belegen.
2. `npm run test` — Datei- und Testzahl mitnennen, nicht nur "bestanden".
3. `npm run typecheck`
4. `npm run build`

[[2026-09-02]] Wed 15:40
## Ergebnis (benny-17)

Die Kopfzeile ist jetzt eine Zeile aus `<h1>` und Verweis, darunter der Absatz unveraendert. Das `<a>` traegt `aria-label="kaimarkit auf GitHub"`, `target="_blank"` und `rel="noopener noreferrer"`; das SVG ist `aria-hidden`, `fill="currentColor"`, `viewBox="0 0 24 24"`, Groesse ueber `h-6 w-6 sm:h-7 sm:w-7`.

Zwei Abweichungen vom Rumpf, beide bewusst:

1. **Der Pfad kommt aus der Quelle**, nicht aus dem Rumpf. `primer/octicons`, `icons/mark-github-24.svg` (MIT), per `curl` geholt. Er weicht vom Pfad im Ticketrumpf ab — der zitiert eine aeltere Fassung desselben Zeichens. Der Rumpf verlangt die Quelle, wo sie erreichbar ist; sie war es.
2. **Eine Fokusring-Klasse zum Uebernehmen gibt es nicht.** Der Ring kommt global aus `style.css` ueber `*:focus-visible` und gilt fuer den Verweis ohne Zutun. Nichts nachgebaut; ein Kommentar in `App.vue` haelt es fest.

**Rot vor gruen belegt.** Vor der Aenderung an `App.vue`: `Test Files 1 failed | 8 passed (9)`, `Tests 1 failed | 101 passed (102)`. Danach: `Test Files 9 passed (9)`, `Tests 102 passed (102)`. `npm run typecheck` und `npm run build` ohne Befund.

**Doku:** Keine Seite unter `docs/` beschreibt den Kopf der Oberflaeche; der Abschnitt „Ueber die Oberflaeche" in `docs/schnellstart.md` wird durch den Verweis nicht unwahr. Nichts zu berichtigen.

Nur `frontend/src/App.vue` und `frontend/src/App.test.ts` angefasst — keine Grenzueberschreitung.
