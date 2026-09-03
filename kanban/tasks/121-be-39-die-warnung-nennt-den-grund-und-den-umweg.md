---
id: 121
title: 'BE-39 · Die Warnung nennt den Grund und den Umweg (GitHub #2)'
status: todo
priority: high
created: 2026-09-03T15:13:02.423738476+02:00
updated: 2026-09-03T15:13:02.423738476+02:00
assignee: sophie
tags:
    - backend
    - gh-2
class: standard
---

## Ziel

Das ist der eigentliche Punkt aus GitHub-Issue #2. Der Nutzer hat eine Warnung gesehen
und wurde daraus nicht klüger — auf die Frage „stand ein Warnhinweis da?" hat er
geantwortet: „Ja, eine Warnung stand da." Gefehlt hat ihm nicht die Warnung, sondern
ihr **Grund**.

Aus BE-38 (#117) liegt der gemessene Wortlaut vor, den MarkItDown bei PDF setzt:

    MarkItDown übernimmt keine Bilder aus PDF. Enthielt bild_im_dokument.pdf Bilder,
    fehlt ihr Inhalt hier.

Der Satz sagt, was fehlt. Er sagt nicht, was der Nutzer tun kann. Und für den gemessenen
Hauptfall — ein Bild in einem docx — gibt es überhaupt keine Warnung; den behandelt
BE-40.

## Eigene Dateien

- `backend/app/converters/docling.py` und der Test dazu
- die Datei, in der die Warnungstexte der Engines stehen, **falls es eine gemeinsame
  gibt** — erst nachsehen, nicht raten. Steht der Wortlaut in mehreren Engine-Modulen,
  gehören sie alle dazu, `markitdown.py` ausgenommen.

`backend/app/converters/markitdown.py` gehört BE-40 (#122). Kollidieren die beiden an
einer gemeinsamen Datei, geht dieses Ticket zuerst; BE-40 hängt daran.

Nicht hier: `docs/formate.md` und `docs/grenzen.md` — die gehören DOC-18 (#123).

## Vorgaben

- Eine Warnung über ausgelassene Bilder nennt drei Dinge: **was** ausgelassen wurde,
  **warum** (die Engine kann es an dieser Stelle nicht), und **was der Nutzer tun kann**.
  Der Umweg ist gemessen: bei PDF hilft Docling mit OCR, bei docx hilft, das Dokument
  als PDF abzugeben.
- Deutsch, ein Satz je Sache, keine Fachbegriffe aus der Bibliothek. Der Leser ist
  jemand, der ein Dokument hochgeladen hat, kein Entwickler.
- Der Dateiname bleibt in der Meldung; er unterscheidet die Zeilen bei einem Stapel.
- Konvention 3 bleibt unberührt: Das sind Warnungen, keine `ConversionError`.

## Prüfung

- Rot vor grün: Ein Test, der die Warnung eines Laufs mit ausgelassenen Bildern auf den
  Umweg hin prüft, fällt vor der Arbeit durch.
- Der neue Wortlaut steht **wörtlich** in der Ticketnotiz, in richtiger Schreibung mit
  Umlauten, damit er im Issue-Kommentar zitiert werden kann.
- `pytest -q -rs` und `ruff check .` sauber; Sammelzahl und Abgewählte gemeldet.
- Wo die Warnung nur im Abbild entsteht: `make test-slow-image`, nicht die pyenv-Umgebung.
