---
id: 109
title: 'DOC-15 · Doku der URL-Konvertierung: API, Oberfläche, Grenzen (GitHub #5)'
status: in-progress
priority: medium
created: 2026-09-03T11:20:27.8373002+02:00
updated: 2026-09-03T14:31:37.188854458+02:00
assignee: akar
tags:
    - docs
    - gh-5
depends_on:
    - 107
    - 108
claimed_by: akar-38
claimed_at: 2026-09-03T14:31:37.188854458+02:00
class: standard
---

## Ziel

GitHub-Issue #5, dritter Teil: Die Doku beschreibt die URL-Konvertierung so, wie BE-35 und FE-21 sie gebaut haben: für den API-Nutzer, den Bediener und den Betreiber.

## Eigene Dateien (je Abschnitt)

- `docs/api.md`: neuer Abschnitt „Eine Webseite wandeln — `POST /api/convert/url`" nach dem Batch-Abschnitt, mit `curl`-Beispiel und den Fehlercodes
- `docs/schnellstart.md` (Abschnitt „Über die Oberfläche"): das Textfeld, eine Adresse je Zeile
- `docs/grenzen.md`: neuer Abschnitt „Webseiten: nur öffentlich, kein JavaScript" (Adressprüfung, Größenlimit, `KAIMARKIT_URL_TIMEOUT`, Redirects, Seiten hinter Anmeldung, dynamisch gerenderte Seiten). Den Abschnitt „Was der Dienst gar nicht tut" hat BE-35 schon berichtigt; hier nur lesen, ob er noch stimmt.
- `docs/formate.md` (Abschnitt „Die Matrix"): ein Satz, dass eine URL nach dem gelieferten Inhaltstyp in die Matrix fällt; `.html` steht schon drin
- `docs/index.md` (Abschnitt „Der Dienst legt nichts ab"), falls dort steht, der Dienst hole nichts aus dem Netz

Nicht hier: `docs/betrieb/konfiguration.md` und `docker/.env.example`. Die Variable hat BE-35 eingetragen.

## Vorgaben

- Quelle ist der Quelltext nach dem Merge von BE-35 und FE-21, nicht dieses Ticket: `backend/app/fetching.py` für die Regeln, `contracts/api.md` für die Schnittstelle. Wo beides auseinandergeht, gilt der Quelltext, und die Abweichung wird gemeldet.
- Das `curl`-Beispiel muss laufen: gegen einen lokal gestarteten Dienst mit `https://example.com/` ausprobieren, Antwort gekürzt übernehmen.
- Deutsche Prosa nach `SPRACHE.md`; keine Umschrift.

## Prüfung

1. Vorher rot: `grep -n 'convert/url' docs/api.md` findet nichts. Nachher findet es den Abschnitt.
2. `mkdocs build --strict` im Backend-venv läuft ohne Warnung durch.
3. Das `curl`-Beispiel aus `docs/api.md` liefert gegen `uvicorn app.main:app` die gezeigte Antwortform.
4. `grep -rn 'Nichts nachladen' docs/` findet keinen Satz mehr, der dem Endpunkt widerspricht.

[[2026-09-03]] Thu 14:19
Nachtrag von katche, vor dem Claim: In den Abschnitt "Die Matrix" gehoert neben dem
URL-Satz die Unterscheidung, die DOC-16 (#112) zutage gefoerdert hat. Eine Engine im
Zustand `warming` steht in `engines` von `GET /api/capabilities` und ist damit
ausdruecklich waehlbar - eine solche Anfrage wartet, bis das Modell geladen ist
(`converters/docling.py:226-229`). Aus `formats` faellt sie aber heraus, genau wie
`unavailable` (`converters/registry.py:161,199`): `engine=auto` nimmt fuer ein PDF
solange die naechste Engine der Liste. Beides in einem Satz, damit die Matrix nicht
den Eindruck erweckt, waehlbar und in `formats` sei dasselbe.
Der Vertrag braucht dazu nichts; er behauptet an keiner Stelle etwas ueber `formats`
und `warming` (geprueft).
