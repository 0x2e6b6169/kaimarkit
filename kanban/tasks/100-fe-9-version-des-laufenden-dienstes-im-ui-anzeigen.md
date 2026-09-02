---
id: 100
title: FE-9 · Version des laufenden Dienstes im UI anzeigen
status: todo
priority: high
created: 2026-09-02T16:38:53.891700471+02:00
updated: 2026-09-02T16:38:53.891700471+02:00
assignee: benny
class: standard
---

## Ziel

Die Oberfläche zeigt, welchen Stand der Dienst fährt. Der Wert steht schon
bereit: `GET /api/health` liefert `{ "status": "ok", "version": "…" }`, und
`HealthResponse` steht seit jeher in `types.ts` — aufgerufen hat den Endpunkt
im Frontend noch nie jemand.

## Eigene Dateien

- `frontend/src/api.ts`
- `frontend/src/App.vue`
- `frontend/src/App.test.ts`

`types.ts` bleibt unverändert: `HealthResponse` ist bereits richtig. Muss es
doch angefasst werden, ist das der Schnittstellen-Dreiklang und gehört gemeldet.

## Vorgaben

**Nichts am Vertrag ändern.** `/api/health` existiert, die Form steht in
`contracts/api.md`. Dieses Ticket ruft nur ab.

**Die Form des Werts ist nicht Sache des Frontends.** Heute kommt `0.1.0`,
nach BE-33 (#98) und IN-19 (#99) etwas wie `v0.1.0-12-ga22a6c5`. Die Anzeige
gibt aus, was kommt — **kein Zurechtschneiden, kein Abschneiden des Hashs, kein
vorangestelltes `v`**, wenn keines kam. Der Wert ist eine undurchsichtige
Zeichenkette.

**Der Ausfall ist stumm.** Antwortet `/api/health` nicht oder fehlt das Feld,
erscheint gar nichts — keine Fehlermeldung, kein Platzhalter, kein „unbekannt".
Anders als bei `/api/capabilities` hängt nichts daran: Wer nicht weiß, welche
Version läuft, kann trotzdem umwandeln. Ein Fehlerbanner für eine Fußnote wäre
aus dem Verhältnis.

**Platz: unten, nicht oben.** Der Kopf hat mit Überschrift, Beschreibung und
dem GitHub-Verweis aus FE-8 genug. Die Version gehört als unaufdringliche
Fußzeile unter den Inhalt, kleiner und in gedämpfter Farbe. Naheliegend ist,
sie neben den GitHub-Verweis zu stellen — **nicht tun**: Der Verweis steht
oben und bleibt dort.

**Der Abruf läuft einmal beim Laden** und wird nicht wiederholt. Er darf
nichts blockieren; die Dropzone ist bedienbar, bevor die Antwort da ist.

## Prüfung

1. Neuer Test in `App.test.ts`: Bei einer Attrappe, die
   `{ status: 'ok', version: 'v0.1.0-12-ga22a6c5' }` liefert, steht genau diese
   Zeichenkette im gerenderten Baum. Vor der Änderung rot — belegen.
2. Zweiter Test: Schlägt der Abruf fehl, erscheint nichts, und die übrigen
   Zusicherungen der Datei bleiben grün. Kein Fehlerbanner, kein Platzhaltertext.
3. `npm run test` — Datei- **und** Testzahl beider Zeilen nennen.
4. `npm run typecheck`
5. `npm run build`
