---
id: 17
title: 'FE-5 · Optionen: Enginewahl und OCR-Schalter aus /api/capabilities'
status: done
priority: medium
created: 2026-08-31T10:20:21.574451025+02:00
updated: 2026-08-31T11:08:56.694389043+02:00
started: 2026-08-31T11:08:50.718194213+02:00
completed: 2026-08-31T11:08:50.718194213+02:00
assignee: benny
tags:
    - frontend
depends_on:
    - 14
class: standard
---

## Ziel

Dem Nutzer die Wahl geben, ohne ihm Unmoegliches anzubieten.

## Eigene Dateien

- `frontend/src/components/OptionsPanel.vue`
- `frontend/src/components/EngineSelect.vue`

## Vorgaben

- Die Auswahl steht auf "automatisch" und listet daneben, was
  `/api/capabilities` fuer die tatsaechlich vorhandenen Dateiformate hergibt.
  Eine Engine, die das hochgeladene Format nicht kann, erscheint nicht.
- Der OCR-Schalter erscheint nur, wenn das Backend OCR meldet.
- Eine Engine im Zustand `warming` wird als solche gekennzeichnet und ist waehlbar;
  eine im Zustand `unavailable` nicht.
- Die Optionen gelten fuer den naechsten Lauf, nicht rueckwirkend fuer bereits
  konvertierte Dateien.

## Pruefung

Mit dem Mock: Bei nur einer hochgeladenen `.epub` erscheint docling nicht in der
Auswahl. Bei abgeschaltetem OCR im Mock fehlt der Schalter.

[[2026-08-31]] Mon 11:08
## Ergebnis benny-05

FE-5 umgesetzt auf task/17-options-panel, nach main gemergt (8e27e9a).

Gebaut: OptionsPanel.vue und EngineSelect.vue plus Unit-Tests unter
src/components/__tests__/OptionsPanel.test.ts (deckt beide Komponenten ab).
Kein Eingriff in App.vue, style.css oder fremde Komponenten. Der
Schnittstellen-Dreiklang bleibt unberuehrt; types.ts wurde nicht geaendert.

Ableitung aus /api/capabilities (ueber useCapabilities, kein eigener fetch):
Ohne Dateien stehen alle nutzbaren Engines zur Wahl. Liegen Dateien in der
Warteschlange, bleibt die Schnittmenge der Engines uebrig, die jede Endung
lesen koennen; Dateien in unbekanntem Format bleiben ausser Betracht, sonst
schnitte ihre leere Liste jede Engine weg. warming ist waehlbar und mit
'(laedt noch)' gekennzeichnet, unavailable erscheint nicht. Faellt die
gewaehlte Engine aus der Liste, springt die Auswahl auf 'automatisch' zurueck.
Der OCR-Schalter erscheint nur bei ocr_available.

### Pruefung

Tatsaechliche Ausgabe im Worktree, nach dem Merge von main:

    npm run test      -> Test Files 3 passed (3), Tests 19 passed (19)
    npm run typecheck -> keine Ausgabe, Exit 0
    npm run build     -> built in 1.08s

Gegen den Mock geprueft (VITE_KAIMARKIT_MOCK=1, curl /api/capabilities):
epub: ['pandoc', 'markitdown'] — docling steht dort nicht und erscheint
folglich nicht in der Auswahl. engines: markitdown ready, docling warming,
pandoc ready; ocr_available: true. Der Fall 'OCR abgeschaltet' laesst sich am
Mock nicht einstellen und steht deshalb im Test: bei ocr_available false
fehlen Schalter und Feld ganz.

### Fuer FE-7 (#19) zum Verdrahten in App.vue

    <OptionsPanel v-model="options" :filenames="filenames" />

- modelValue: ConvertOptions, v-model. Passt auf 'options' aus useConversion():
  const { options, entries } = useConversion().
- filenames?: string[], Vorgabe []. Die Dateinamen der Warteschlange, etwa
  computed(() => entries.value.map((e) => e.filename)).
- Emit: update:modelValue mit einem neuen ConvertOptions-Objekt.
- Die Komponente ruft load() selbst und zeigt Ladehinweis und Fehler aus
  useCapabilities. Sie bringt eine eigene h2 'Optionen' mit
  (aria-labelledby='options-heading').
- EngineSelect ist eigenstaendig nutzbar: modelValue, engines, states, id.
- Die Gestaltung ist absichtlich schlicht (Tailwind-Grundklassen). Feinschliff,
  Dark Mode und Tastaturbedienung gehoeren zu FE-7.

### Doku-Luecke

Wie schon bei FE-2 vermerkt fehlt docs/entwicklung.md, weil DOC-1 und DOC-2
offen sind. Dorthin gehoert, dass die Oberflaeche keine Engineliste kennt,
sondern jede Auswahl aus /api/capabilities ableitet — eine neue Engine braucht
deshalb keine Aenderung im Frontend. Dokumentiert ist das vorerst nur in den
Kopfkommentaren der beiden Komponenten.
