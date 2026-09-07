---
id: 137
title: BE-41 · ocr_available meldet die Voreinstellung, nicht die Verfuegbarkeit
status: backlog
priority: high
created: 2026-09-07T12:08:28.338382941+02:00
updated: 2026-09-07T12:08:28.338382941+02:00
assignee: sophie
tags:
    - backend
class: standard
---

## Befund (2026-09-07, gemeldet von akar-45 beim Abschluss von DOC-26)

`backend/app/api/meta.py:52` setzt `ocr_available` aus `settings.ocr_enabled` — der
**Voreinstellung**, nicht daraus, ob der Dienst Texterkennung überhaupt anbietet. Das
Frontend blendet den OCR-Schalter genau an diesem Feld aus (`useCapabilities.ts:77`).

Folge: Ein Dienst, dessen `KAIMARKIT_OCR_ENABLED` auf `false` steht, versteckt den
Schalter vollständig — obwohl das Feld `ocr` im Aufruf die Voreinstellung ausdrücklich
je Anfrage überschreiben kann (`contracts/api.md`). Wer Texterkennung nur gelegentlich
braucht und sie deshalb nicht als Voreinstellung führt, kann sie über die Oberfläche
nie einschalten, obwohl der Dienst sie liefern könnte.

DOC-26 dokumentiert jetzt: "Rührt ihn niemand an, gilt die Voreinstellung des
Dienstes." Dieser Satz kann den Fall "Voreinstellung aus" nie meinen, solange
`ocr_available` daran hängt — die Doku und das Verhalten laufen auseinander.

## Eigene Dateien

- `backend/app/api/meta.py`
- `backend/tests/`, der Test zu `/api/capabilities`

Nicht hier: `contracts/api.md`, `backend/app/models.py`, `frontend/src/types.ts` —
der Feldname `ocr_available` und seine Bedeutung ("bietet der Dienst Texterkennung
an") bleiben unverändert. Es ändert sich nur, woraus der Wert berechnet wird.

## Vorgaben

`ocr_available` meldet, ob Docling (die einzige Engine mit Texterkennung) installiert
ist — unabhängig von `KAIMARKIT_OCR_ENABLED`. Ob `warming` dabei schon als verfügbar
zählt oder nicht, entscheidet die Lane; `unavailable` zählt in jedem Fall nicht.

## Prüfung

- Rot vor grün: ein Test mit `ocr_enabled=False` und installiertem Docling erwartet
  `ocr_available: true` in `/api/capabilities` — fällt vor der Arbeit durch.
- `pytest -q -rs` und `ruff check .` sauber; Sammelzahl und Abgewählte gemeldet.
