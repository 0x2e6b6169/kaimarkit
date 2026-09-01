---
id: 61
title: FE-9 · Die Enginewahl sagt nicht, was sie kostet
status: in-progress
priority: high
created: 2026-09-01T12:03:27.128646032+02:00
updated: 2026-09-01T12:05:05.981598039+02:00
assignee: benny
tags:
    - frontend
    - ux
claimed_by: benny-10
claimed_at: 2026-09-01T12:05:05.981598039+02:00
class: standard
---

## Ziel

Wer eine Engine waehlt, soll wissen, worauf er sich einlaesst. Heute steht dort
`automatisch, markitdown, docling, pandoc` ohne ein Wort dazu, was die Wahl bedeutet.

## Befund (01.09.2026, aus der Abnahme des Nutzers)

Gemessen an echten Dokumenten auf diesem Rechner:

| Datei | Engine | Dauer | Ergebnis |
|---|---|---|---|
| Bahnrechnung, 1 Seite | docling | 103,5 s | beide Tabellen vollstaendig |
| Anmeldung | docling | 326,1 s | vollstaendig, 3 Platzhalter mit Warnung |
| PDF mit breiter Tabelle | docling | 17,3 s | Tabelle als `<!-- image -->` verloren |
| dasselbe PDF | markitdown | 0,035 s | Tabelle vollstaendig |

Der Unterschied liegt bei einem Faktor von mehreren hundert bis mehreren tausend —
und das schnellere Ergebnis ist nicht durchweg das schlechtere. Das erste Dokument
des Nutzers lief in eine Zeitgrenze, ohne dass ihm vorher jemand gesagt haette, dass
Minuten zu erwarten sind.

## Die Entscheidung dahinter

Der Nutzer hat entschieden: **Die Wahl bleibt beim Menschen, mit einer Empfehlung
daneben.** Nicht die Voreinstellung umdrehen, nicht heimlich waehlen. `engine=auto`
bleibt, wie es ist; die Oberflaeche sagt dazu, was die Alternativen bedeuten.

## Eigene Dateien

- `frontend/src/components/EngineSelect.vue`
- `frontend/src/components/OptionsPanel.vue`
- die zugehoerigen Tests unter `frontend/src/components/__tests__/`

Nicht `types.ts` und nicht das Backend: Dieses Ticket kommt ohne neue Felder in
`/api/capabilities` aus. Braucht es doch eines, ist das der
Schnittstellen-Dreiklang — melden, nicht nebenbei einbauen.

## Vorgaben

Zwei Saetze in der Sprache des Nutzers, keine Tabelle mit Millisekunden. Der Kern:
**docling liest gruendlich und braucht dafuer Minuten; markitdown liest sofort und
kann Layout verlieren; bei gescannten Seiten ohne Textebene fuehrt kein Weg an
docling vorbei.**

Wo genau der Hinweis steht — unter der Auswahl, als Beschriftung je Eintrag, beim
Umschalten — entscheidet die Lane. Er darf nicht bevormunden und muss ohne Maus
erreichbar sein; die Barrierefreiheit aus FE-7 gilt weiter.

## Pruefung

- Die Auswahl nennt fuer docling und markitdown je einen Hinweis, der Dauer und
  Vollstaendigkeit gegeneinanderstellt.
- Der Hinweis ist mit der Tastatur erreichbar und fuer Screenreader angebunden.
- `npm run test` und `npm run typecheck` bleiben gruen.
- Gegenprobe: Ohne die Aenderung faellt der neue Test durch.
