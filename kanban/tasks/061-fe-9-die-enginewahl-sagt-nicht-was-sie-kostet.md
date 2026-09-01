---
id: 61
title: FE-9 · Die Enginewahl sagt nicht, was sie kostet
status: done
priority: high
created: 2026-09-01T12:03:27.128646032+02:00
updated: 2026-09-01T12:10:54.04520561+02:00
assignee: benny
tags:
    - frontend
    - ux
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


## Ergebnis (benny-10)

Der Hinweis steht offen unter der Auswahl in `EngineSelect.vue` — je ein Satz zu
docling und zu markitdown, kein Tooltip, damit man ihn ohne Maus liest. Er haengt
per `aria-describedby" am Auswahlfeld, ein Screenreader liest ihn beim Anspringen
mit.

- docling: liest gruendlich und braucht dafuer oft Minuten je Dokument; bei
  gescannten Seiten ohne Textebene fuehrt kein Weg daran vorbei.
- markitdown: ist nach Sekundenbruchteilen fertig, verliert dabei aber
  gelegentlich eine Tabelle oder das Layout.

pandoc bekommt keinen Satz: Es liest Formate, die sonst niemand liest, und stellt
damit keine Wahl zwischen schnell und gruendlich. Faellt eine der beiden Engines
aus der Auswahl, verschwindet ihr Satz mit ihr. `OptionsPanel.vue` richtet nur die
Zeile neu aus (`items-start`/`items-baseline`), weil das Feld jetzt hoeher ist.
`engine=auto` bleibt Voreinstellung, am Backend aendert sich nichts.

86 Tests gruen, typecheck gruen. Gegenprobe gelaufen: ohne die Aenderung fallen
5 der neuen Tests durch.
