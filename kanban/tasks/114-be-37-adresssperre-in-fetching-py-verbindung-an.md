---
id: 114
title: 'BE-37 · Adresssperre in fetching.py: Verbindung an die geprüfte IP binden (DNS-Rebinding)'
status: done
priority: medium
created: 2026-09-03T11:42:55.055749229+02:00
updated: 2026-09-03T14:25:20.343701196+02:00
started: 2026-09-03T14:25:13.918008844+02:00
completed: 2026-09-03T14:25:13.918008844+02:00
assignee: sophie
tags:
    - backend
    - gh-5
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


## Umsetzung (sophie-38)

`check_public` gibt jetzt die Adresse zurück, an die verbunden werden darf, statt nur zu
werfen. Zeigt der Name auf mehrere geprüfte Adressen, gilt die erste; alle müssen
weiterhin öffentlich sein. `fetch_page` ersetzt im Ziel den Namen durch diese Adresse und
lässt den Namen an den beiden Stellen stehen, an denen die Gegenstelle ihn braucht: im
`Host`-Header und in der Erweiterung `sni_hostname`. Jeder Sprung einer Weiterleitung
läuft durch dieselbe Prüfung und dieselbe Bindung; für `urljoin`, den Dateinamen und die
Meldungen bleibt die Adresse mit dem Namen maßgeblich.

**Kein Umweg über `httpcore` nötig.** `sni_hostname` ist eine Erweiterung, die `httpx`
an `httpcore` durchreicht; dort wird sie in `_async/connection.py` zum `server_hostname`
des TLS-Handschlags (`"server_hostname": sni_hostname or self._origin.host`). Die
Zertifikatsprüfung bleibt damit an und prüft weiter den Namen, nicht die Adresse. Ein
eigener Transport war nicht erforderlich; `httpx` bleibt die einzige HTTP-Bibliothek und
steht weiter nur in `fetching.py` (`grep -rln httpx backend/app/` nennt allein diese
Datei). Geprüft mit httpx 0.28.1 und httpcore 1.0.9.

**Rot vor grün.** Die neue Attrappe `rebinding_dns` liefert beim ersten Aufruf
`93.184.216.34`, danach `10.0.0.5`; die Hilfe `connect_target` löst nach, wohin ein
echter Transport verbände — steht im Host ein Name, löst sie ihn im Augenblick des
Verbindungsaufbaus selbst auf, genau wie `httpx` es tut. Vorher:
`assert [connect_target(request) for request in seen] == [PUBLIC]` scheiterte mit
`["10.0.0.5"] != ["93.184.216.34"]`. Nachher grün. Dazu zwei weitere Tests: Pfad, Port
und Abfrage überstehen die Bindung (`https://93.184.216.34:8443/blog/post?a=1`, Host
`example.com:8443`), und jeder Weiterleitungssprung wird einzeln gebunden.

Ein bestehender Test musste nachziehen: `test_a_redirect_into_a_private_network_is_rejected`
unterschied die Sprünge an `request.url.host` — dort steht jetzt die Adresse. Er
unterscheidet sie nun am `Host`-Header, wo der Name geblieben ist.

**TLS-Abruf mit Netz** (einmal, von Hand): `check_public("https://example.com/")` ergab
`172.66.147.243`, `fetch_page` holte darüber `example-domain.html`, 559 Bytes, beginnend
mit `<!doctype html><html lang="en"><head><title>Example Domain</`. Der Handschlag gelang
gegen die Adresse mit `server_hostname=example.com` — hätte die Prüfung die Adresse statt
des Namens genommen, wäre er gescheitert.

**Zahlen:** `pytest -q -rs` im Backend: 207 gesammelt, 200 ausgewählt (7 als `slow`
abgewählt), 200 bestanden, 0 übersprungen. `ruff check .` ohne Befund. Nach dem Rebase auf
`main` erneut gelaufen, gleiches Ergebnis.

Neue Umgebungsvariable war nicht nötig; `docker/.env.example` und
`docs/betrieb/konfiguration.md` bleiben unberührt. Der Absatz „Bekannte Einschränkung" im
Moduldocstring beschrieb die Lücke und ist durch die Beschreibung der Bindung ersetzt.

Zweig `task/114-rebinding`, Merge `c7dd63f`.
