---
id: 63
title: FE-10 · Die Oberflaeche zeigt deutsche Texte in ASCII-Umschrift
status: done
priority: medium
created: 2026-09-01T12:12:54.471738305+02:00
updated: 2026-09-01T12:18:56.068700293+02:00
started: 2026-09-01T12:18:36.776301718+02:00
completed: 2026-09-01T12:18:36.776301718+02:00
assignee: benny
tags:
    - frontend
    - ux
class: standard
---

## Befund (01.09.2026, gemeldet von benny aus FE-9)

Keine einzige Datei unter `frontend/src` enthaelt einen Umlaut. Im Browser steht
deshalb "Dateien hierher ziehen oder auswaehlen", "Die Optionen gelten fuer den
naechsten Lauf" und seit gestern "docling liest gruendlich".

Belegt an den Bildschirmfotos des Nutzers aus der Abnahme — er hat den ganzen
Vormittag auf diese Texte gesehen.

    grep -rlP "[aeoeueAEOEUEss]" frontend/src   ->  0 Dateien

## Warum das ein Fehler ist und kein Stil

`CLAUDE.md` trennt beides sauber: Code, Bezeichner und Commit-Messages bleiben
englisch, deutsche Fliesstexte folgen `SPRACHE.md`. Eine Zeichenkette, die im Browser
steht, ist deutscher Fliesstext und kein Bezeichner.

Dass es keine technische Huerde gibt, zeigt `docs/`: Die Dokumentation benutzt
durchgehend Umlaute und rendert fehlerfrei.

benny-10 hat sich in FE-9 korrekt an den vorhandenen Stil gehalten. Der Fehler ist
aelter als das Ticket, deshalb gemeldet statt nebenbei geaendert.

## Eigene Dateien

Alle `.vue`-Dateien unter `frontend/src` und die Tests, die Texte pruefen.

**Dieses Ticket sperrt die ganze Lane, solange es laeuft.** Das ist beabsichtigt und
der Grund, es allein und zuegig zu fahren statt neben etwas anderem.

## Vorgaben

Nur **nutzersichtbare** Zeichenketten: Beschriftungen, Hinweise, Fehlermeldungen,
`aria-label` und `title`. Nicht Bezeichner, nicht Kommentare, nicht Testnamen — das
haelt die Aenderung klein und den Diff lesbar.

Von Hand pruefen, nicht ersetzen lassen: Ein blindes `ue` -> `ü` verunstaltet
`queue`, `value`, `neue`. Jede Stelle einzeln ansehen.

## Pruefung

- `grep -rlP "[äöüÄÖÜß]" frontend/src` findet die geaenderten Dateien.
- Kein Bezeichner und kein Import hat sich geaendert: `npm run typecheck` bleibt
  gruen, `npm run test` ebenso.
- Gegenprobe: Die Dropzone zeigt im Browser "auswählen", nicht "auswaehlen".


## Ergebnis (benny-11, Branch task/63-umlaute)

11 Dateien, 13 nutzersichtbare Zeichenketten: App.vue (2), FileDropZone.vue (3),
EngineSelect.vue (3, darunter der docling-Hinweis), OptionsPanel.vue (2),
FileQueue.vue (1), FileRow.vue (1), download.ts (1). Vier Testerwartungen ziehen
nach — App.test.ts, FileQueue.test.ts (zwei Stellen), FileRow.test.ts,
OptionsPanel.test.ts. Testnamen, Bezeichner und Kommentare blieben unberührt.

Bewusst ASCII geblieben ist nichts. Alle übrigen deutschen Zeichenketten in
`frontend/src` brauchen von sich aus keinen Umlaut: „Warteschlange", „Kopieren",
„fehlgeschlagen", „Der Dienst ist nicht erreichbar." Deshalb ändern sich
MarkdownPreview.vue, api.ts, useConversion.ts und useCapabilities.ts nicht.

Prüfung: `npm run typecheck` grün, `npm run test` 86 von 86 grün. Gegenprobe mit
headless Chrome gegen den Dev-Server: Die Dropzone zeigt jetzt „Dateien hierher
ziehen oder auswählen", daneben „alle unterstützten Formate", „Noch keine Dateien
ausgewählt." und „Die Optionen gelten für den nächsten Lauf". In `docs/` steht
keine dieser Zeichenketten; es wurde durch die Änderung nichts falsch.

## Befund, gemeldet statt geändert

Der Platzhalter im Slot `preview` von FileRow.vue sagt: „Die Vorschau folgt mit
FE-4. Bis dahin steht hier nur, dass N Zeichen Markdown vorliegen." FE-4 ist
gebaut, App.vue hängt `MarkdownPreview` ein. Der Satz verspricht dem Nutzer
etwas, das längst da ist — er stimmt nur noch dort, wo die Warteschlange ohne
Slot eingesetzt wird. Zwei Tests prüfen ihn (FileQueue.test.ts, FileRow.test.ts).
Gehört in ein eigenes Ticket.
