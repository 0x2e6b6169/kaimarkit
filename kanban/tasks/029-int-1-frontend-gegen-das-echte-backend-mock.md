---
id: 29
title: INT-1 · Frontend gegen das echte Backend, Mock entfernen
status: done
priority: medium
created: 2026-08-31T10:21:43.644388097+02:00
updated: 2026-08-31T11:58:41.344943969+02:00
started: 2026-08-31T11:57:46.409318849+02:00
completed: 2026-08-31T11:57:46.409318849+02:00
assignee: benny
tags:
    - frontend
depends_on:
    - 12
    - 19
    - 11
class: standard
---

## Ziel

Die beiden Straenge zusammenfuehren und die Attrappe entfernen.

## Eigene Dateien

- `frontend/src/mocks/` (Loeschung)
- Fehlerkorrekturen in beiden Straengen, wo die Wirklichkeit vom Vertrag abweicht

## Vorgaben

- Jede Abweichung zwischen Mock und echter API wird in `contracts/api.md`,
  `models.py` und `types.ts` gemeinsam geradegezogen - nicht einseitig im Frontend
  weggepatcht.
- Der Mock verschwindet vollstaendig, einschliesslich seiner Abhaengigkeiten in
  `package.json` und des Schalters in `vite.config.ts`.

## Pruefung

`npm run dev` gegen das laufende Backend: fuenf gemischte Dateien, darunter eine,
die fehlschlaegt. Vorschau, Einzeldownload und ZIP funktionieren.
`npm run typecheck` und `pytest -q` bleiben gruen.


---

## Notiz (benny-08)

Beide Straenge laufen gegen dieselbe Wirklichkeit. Der Mock ist weg, der Download
ist verdrahtet, drei Abweichungen sind geradegezogen. Branch
`task/29-integration`, gemergt als `merge: INT-1 frontend against the real
backend, mock removed`.

### Was der Mock hinterlassen hat

Geloescht: `frontend/src/mocks/` samt `busboy` und `@types/busboy` aus
`package.json`, der Schalter `VITE_KAIMARKIT_MOCK` aus `vite.config.ts`, der
`exclude`-Eintrag in `tsconfig.app.json` und die Mock-Pfade in
`tsconfig.node.json`. `npm run dev` reicht `/api` jetzt immer per Proxy an
`localhost:8000` weiter; ein Backend ist noetig.

Kein Test hing an der Attrappe des Dev-Servers. Die Faelle `...fehler...` und
`...warnung...` lebten allein im Mock; die Unit-Tests attrappieren `./api` und
pruefen den Vertrag, nicht den Mock. Es wurde deshalb kein Test geloescht.

### Die Verdrahtung des Downloads

`download.ts` hatte seit FE-6 keinen Aufrufer. Jetzt:

- `FileRow.vue` traegt "Herunterladen", sichtbar nur bei `hasResult(entry)`,
  mit dem Dateinamen als `sr-only`-Zusatz.
- `App.vue` traegt "Alles herunterladen", gesperrt solange `busy`, waehrend des
  Packens und ohne Ergebnis. Der Ausgang wird im `aria-live`-Bereich angesagt
  ("kaimarkit.zip steht bereit."), ein gescheiterter Archivbau steht als
  `role="alert"` daneben.
- Der Tastaturweg reicht damit von der Vorschau bis zum Download; alle neuen
  Bedienelemente sind `button` und stehen von selbst in der Tabreihenfolge.
  Geprueft im Browser: Zuklappen, Herunterladen, Entfernen, Ergebnis, Kopieren,
  Vorschau, Rohtext, naechste Zeile.
- Keine neue Farbstufe. Verwendet sind `slate-400` (Linie), `slate-100`
  (Flaeche), `slate-600` (Schrift) und die rote Meldungsgruppe -- alle mit der
  Rolle, die `style.css` ihnen gibt. In Chrome mit `colorScheme: dark` gemessen:
  Knopf `rgb(226,232,240)` auf durchsichtig, Rahmen `rgb(71,85,105)`.

### Abweichungen zwischen Vertrag und Wirklichkeit

**1. Ein fehlendes Docling meldete sich als `warming` -- dauerhaft.**
`meta.py::_state()` las `available()` des Adapters. Docling laedt sein Modul
absichtlich auch ohne die Bibliothek, damit ein fehlendes `docling` nicht als
`ImportError` endet; `get_converter()` gelingt dann, und `available()` ist False
-- beim Vorladen wie bei fehlender Bibliothek. Der Vertrag sagt, `unavailable`
heisse "nicht installiert oder defekt, wird nicht angeboten". Das Frontend bot
"docling (laedt noch)" an, und die Wahl endete in 400 `engine_unavailable`.
`_state()` fragt jetzt `state()` ab, wo eine Engine sie anbietet -- Docling hat
die Methode laengst, sie wurde nur nie gerufen. Der Rueckfall auf `available()`
bleibt fuer alle uebrigen. Test: `test_engine_reports_its_own_state`.
Das Protokoll in `converters/base.py` nennt `state()` jetzt als wahlweise.

