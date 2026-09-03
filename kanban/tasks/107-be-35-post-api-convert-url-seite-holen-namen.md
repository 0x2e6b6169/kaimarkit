---
id: 107
title: 'BE-35 · POST /api/convert/url: Seite holen, Namen ableiten, nur öffentliche Adressen (GitHub #5)'
status: in-progress
priority: medium
created: 2026-09-03T11:20:26.703137724+02:00
updated: 2026-09-03T11:27:30.505363665+02:00
assignee: sophie
tags:
    - backend
    - gh-5
claimed_by: sophie-36
claimed_at: 2026-09-03T11:27:30.505363665+02:00
class: standard
---

## Ziel

GitHub-Issue #5, erster Teil: Der Dienst holt eine Seite aus dem Netz und wandelt sie wie eine hochgeladene Datei. Neuer Endpunkt `POST /api/convert/url`, ein Aufruf je URL. Das Frontend (FE-21) ruft ihn je Zeile auf, wie es `/api/convert` je Datei aufruft. Der Dateiname kommt aus dem `<title>` der Seite.

## Entscheidungen des Nutzers

- **Nur öffentliches http(s).** Loopback, private Netze (10/8, 172.16/12, 192.168/16, fc00::/7), Link-local (169.254/16, fe80::/10) und alles, was `ipaddress.ip_address(...).is_global` verneint, werden abgewiesen, auch wenn erst ein Redirect dorthin führt. Der Dienst steht auf dem VPS im selben Docker-Netz wie Traefik und Authelia; ohne diese Sperre wäre er ein Sprungbrett dorthin.
- **Dateiname aus dem Titel.** `<title>` → Kleinbuchstaben, Umlaute umgeschrieben (ä→ae, ö→oe, ü→ue, ß→ss), alles außer `[a-z0-9]` zu `-`, Mehrfach-Bindestriche zusammengezogen, Ränder beschnitten, auf 80 Zeichen gekürzt. Ohne Titel: Host und Pfad auf dieselbe Art. Nummerieren bei gleichem Namen tut der Client (das Frontend hängt `-2`, `-3` an, siehe `download.ts`); der Endpunkt liefert nur den Namen.

## Schnittstelle

Anfrage als JSON: `{ "url": "https://…", "engine": "auto" | "<name>", "ocr": true | false | null }`. `engine` und `ocr` wie bei `/api/convert`, gleiche Bedeutung, gleiche Vorgaben.

Antwort: ein `ConversionEntry`, unverändert. `filename` ist der abgeleitete Name **mit der Endung der geholten Datei**: `example-domain.html`, bei einer PDF-URL `paper.pdf`. Das Frontend macht daraus `.md`, wie bei Uploads.

Fehler: 400 `invalid_url` (kein http/https, nicht auflösbar, nicht öffentlich, Redirect ins Private, mehr als 5 Redirects); 413, wenn die Antwort `KAIMARKIT_MAX_FILE_SIZE_MB` überschreitet (beim Streamen abbrechen, nicht erst danach messen); 415, wenn der Inhaltstyp auf keine bekannte Endung führt; 504 wie bei `/api/convert`. Alles als `ErrorResponse`. Ob `invalid_url` ein neuer `ErrorCode` wird oder ein bestehender passt, entscheidet der Blick in `errors.py`; ein neuer Code wandert durch den Dreiklang.

Der Schnittstellen-Dreiklang (`contracts/api.md`, `backend/app/models.py`, `frontend/src/types.ts`) ändert sich in **einem** Commit; der neue Typ `UrlConvertRequest` steht in allen dreien. Vermerk in der Ticketnotiz, damit benny es sieht.

## Eigene Dateien

