---
id: 109
title: 'DOC-15 · Doku der URL-Konvertierung: API, Oberfläche, Grenzen (GitHub #5)'
status: done
priority: medium
created: 2026-09-03T11:20:27.8373002+02:00
updated: 2026-09-03T14:40:56.550578607+02:00
started: 2026-09-03T14:40:23.665694797+02:00
completed: 2026-09-03T14:40:23.665694797+02:00
assignee: akar
tags:
    - docs
    - gh-5
depends_on:
    - 107
    - 108
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


[[2026-09-03]] Thu — akar-38

Merge d4829e1 (Branch task/109-url-conversion-docs, Commit bf29ee3).

Geändert: `docs/api.md` (neuer Abschnitt „Eine Webseite wandeln — `POST /api/convert/url`" vor „Die Schnittstelle maschinenlesbar": Feldtabelle, curl-Beispiel, abgeleiteter Dateiname, vollständige Fehlertabelle, `invalid_url`-Beispiel); `docs/grenzen.md` (neuer Abschnitt „Webseiten: nur öffentlich, kein JavaScript" vor „Was der Dienst gar nicht tut"); `docs/schnellstart.md` (Abschnitt „Über die Oberfläche", ein Absatz zum Textfeld); `docs/formate.md` (Abschnitt „Die Matrix"); `docs/index.md`.

curl-Läufe gegen `uvicorn app.main:app --port 8123` im Worktree — nicht 8000 oder 8080, uvicorn danach beendet, Port wieder frei:

- `POST /api/convert/url` mit `{"url": "https://example.com/"}` → **HTTP 200**, `filename` `example-domain.html`, `engine` `markitdown`, `warnings` leer, `duration_ms` 10 (kalt 3668). Genau die Antwortform, die jetzt in `api.md` steht.
- Nachtrag von katche, alle drei Punkte selbst geprüft und bestätigt:
  1. Der Name kommt aus dem `<title>`: example.com trägt den Titel „Example Domain" → `example-domain.html`, nicht `example-com.html`. Steht jetzt konkret in `schnellstart.md`.
  2. Eine PDF-Adresse kommt durch: `https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf` → HTTP 200, `engine` `markitdown`, Warnung „MarkItDown übernimmt keine Bilder aus PDF. …". Zweiter Beleg `https://arxiv.org/pdf/2502.16161` → HTTP 200, `filename` `arxiv-org-pdf-2502-16161.pdf`. Steht jetzt in der Matrix.
  3. `http://127.0.0.1/` → **HTTP 400**, `code` `invalid_url`, `detail` „127.0.0.1 zeigt auf 127.0.0.1, und das ist keine öffentliche Adresse." Zusätzlich geprüft: `http://localhost:8000/api/health` → ebenfalls 400 `invalid_url` („localhost zeigt auf 127.0.0.1, …"); der Name schützt also nicht davor. Beides steht in `api.md` und `grenzen.md`.

Prüfung: (1) vorher rot — `grep -n 'convert/url' docs/api.md` lieferte nichts, Rückgabewert 1; nachher drei Treffer. (2) `mkdocs build --strict` im venv `claude-code`: Rückgabewert 0, keine Warnung; der rote Kasten im Protokoll ist der Material-Hinweis auf MkDocs 2.0, keine Baumeldung. (3) curl wie oben, HTTP 200. (4) `grep -rn 'Nichts nachladen' docs/` findet nur `grenzen.md:138`, und der Satz nennt `/api/convert/url` bereits richtig — BE-35 hatte ihn berichtigt.

Keine Abweichung zwischen `contracts/api.md` und Quelltext gefunden: Feldnamen, Standardwert `engine=auto`, Fehlercodes, Namensableitung und die Grenze von fünf Weiterleitungen stimmen mit `fetching.py`, `models.py` und `api/convert.py` überein. Geschrieben ist die Doku trotzdem aus dem Quelltext.

Drei Befunde außerhalb der eigenen Abschnitte:

- `docs/index.md` führte „die vier Endpunkte". Seit BE-35 sind es fünf. Kein offenes Ticket besitzt die Datei, deshalb habe ich das eine Wort im selben Merge berichtigt.
- `docs/schnellstart.md`, Abschnitt „Was vorher da sein muss", Zeile 12: „dafür holt der Dienst zur Laufzeit nichts mehr aus dem Netz". Gemeint sind die Docling-Modelle; seit `/api/convert/url` liest sich der Satz zu absolut. Nicht geändert, fremder Abschnitt — bitte als Ticket aufnehmen.
- `docs/grenzen.md`, Abschnitt „Vier Werte begrenzen einen Aufruf": `KAIMARKIT_URL_TIMEOUT` ist ein fünfter Wert und fehlt in der Tabelle. Der neue Abschnitt nennt ihn samt Standard von 30 Sekunden; die Überschrift habe ich stehen lassen, weil die Tabelle die Grenzen einer Umwandlung meint. Soll sie umgestellt werden, ist das ein eigenes Ticket.
