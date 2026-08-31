---
id: 27
title: 'DOC-3 · Inhalte Betrieb: Konfiguration, lokal, Traefik, Authelia'
status: done
priority: medium
created: 2026-08-31T10:21:42.015369338+02:00
updated: 2026-08-31T11:15:16.866117642+02:00
started: 2026-08-31T11:14:38.273522315+02:00
completed: 2026-08-31T11:14:38.273522315+02:00
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


## Nachtrag aus IN-3 (#24)

Compose ersetzt Variablen nur in Label-Werten, nicht in Label-Schluesseln. Der
Router heisst deshalb fest `kaimarkit`; `KAIMARKIT_ROUTER` steht noch in
`docker/.env.example`, wird aber von nichts mehr gelesen. DOC-3 entscheidet: die
Variable streichen oder mit dem Hinweis behalten, dass ein anderer Name beide
Compose-Schichten anfasst. Domaene, Entrypoint, Certresolver und Netzname kommen
weiter aus der Umgebung.

`docs/betrieb/traefik.md` muss ausserdem `!reset` erklaeren: Es verlangt Compose
2.24 oder neuer. Wer aelter faehrt, nimmt den Port aus der Basisdatei und
veroeffentlicht ihn aus einer eigenen `docker-compose.local.yml`.

Aus IN-2 (#22) offen: `KAIMARKIT_HEALTH_START_PERIOD=180s` ist in
`docker/.env.example` angelegt und in `konfiguration.md` noch nicht beschrieben
(Konvention 6).


## Nachtrag aus IN-4 (#25)

Keine neuen Variablen; `.env.example` unveraendert. `AUTH_MIDDLEWARE=kaimarkit-auth`
wird aber von nichts mehr gelesen — derselbe Grund wie bei `KAIMARKIT_ROUTER`: Der
Middleware-Name steht in einem Label-Schluessel, und Compose ersetzt nur Werte.
Beide Variablen stehen noch da und warten auf dieselbe Entscheidung.

Fuer `authelia.md`: Ein leeres `KAIMARKIT_API_MIDDLEWARES` gibt die API frei —
Traefik liest ein leeres `middlewares=` als „keine Middleware". Ein
auskommentierter Block ist dafuer nicht noetig.

Fuer `traefik.md`: Die Routernamen `kaimarkit` und `kaimarkit-api` muessen auf dem
Host eindeutig sein. Deklariert ein anderer Container Router gleichen Namens mit
abweichender Konfiguration, verwirft Traefik stillschweigend **beide**
("Router defined multiple times").

Offen geblieben und an INT-2 (#30) uebergeben: die Anmeldung im Browser gegen ein
echtes Authelia. IN-4 hatte weder Image noch Netz dafuer.


## Ergebnis (akar-07)

Vier Seiten geschrieben, Merge 88b7006 auf main.

- konfiguration.md: alle 32 Variablen aus docker/.env.example mit Standardwert und
  Wirkung, gruppiert nach Quellen/Build, Anwendung, Container, Traefik, Authelia.
  KAIMARKIT_HEALTH_START_PERIOD ist damit beschrieben (offener Punkt aus IN-2
  erledigt).
- lokal.md: cp .env.example, make up, warten auf healthy; Probe mit curl,
  make logs/down, die drei Stellen, die man zuerst anpasst.
- traefik.md: Voraussetzungen, vollstaendiger Aufruf, Label-Tabelle, Map- statt
  Listenform, feste Routernamen, !reset mit Compose 2.24 und der Ausweichweg ueber
  eine eigene docker-compose.local.yml, Warnung vor doppelten Routernamen
  ("Router defined multiple times" verwirft beide), Probe mit docker port.
- authelia.md: dritte Schicht, ForwardAuth, die zwei Adressen in
  AUTHELIA_VERIFY_URL, fester Middlewarename, zweiter /api-Router mit Prioritaet
  100, drei sinnvolle Werte fuer KAIMARKIT_API_MIDDLEWARES einschliesslich leer
  (mit Traefik 3.6.7 geprueft, kein auskommentierter Block noetig). Die
  Browser-Anmeldung gegen ein echtes Authelia ist ausdruecklich als noch nicht
  erprobt vermerkt und an INT-2 (#30) verwiesen.

**Entscheidung (Konvention 6, im selben Commit):** KAIMARKIT_ROUTER und
AUTH_MIDDLEWARE aus docker/.env.example **gestrichen**. Beide Namen stehen in
Label-Schluesseln, und Compose ersetzt nur Werte — die Variablen wirkten nirgends.
Der Grund und der Weg zum Umbenennen (beide Compose-Schichten von Hand) stehen jetzt
in traefik.md bzw. authelia.md. Der Kommentar bei KAIMARKIT_API_MIDDLEWARES verwies
auf die alte Variable und nennt nun den woertlichen Namen kaimarkit-auth@docker.
Keine weitere Fundstelle im Repo (grep leer).

**Pruefung, tatsaechliches Ergebnis:**

- mkdocs build --strict → Exit 0, keine WARNING- und keine ERROR-Zeile. Die rote
  Ausgabe beim Start ist der Hinweis des Material-Teams zu MkDocs 2.0, keine
  Buildwarnung.
- Variablenabgleich mechanisch, nicht nach Augenmass: Namen aus
  docker/.env.example gegen die Codespans in konfiguration.md mit comm/diff —
  **beide Richtungen leer, 32 zu 32.**
- Zwei Fundstellen beim Gegenlesen behoben: Die urspruenglich benutzten
  Definitionslisten rendern nicht, weil def_list in mkdocs.yml nicht aktiviert ist
  (mkdocs.yml gehoert DOC-1, deshalb im Text umgebaut statt in der Konfiguration).
  Deutsche Schlusszeichen auf U+201C korrigiert.

**Hinweis fuer DOC-1/IN-5:** def_list fehlt in markdown_extensions. Kein Fehler,
aber wer Definitionslisten schreibt, bekommt sie als Fliesstext.
