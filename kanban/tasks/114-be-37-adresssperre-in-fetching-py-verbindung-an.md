---
id: 114
title: 'BE-37 · Adresssperre in fetching.py: Verbindung an die geprüfte IP binden (DNS-Rebinding)'
status: in-progress
priority: medium
created: 2026-09-03T11:42:55.055749229+02:00
updated: 2026-09-03T14:20:20.147017326+02:00
assignee: sophie
tags:
    - backend
    - gh-5
claimed_by: sophie-38
claimed_at: 2026-09-03T14:20:20.147017326+02:00
class: standard
---

## Ziel

Befund aus BE-35 (#107): `fetching.py` löst den Hostnamen auf und prüft jede Adresse, aber `httpx` löst beim Verbindungsaufbau erneut auf. Ein Name, der zwischen den beiden Auflösungen von einer öffentlichen auf eine private Adresse wechselt (DNS-Rebinding), käme durch. Der Nutzer hat für Issue #5 „nur öffentliches http(s)" entschieden; die Sperre soll das auch unter einem gegnerischen DNS halten.

## Eigene Dateien

- `backend/app/fetching.py`
- `backend/tests/test_fetching.py`

## Vorgaben

- Der Abruf geht an die geprüfte IP-Adresse; der Hostname steht nur noch im `Host`-Header und in SNI. Der gangbare Weg in httpx: ein eigener Transport, der die Zieladresse setzt (`httpx.AsyncHTTPTransport(local_address=…)` reicht nicht; gemeint ist die Gegenstelle). Wer feststellt, dass httpx das ohne Umweg über `httpcore` nicht hergibt, meldet das mit Beleg und schlägt den kleinsten Umweg vor, statt eine zweite HTTP-Bibliothek einzuführen.
- Bei mehreren geprüften Adressen die erste nehmen; alle müssen öffentlich sein (gilt schon).
- Redirects: jeder Sprung läuft durch dieselbe Prüfung und dieselbe Bindung.
- Zertifikatsprüfung bleibt an: Der Hostname muss weiter gegen das Zertifikat geprüft werden, nicht die IP.
- Konvention 2 und 3 unverändert: `httpx` nur in `fetching.py`, Fehler als `ConversionError` oder `InvalidUrl`.

## Prüfung

1. Vorher rot: Ein Test mit einer Attrappe für die Namensauflösung, die beim ersten Aufruf eine öffentliche und beim zweiten eine private Adresse liefert, während der Transport festhält, wohin verbunden wird. Vorher verbindet der Abruf zur privaten Adresse; nachher zur geprüften öffentlichen.
2. Ein TLS-Abruf gegen `https://example.com/` (einmal, von Hand, mit Netz) gelingt weiterhin; die Notiz nennt das Ergebnis.
3. `pytest -q -rs` grün; Sammelzahl, ausgewählte Zahl und Übersprungenes nennen. `ruff check .` grün.
