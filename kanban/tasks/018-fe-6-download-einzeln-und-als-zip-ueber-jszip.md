---
id: 18
title: FE-6 · Download einzeln und als ZIP ueber jszip
status: done
priority: medium
created: 2026-08-31T10:20:22.18026728+02:00
updated: 2026-08-31T11:22:03.646081021+02:00
started: 2026-08-31T11:22:01.598045827+02:00
completed: 2026-08-31T11:22:01.598045827+02:00
assignee: benny
tags:
    - frontend
depends_on:
    - 15
class: standard
---

## Ziel

Das Ergebnis herausbekommen.

## Eigene Dateien

- `frontend/src/download.ts`

## Vorgaben

- Einzeldownload je Zeile als `.md`.
- "Alles herunterladen" packt im Browser mit `jszip`. Der Grund: Die Ergebnisse
  liegen bereits im Browser; sie fuer das Archiv erneut zum Server zu schicken
  hiesse, jede Datei zweimal zu konvertieren.
- Fehlgeschlagene Dateien landen nicht im Archiv, sondern als Zeile in einer
  `_errors.txt` darin.
- Dateinamen im Archiv wie im Backend gesaeubert, Kollisionen durchnummeriert.

## Pruefung

Fuenf Dateien, davon eine fehlgeschlagen: Das Archiv enthaelt vier `.md`-Dateien
und eine `_errors.txt`, laesst sich mit `unzip` entpacken und die Namen stimmen.


---

## Notiz (benny-06)

Umgesetzt in `frontend/src/download.ts` samt `frontend/src/__tests__/download.spec.ts`.
Branch `task/18-download-zip`, gemergt als `merge: FE-6 single-file and ZIP download`.

### Exportflaeche (fuer FE-7 / INT-1, die die Knoepfe verdrahten)

```ts
import {
  downloadMarkdown, downloadArchive, buildArchive, hasResult,
  markdownFilename, sanitizeFilename, saveBlob,
  ARCHIVE_FILENAME, ERROR_FILENAME, UNKNOWN_ERROR,
  type DownloadEntry, type SaveFn,
} from './download'

interface DownloadEntry {
  filename: string
  status: 'queued' | 'running' | 'ok' | 'failed'
  markdown: string | null
  error: string | null
}
type SaveFn = (blob: Blob, filename: string) => void

downloadMarkdown(entry: DownloadEntry, save?: SaveFn): void
downloadArchive(entries: readonly DownloadEntry[], filename?: string, save?: SaveFn): Promise<void>
buildArchive(entries: readonly DownloadEntry[]): Promise<Blob>
hasResult(entry: DownloadEntry): boolean
markdownFilename(filename: string | null | undefined): string
sanitizeFilename(name: string | null | undefined): string
saveBlob(blob: Blob, filename: string): void
```

`QueueEntry` aus `composables/useConversion` erfuellt `DownloadEntry` strukturell;
ein Eintrag aus der Warteschlange laesst sich ohne Umbau uebergeben. Der Parameter
`save` ist nur fuer Tests da, die Oberflaeche ruft ohne ihn auf.

Zwei Hinweise fuer die Verdrahtung:

- `downloadMarkdown` wirft, wenn der Eintrag kein Ergebnis hat. Den Knopf je Zeile
  an `hasResult(entry)` haengen, "Alles herunterladen" an `!busy`.
- `ARCHIVE_FILENAME` ist `kaimarkit.zip`.

### Entscheidungen

- Die Regeln aus `backend/app/packaging.py` sind nachgebaut, damit ein im Browser
  gebautes Archiv aussieht wie eines vom Dienst: kein Pfadanteil, keine
  Steuerzeichen, Rueckfall `upload`, von vorn auf 255 Zeichen gekuerzt, `.md`
  statt der Eingabeendung, Kollisionen als `-2`, `-3`, gescheiterte Dateien als je
  eine Zeile in `_errors.txt` statt im Archiv.
- Wartende und laufende Eintraege kommen weder ins Archiv noch in `_errors.txt`:
  Eine Datei, die noch konvertiert wird, ist nicht gescheitert.
- Das Paket entsteht ueber `generateAsync({ type: 'arraybuffer' })` und wird selbst
  in einen `Blob` gewickelt. Direkt nach `blob` zu erzeugen haengt an JSZips
  Erkennung der Blob-Unterstuetzung und liesse sich im Test ohne Browser nicht lesen.

### Pruefung, tatsaechliche Ausgabe

- `npm run test`: `Test Files 7 passed (7)`, `Tests 71 passed (71)` — 43 vorher, 28 neu.
- `npm run typecheck`: ohne Befund.
- `npm run build`: `built in 439ms`.

Die Pruefung aus dem Ticketrumpf zusaetzlich mit echtem `unzip` gefahren: fuenf
Eintraege, davon einer gescheitert und zwei mit demselben Stamm.

```
$ unzip -l ergebnis.zip
  bericht.md  handbuch.md  notizen.md  bericht-2.md  _errors.txt
  5 files
$ cat _errors.txt
roman.epub: pandoc: beschaedigtes Archiv
```

`../../etc/notizen.md` liegt als `notizen.md` im Archiv, der Pfadanteil ist weg.

### Luecken

- **Kein Aufrufer.** `download.ts` steht allein; die Knoepfe gehoeren zu FE-7 (#19)
  und werden dort oder in INT-1 (#29) verdrahtet. Solange niemand importiert, landet
  `jszip` auch nicht im Bundle — der Build zeigt deshalb noch 64 kB.
- **Doku.** `docs/entwicklung.md` fehlt weiterhin (DOC-1/DOC-2, akar). Der Download
  ist im Kopfkommentar von `download.ts` beschrieben; sobald die Seite existiert,
  gehoert dorthin ein Absatz: Das Archiv entsteht im Browser, nicht ueber
  `/api/convert/batch`, und die Namensregeln sind die des Backends.
- **Schnittstellen-Dreiklang unberuehrt.** Weder `contracts/api.md` noch
  `backend/app/models.py` noch `frontend/src/types.ts` geaendert.
