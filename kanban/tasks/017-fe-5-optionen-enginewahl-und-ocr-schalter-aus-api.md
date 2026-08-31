---
id: 17
title: 'FE-5 · Optionen: Enginewahl und OCR-Schalter aus /api/capabilities'
status: todo
priority: medium
created: 2026-08-31T10:20:21.574451025+02:00
updated: 2026-08-31T10:30:45.658367404+02:00
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
