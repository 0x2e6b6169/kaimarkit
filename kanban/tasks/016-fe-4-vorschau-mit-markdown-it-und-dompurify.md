---
id: 16
title: FE-4 · Vorschau mit markdown-it und DOMPurify, Rohtext, Kopieren
status: done
priority: medium
created: 2026-08-31T10:20:20.872199631+02:00
updated: 2026-08-31T11:06:45.650117282+02:00
started: 2026-08-31T11:06:38.455656925+02:00
completed: 2026-08-31T11:06:38.455656925+02:00
assignee: benny
tags:
    - frontend
depends_on:
    - 14
class: standard
---

## Ziel

Das Ergebnis ansehen, bevor es weitergegeben wird - der eigentliche Zweck des
Werkzeugs.

## Eigene Dateien

- `frontend/src/components/MarkdownPreview.vue`

## Vorgaben

- Zwei Reiter: gerendertes Markdown und Rohtext.
- `markdown-it` zum Rendern, **immer** durch `DOMPurify` gefiltert. Das Markdown
  stammt aus fremden Dokumenten; ungefiltert eingefuegtes HTML ist eine
  Einladung zu XSS.
- Kopieren in die Zwischenablage mit sichtbarer Rueckmeldung.
- Lange Ergebnisse bremsen die Seite nicht: gerendert wird erst beim Aufklappen.
- Breite Tabellen und Codebloecke scrollen in ihrem eigenen Bereich, die Seite
  selbst scrollt nicht waagerecht.

## Pruefung

Ein Ergebnis mit Tabelle, Codeblock und einem `<script>`-Versuch im Quelltext:
Tabelle und Code werden dargestellt, das Skript nicht ausgefuehrt. Umschalten
zwischen den Reitern behaelt die Scrollposition nicht bei - das ist in Ordnung.

[[2026-08-31]] Mon 11:06
## Ergebnis FE-4

Umgesetzt in `frontend/src/components/MarkdownPreview.vue`, Branch
`task/16-markdown-preview`, gemergt nach `main`.

**Aufbau.** Eine aufklappbare Sektion je Ergebnis, darin zwei Reiter (Vorschau,
Rohtext) und eine Kopieren-Schaltflaeche mit sichtbarer Rueckmeldung
(Kopieren -> Kopiert -> nach zwei Sekunden zurueck, dazu `role="status"` fuer
Screenreader).

**Die Filterung.** `markdown-it` laeuft mit `html: true`, damit eine aus PDF oder
docx gerettete HTML-Tabelle als Tabelle erscheint und nicht als Quelltext. Damit
reicht jedes Dokument beliebiges HTML bis an die Oberflaeche, und genau ein
Aufruf haelt es auf: `DOMPurify.sanitize()` im computed `rendered`. Ohne ihn
steht das Skript im Ergebnis - mit `markdown-it` allein nachgeprueft, die Ausgabe
beginnt mit `<script>window.x=1</script>` und enthaelt `onerror="y"`. Der
Kommentarkopf der Datei sagt das, damit niemand spaeter ein zweites `v-html`
danebensetzt.

**Erst beim Aufklappen gerendert.** `rendered` ist ein `computed` und steht nur
unter `v-if`; ein zugeklapptes Ergebnis kostet nichts. Tabellen (`display: block`)
und `pre` scrollen in ihrem eigenen Bereich, die Seite selbst nicht.

**Pruefung, alles ausgefuehrt.**

- `npm run test` -> `Test Files 2 passed (2) | Tests 9 passed (9)`, darunter die
  fuenf neuen Faelle. Der Ticketfall - Tabelle, Codeblock und ein
  `<script>`-Versuch in einem Quelltext - steckt in `HOSTILE` und wird zweifach
  geprueft: `<table>` und `<code class="language-python">` sind da; `<script`,
  `onerror` und `href="javascript:` sind es nicht, und `window.__pwned` bleibt
  `undefined`.
- `npm run typecheck` -> sauber, Exit 0.
- `npm run build` -> `12 modules transformed`, `built in 803ms`. Die Komponente
  liegt noch nicht im Bundle, weil `App.vue` sie nicht importiert; das macht FE-7.

**Fuer FE-7, zum Einhaengen in `App.vue`:**

```vue
<MarkdownPreview
  :markdown="entry.markdown"
  :filename="entry.filename"
  v-model:open="offen"
  @copied="ansagen"
/>
```

- `markdown: string | null` - `null` oder leer zeigt „Noch kein Ergebnis."
- `filename?: string` - nur Beschriftung, Vorgabe „Ergebnis"
- `v-model:open?: boolean` - Vorgabe `false`; ohne Bindung regelt die Komponente
  das Aufklappen selbst
- Event `copied` - nach erfolgreichem Kopieren, gedacht fuer die globale
  `aria-live`-Region von FE-7

Eigene Styles liegen `scoped` in der Komponente, `style.css` wurde nicht angefasst.

**Doku-Luecke** (wie schon bei FE-2): `docs/entwicklung.md` fehlt, DOC-1 und DOC-2
sind offen. Dorthin gehoert spaeter der Satz, dass Markdown aus fremden Dokumenten
ausschliesslich ueber `MarkdownPreview` in die Seite gelangt und dass DOMPurify
dort die einzige Grenze ist.
