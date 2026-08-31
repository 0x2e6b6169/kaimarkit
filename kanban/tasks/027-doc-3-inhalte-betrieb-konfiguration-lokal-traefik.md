---
id: 27
title: 'DOC-3 · Inhalte Betrieb: Konfiguration, lokal, Traefik, Authelia'
status: todo
priority: medium
created: 2026-08-31T10:21:42.015369338+02:00
updated: 2026-08-31T10:30:46.284292816+02:00
assignee: akar
tags:
    - docs
depends_on:
    - 20
    - 25
class: standard
---

## Ziel

Der Betriebsteil der Dokumentation. Sie ist die einzige Quelle dafuer - es gibt
kein zweites README daneben.

## Eigene Dateien

- `docs/betrieb/konfiguration.md`
- `docs/betrieb/lokal.md`
- `docs/betrieb/traefik.md`
- `docs/betrieb/authelia.md`

## Vorgaben

- `konfiguration.md` listet jede Variable aus `docker/.env.example` mit
  Standardwert und Wirkung. **Beide Dateien werden gemeinsam geaendert** - wer eine
  Variable ergaenzt, umbenennt oder streicht, fasst beide an.
- `lokal.md`: der kuerzeste Weg zum laufenden Dienst.
- `traefik.md`: die Label-Mechanik, der externe Netzname aus `.env`, die
  Compose-Anforderung fuer `!reset` (2.24 oder neuer) und der Ausweichweg, falls
  sie fehlt.
- `authelia.md`: die ForwardAuth-Middleware und - wichtig - wie die API hinter
  Authelia erreichbar bleibt. Hier gehoert das Ergebnis der Pruefung aus IN-4 hin,
  ob Traefik ein leeres `middlewares`-Label als "keine Middleware" akzeptiert.
- Jede Betriebsvariante mit einem vollstaendigen, kopierbaren Aufruf.

## Pruefung

Jemand richtet den Dienst allein nach `docs/betrieb/` hinter Traefik ein, ohne den
Plan oder die Compose-Dateien zu lesen. `mkdocs build --strict` ohne Warnung.
