---
id: 105
title: 'FE-20 · Enginewahl als Schaltergruppe mit Erklärung, im Browser gemerkt (GitHub #3)'
status: todo
priority: medium
created: 2026-09-03T11:20:25.65723296+02:00
updated: 2026-09-03T11:20:25.65723296+02:00
assignee: benny
tags:
    - frontend
    - gh-3
depends_on:
    - 104
class: standard
---

## Ziel

GitHub-Issue #3: Das Auswahlfeld für die Engine verwirrt. An seine Stelle tritt eine Gruppe von Schaltflächen, von denen genau eine gewählt ist. Neben jedem Namen steht ein Halbsatz, wofür die Engine gut ist; ein Info-Zeichen dahinter zeigt bei Hover **und** Tastaturfokus eine längere Erklärung. Die zuletzt gewählte Engine bleibt im Browser über Sitzungen hinweg gemerkt. Ist nichts gemerkt, ist `markitdown` vorgewählt.

## Entscheidungen des Nutzers

- **Schaltergruppe statt Auswahlfeld.** Echte `<input type="radio">` in einem `<fieldset>` mit gestalteten Labels sind das Einfachere und bringen Pfeiltasten und Screenreader-Semantik mit. Wer stattdessen `<button>` mit `role="radio"` baut, baut die Tastaturbedienung nach.
- **Merken über Sitzungen hinweg.** Im Issue steht „Cookie"; gemeint ist „bleibt im Browser". Der Dienst hat keinen Sitzungszustand und keinen Server, der ein Cookie läse. Deshalb `localStorage`, Schlüssel `kaimarkit.engine`. Gemerkt wird nur die Engine, nicht der OCR-Schalter.
- **Vorgabe `markitdown`,** wenn nichts gemerkt ist. Bisher war es `auto`. `automatisch` bleibt als Schaltfläche wählbar (Kurztext: wählt je Dateiendung die erste Engine, die der Dienst dafür nennt), ist aber nicht mehr die Vorgabe. `KAIMARKIT_DEFAULT_ENGINE` gilt weiter für `auto` und für API-Aufrufe ohne Engine; daran ändert sich nichts.
- **Kurz- und Langtext je Engine** liegen im Frontend, als Tabelle Name → { kurz, lang } in `EngineSelect.vue`. Angeboten wird weiterhin nur, was `/api/capabilities` nennt; das Bauteil entscheidet nicht nach Namen. Nur die Texte kennen Namen, und ein Name ohne Eintrag bekommt keinen Text und keinen Fehler. Die Aussagen stammen aus `docs/formate.md`, Abschnitte „Docling", „MarkItDown", „Pandoc". Kurz: ein Halbsatz („schnell, ohne Modelle, breite Formatliste"). Lang: drei bis fünf Sätze.

## Eigene Dateien

- `frontend/src/components/EngineSelect.vue`
- `frontend/src/components/__tests__/EngineSelect.test.ts`
- `frontend/src/components/OptionsPanel.vue`
- `frontend/src/components/__tests__/OptionsPanel.test.ts`
- `frontend/src/composables/useConversion.ts`
- `frontend/src/composables/useConversion.test.ts`
- `frontend/src/App.test.ts`, falls dort auf das `<select>` zugegriffen wird (FE-19 (#104) ist vorher durch, deshalb keine Kollision)
- `docs/schnellstart.md` (Abschnitt „Über die Oberfläche"), falls dort das Auswahlfeld beschrieben ist

## Vorgaben

- Fällt die gemerkte Engine aus dem Angebot (nicht installiert, oder die Warteschlange enthält Dateien, die sie nicht liest), gilt die bestehende Regel aus `OptionsPanel.vue`: Rücksprung auf `auto`, ohne den gemerkten Wert zu überschreiben. Beim nächsten Besuch ist sie wieder da.
- Eine nicht anbietbare Engine wird als Schaltfläche **deaktiviert** gezeigt, nicht versteckt, mit dem Grund im `title` (lädt noch, nicht installiert, liest diese Dateien nicht). Sonst ändert die Gruppe ihre Form, je nachdem, was in der Warteschlange liegt.
- Das Info-Zeichen ist ein `<button type="button">` mit `aria-describedby` auf den Langtext; der Text erscheint bei Hover und bei Tastaturfokus und schließt mit Escape. Ein Hover-Text, den nur die Maus erreicht, fällt in der Prüfung durch.
- `localStorage` kann werfen (privates Fenster, blockierte Site-Daten). Lesen und Schreiben in `try/catch`; ohne Speicher gilt `markitdown`.
- Zugriff auf `localStorage` nur in `useConversion.ts`: ein Ort, ein Schlüssel.
- Bestehende Tests, die `<select>` oder `<option>` finden, werden auf die neue Form umgeschrieben, nicht gelöscht.

## Prüfung

1. Vorher rot, nachher grün, als neue Tests:
   - Ohne gemerkten Wert ist `markitdown` gewählt.
   - Nach einer Wahl steht der Name unter `kaimarkit.engine` im `localStorage`; ein neu erzeugtes `useConversion()` liest ihn zurück.
   - Ein werfendes `localStorage` (Attrappe) lässt die Vorgabe bei `markitdown` und wirft nicht weiter.
   - Jede angebotene Engine hat einen Kurztext; der Langtext ist über `aria-describedby` erreichbar.
   - Eine Engine, die die Warteschlange ausschließt, ist als deaktivierte Schaltfläche vorhanden.
2. `cd frontend && npm run test`, `npm run typecheck`, `npm run build` grün.
3. `grep -n '<select' frontend/src/components/EngineSelect.vue` findet nichts mehr.
4. Von Hand gegen das Backend: Wahl treffen, Seite neu laden, Wahl steht noch. Mit Tab bis auf das Info-Zeichen: Erklärung sichtbar.