**2. Die Meldungen nannten die temporaere Datei.** Live gesehen:
"Pandoc ist an tmpqwhm57ia.epub gescheitert" -- in der Zeile, in `warnings` und
in `_errors.txt` des Archivs. Der Vertrag verlangt in `error` eine lesbare
Meldung; ein Name, den der Nutzer nie vergeben hat, ist keine. `stored_upload`
legt die Datei jetzt unter ihrem gesaeuberten Namen in ein eigenes
`TemporaryDirectory`, das im `finally` mitsamt Inhalt verschwindet. Damit
stimmen die Meldungen aller drei Engines auf einen Schlag, ohne dass eine davon
angefasst werden musste. Konvention 5 gilt unveraendert und ist in `CLAUDE.md`
nachgezogen (`NamedTemporaryFile` zu `TemporaryDirectory`). Test:
`test_stored_file_keeps_the_name_it_arrived_under`.

**3. `passthrough` stand in `capabilities.engines`.** Nach der PO-Entscheidung
(Rumpf von #32) fuehrt `engines` nur die drei waehlbaren Engines. `formats`
behaelt `.md` mit `passthrough`, und der Name steht weiterhin im Feld `engine`
eines Ergebnisses. Damit die beiden Listen nicht auseinanderlaufen, bietet
`OptionsPanel` nur noch an, was in `engines` steht -- sonst haette die Auswahl
`passthrough` gefuehrt, obwohl der Dienst dort nichts zur Wahl stellt. Mit einer
`.md` in der Warteschlange steht jetzt nur "automatisch" da. Tests:
`test_capabilities_lists_only_ready_engines` (angepasst) und "bietet nicht an,
was in engines gar nicht steht".

**Schnittstellen-Dreiklang beruehrt.** `contracts/api.md`, `models.py` und
`types.ts` im selben Commit: Der Vertrag beschreibt jetzt, dass `engines` nur
die waehlbaren Engines nennt und `passthrough` als Wert von `engine` auftritt;
die beiden Typdateien halten dasselbe im Kommentar fest. Strukturell aendert
sich nichts -- `engines` war schon `dict[str, EngineState]`.

### Fuer sophie, BE-10 (#32)

An `meta.py` geaendert: (a) `_state()` fragt `state()` ab, wo eine Engine sie
anbietet; (b) `engines` zaehlt nur noch `registry.ENGINE_NAMES`, ohne
`passthrough`. Beide Befunde sind damit erledigt. `registry.py`, `main.py` und
die Engineadapter blieben unberuehrt.

### Pruefung, tatsaechliche Ausgabe

Backend `uvicorn app.main:app --port 8000`, Frontend `npm run dev` auf :5173,
der Browser ueber Playwright/Chrome auf `http://localhost:5173/`. Fuenf
gemischte Dateien, darunter eine, die wirklich scheitert (`kaputt.odt` -- nur
Pandoc liest `.odt`, es gibt also keinen Rueckfall):

```
--- Fortschritt ---
4 von 5 fertig - 1 fehlgeschlagen
--- Zeilen ---
notizen.md    fertig  passthrough - 0 ms
tabelle.csv   fertig  markitdown - 40 ms
bericht.html  fertig  markitdown - 59 ms
handbuch.docx fertig  markitdown - 290 ms
kaputt.odt    fehlgeschlagen
  Pandoc ist an kaputt.odt gescheitert: Could not unzip ODT: ...
--- Vorschau (gerendert) ---
<h1>Notizen</h1><p>Ein <strong>Absatz</strong>.</p>
--- Einzeldownload --- notizen.md
--- Archiv --- kaimarkit.zip
--- Ansagen ---
Alle Dateien sind fertig: 4 gelungen, 1 fehlgeschlagen.
kaimarkit.zip steht bereit.
```

```
$ unzip -l kaimarkit.zip
  notizen.md  tabelle.md  bericht.md  handbuch.md  _errors.txt
  5 files
$ unzip -p kaimarkit.zip _errors.txt
kaputt.odt: Pandoc ist an kaputt.odt gescheitert: Could not unzip ODT: ...
```

- `pytest -q`: `105 passed, 3 deselected` (99 vor dem Ticket, dazu drei neue und
  drei aus zwischenzeitlich gemergtem `main`).
- `ruff check .`: `All checks passed!`
- `npm run test`: `Test Files 8 passed (8)`, `Tests 79 passed (79)` -- 75 vorher,
  4 neu.
- `npm run typecheck`: ohne Befund.
- `npm run build`: `built in 1.78s`, `318.82 kB`. Der Sprung von 64 kB kommt von
  `jszip`, das nun tatsaechlich importiert wird.

`main` war unter dem Ticket weitergezogen; `main` wurde in den Branch gemergt und
die ganze Pruefung danach erneut gefahren.

### Offen, nicht in diesem Ticket

- **Zwei Absaetze fuer akar** (aus FE-7 uebernommen und weiterhin unerledigt):
  Der Dark Mode und die Bedingung an die Farbpalette gehoeren nach
  `docs/entwicklung.md`. Wer dort eine Farbklasse ergaenzt, muss vorher
  `frontend/src/style.css` lesen -- jede Stufe dient nur einer Sache,
  `slate-800` ist die einzige Ausnahme.
- **Kein Favicon.** `frontend/index.html` nennt keines, der Browser fragt
  `/favicon.ico` und bekommt 404. Kosmetisch, keine Abweichung vom Vertrag.
- **Docling ungeprueft.** Die Bibliothek ist in der Entwicklungsumgebung nicht
  installiert; `markitdown` wurde dafuer nachinstalliert. Der Weg durch Docling
  bleibt INT-2 (#30) im Container vorbehalten.