- `contracts/api.md`, `backend/app/models.py`, `frontend/src/types.ts` (Dreiklang)
- `backend/app/api/convert.py`
- `backend/app/fetching.py` (neu: holen, prüfen, Namen ableiten)
- `backend/app/config.py`: `url_timeout: int = 30` (`KAIMARKIT_URL_TIMEOUT`, Sekunden je Abruf)
- `backend/app/errors.py`, nur falls ein neuer Code nötig ist
- `backend/pyproject.toml`: `httpx` wird Laufzeitabhängigkeit (steht heute nur unter `dev`)
- `backend/tests/test_fetching.py` (neu), `backend/tests/test_api.py`
- `docker/.env.example` und `docs/betrieb/konfiguration.md` (Abschnitt „Anwendung"): die neue Variable, gemeinsam (Konvention 6)
- `docs/grenzen.md` (Abschnitt „Was der Dienst gar nicht tut"): Der Punkt „Nichts nachladen" wird nach dem Merge falsch und wird berichtigt. Zur Laufzeit holt der Dienst nur, was ein Aufruf von `/api/convert/url` verlangt, nie Modelle. Alle übrige Doku gehört DOC-15.

## Vorgaben

- Der Abruf läuft unter demselben Semaphor wie Uploads (`uploads.py` zeigt, wie). Zeitgrenze je Abruf `KAIMARKIT_URL_TIMEOUT`; die Konvertierung danach unterliegt `KAIMARKIT_CONVERSION_TIMEOUT` wie bisher.
- Redirects von Hand folgen (`follow_redirects=False`), jeden Zielhost vor dem nächsten Sprung prüfen. Die Prüfung löst den Hostnamen auf und prüft **jede** zurückgegebene Adresse; ein Name, der auf eine öffentliche und eine private Adresse zeigt, wird abgewiesen.
- Die Antwort landet als Datei im `TemporaryDirectory` (Konvention 5), Endung aus `Content-Type` (`text/html` → `.html`, `application/pdf` → `.pdf`, sonst aus dem Pfad; nichts erkennbar → 415). Danach derselbe Weg wie ein Upload: Registry, Engine, Fallback. Kein zweiter Konvertierungspfad.
- Kein JavaScript-Rendering. Was der Server als HTML liefert, ist die Seite.
- `User-Agent`: `kaimarkit/<version>` aus `Settings.service_version`.
- Konvention 3: `httpx`-Fehler werden zu `ConversionError` oder zur passenden HTTP-Antwort; kein `httpx.ConnectError` erreicht die API.
- Konvention 4: Der Timeout kommt aus der Umgebung. Die Redirect-Grenze 5 und die Slug-Länge 80 sind keine Betriebsgrößen und bleiben Konstanten.
- Die Tests für den Netzteil laufen ohne Netz: `httpx.MockTransport`; die Adressprüfung mit einer Attrappe für die Namensauflösung.

## Prüfung

1. Vorher rot: `curl -s -X POST -H 'content-type: application/json' -d '{"url":"https://example.com/"}' localhost:8000/api/convert/url` antwortet 404. Nachher 200, `filename` ist `example-domain.html`, `markdown` enthält „Example Domain".
2. Neue Tests, vorher rot, nachher grün: öffentliche URL mit `<title>` → Slug; ohne `<title>` → Host und Pfad; Umlaute im Titel; `http://127.0.0.1/`, `http://10.0.0.1/`, `http://169.254.169.254/`, `file:///etc/passwd` → 400; Redirect von öffentlich auf `http://192.168.1.1/` → 400; Antwort größer als das Limit → 413, und der Abbruch kommt vor dem Ende des Stroms; `application/pdf` → Endung `.pdf` und dieselbe Enginewahl wie beim Upload; Verbindungsfehler → `ErrorResponse`, kein Traceback.
3. `pytest -q -rs` grün; Sammelzahl, ausgewählte Zahl und Übersprungenes nennen. `ruff check .` grün.
4. `grep -rln 'httpx' backend/app/` findet nur `fetching.py`.
5. `grep -n 'Nichts nachladen' docs/grenzen.md` findet nach dem Merge keinen Satz mehr, der den Endpunkt verschweigt.
6. `cd frontend && npm run typecheck` grün; `types.ts` ist geändert, nichts sonst im Frontend.
