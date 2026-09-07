---
id: 137
title: BE-41 · ocr_available meldet die Voreinstellung, nicht die Verfuegbarkeit
status: done
priority: high
created: 2026-09-07T12:08:28.338382941+02:00
updated: 2026-09-07T12:42:18.109923754+02:00
started: 2026-09-07T12:37:42.669814174+02:00
completed: 2026-09-07T12:42:17.501052673+02:00
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


## Erledigt (sophie-45, 2026-09-07)

`ocr_available` kommt jetzt aus dem Zustand von Docling, nicht aus
`settings.ocr_enabled`: `backend/app/api/meta.py` liest den Wert aus dem schon
berechneten `engines`-Wörterbuch und meldet `true`, solange Docling nicht
`unavailable` ist. Die Konstante `OCR_ENGINE = "docling"` benennt, woran das Feld
hängt.

**Entscheidung zu `warming`: zählt als verfügbar.** Wer Docling während des
Warmlaufs verlangt, wartet an dessen Sperre und bekommt ein richtiges Ergebnis,
nur später — der Dienst bietet die Texterkennung also an. Ein Schalter, der eine
halbe Minute lang verschwindet und danach wiederkommt, wäre für den Leser der
Oberfläche schlechter als einer, der von Anfang an steht. Die Begründung steht als
Kommentar an der Berechnung.

Der Schnittstellen-Dreiklang blieb unberührt: Feldname und Bedeutung ändern sich
nicht, nur die Berechnung. `contracts/api.md`, `models.py` und `types.ts` nicht
angefasst.

**Doku**: Der von DOC-26 genannte Satz in `docs/nutzer/engine-und-texterkennung.md`
— „Rührt ihn niemand an, gilt die Voreinstellung des Dienstes." — stimmt nach der
Änderung, denn der Schalter steht nun auch bei ausgeschalteter Voreinstellung da.
Vorher konnte er den Fall nie meinen. Auch „In `ocr_available` steht, ob die
Oberfläche den Schalter zeigt." bleibt richtig. `docs/admin/api.md` sagt nichts
über `ocr_available`. Keine Berichtigung nötig.

**Prüfung.** Drei neue Tests in `backend/tests/test_api.py`, alle drei **vor** der
Arbeit rot (`3 failed, 217 deselected`):

- `test_ocr_available_ignores_the_default` — `ocr_enabled=False`, Docling `ready`
  → `ocr_available: true`.
- `test_ocr_available_while_docling_warms` — `ocr_enabled=False`, Docling
  `warming` → `ocr_available: true` (hält die Entscheidung fest).
- `test_ocr_available_is_false_without_docling` — Gegenfall: `ocr_enabled=True`,
  Docling meldet `unavailable` → `ocr_available: false`.

Aus `test_capabilities_reports_limits_from_settings` ist die Zusicherung auf
`ocr_available` herausgenommen; sie gehört nicht zu den Grenzen und wäre dort
zudem vom Zustand des Docling-Warmlaufs abhängig geworden.

`pytest -q -rs`: **220 gesammelt, 209 ausgewählt, 209 bestanden, 11 abgewählt**
(die slow-Tests über `addopts = -m "not slow"`), 0 übersprungen. `ruff check .`:
All checks passed.

Merge: `75673c2` (`--no-ff`), Zweig `task/137-ocr-available`.
