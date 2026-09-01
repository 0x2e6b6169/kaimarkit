# Authelia

Authelia setzt eine Anmeldung vor kaimarkit. Traefik fragt bei jeder Anfrage dort
nach, ob die Sitzung gilt, und leitet sonst zur Anmeldeseite weiter. Das erledigt
eine ForwardAuth-Middleware.

`docker-compose.authelia.yml` ist die dritte Schicht und setzt die Traefik-Schicht
voraus: Die Middleware hängt an dem Router, den jene anlegt.

!!! note "Diese Datei startet Authelia nicht mit"
    Sie erwartet einen laufenden Authelia-Dienst im Traefik-Netz und verweist nur
    auf ihn. Authelia einzurichten — Benutzerdatenbank, Zugriffsregeln, Sitzungen —
    steht in dessen eigener Dokumentation.

## Was vorher da sein muss

Alles aus [Traefik](traefik.md), dazu:

- Ein laufender Authelia im selben Docker-Netz, unter seinem Containernamen
  erreichbar.
- Eine Zugriffsregel in Authelia, die `KAIMARKIT_DOMAIN` abdeckt. Ohne sie greift
  Authelias Standardregel.
- Ein DNS-Eintrag für die Anmeldeseite, etwa `auth.example.com`.
- Eine ForwardAuth-Middleware, die Traefik kennt. Bringt die vorhandene Authelia
  keine mit, definiert diese Schicht eine eigene — siehe den nächsten Abschnitt.

## Starten

```bash
cp docker/.env.example docker/.env
# Heisst die Middleware der vorhandenen Authelia "authelia@docker", genuegt das.
make up-authelia
```

Ohne `make`, alle drei Dateien in dieser Reihenfolge:

```bash
docker compose -f docker/docker-compose.yml \
               -f docker/docker-compose.traefik.yml \
               -f docker/docker-compose.authelia.yml up -d --build
```

Die Reihenfolge entscheidet. Fehlt die mittlere Datei, gibt es keinen Router, an den
sich die Middleware hängen könnte.

## Zwei Wege zur Middleware

Eine ForwardAuth-Middleware muss irgendwo definiert sein. Entweder bringt die
vorhandene Authelia sie mit, oder diese Schicht definiert eine eigene. Beides
funktioniert; die Wahl fällt über `KAIMARKIT_MIDDLEWARES` und
`KAIMARKIT_API_MIDDLEWARES`.

### Die vorhandene Middleware — der Normalfall

Wer Authelia betreibt, hat sie meist per Docker-Label an sich selbst beschriftet und
schaltet sie so vor einen Dienst:

```yaml
traefik.http.routers.whoami-secure.middlewares: "authelia@docker"
```

Dann ist nichts weiter zu tun. Beide Variablen stehen voreingestellt auf
`authelia@docker`, und `AUTHELIA_VERIFY_URL` und `AUTHELIA_RESPONSE_HEADERS` bleiben
ungenutzt — kaimarkit hängt an derselben Middleware wie alles andere hinter dieser
Authelia. Ändert sich dort etwas, ändert es sich an einer Stelle.

Eine Bedingung: Der Zusatz hinter dem `@` muss stimmen. Er gehört nicht zum Namen,
sondern nennt den Traefik-Anbieter, aus dem die Middleware stammt.

### Die eigene Middleware

Wessen Authelia ihre Middleware nicht per Docker-Label mitbringt — weil sie aus einer
Datei kommt, außerhalb von Docker läuft oder gar keine hat —, trägt
`kaimarkit-auth@docker` ein und setzt dafür die beiden Variablen:

```
KAIMARKIT_MIDDLEWARES=kaimarkit-auth@docker
KAIMARKIT_API_MIDDLEWARES=kaimarkit-auth@docker
AUTHELIA_VERIFY_URL=http://authelia:9091/api/verify?rd=https://auth.example.com
AUTHELIA_RESPONSE_HEADERS=Remote-User,Remote-Groups,Remote-Name,Remote-Email
```

`AUTHELIA_VERIFY_URL` nennt zwei verschiedene Adressen in einer Zeile. Vor dem
Fragezeichen steht die Adresse, unter der Traefik Authelia im Docker-Netz erreicht —
Containername und interner Port, unverschlüsselt, weil beide im selben Netz stehen.
Der Parameter `rd` dagegen ist die Anmeldeseite, wie der Browser sie sieht: von außen
erreichbar und mit TLS. Beide zeigen auf denselben Dienst, nur aus verschiedenen
Blickwinkeln. Wer nur eine der beiden anpasst, bekommt entweder einen
Verbindungsfehler oder eine Weiterleitung ins Leere.

`AUTHELIA_RESPONSE_HEADERS` legt fest, was Traefik von Authelia an die Anwendung
durchreicht: `Remote-User`, `Remote-Groups`, `Remote-Name`, `Remote-Email`. kaimarkit
wertet diese Kopfzeilen nicht aus. Sie stehen bereit, falls später jemand danach
unterscheiden will.

Wer den ersten Weg geht, sollte prüfen, dass seine vorhandene Middleware dieselben
Kopfzeilen durchreicht — kaimarkit braucht sie zwar nicht, aber eine Authelia, die
gar keine durchreicht, verrät später niemandem, wer angemeldet war.

Die eigene Middleware bleibt immer definiert, auch wenn kein Router sie benutzt. Eine
leere `AUTHELIA_VERIFY_URL` stört dabei nicht: Traefik 3.6.25 führte die ungenutzte
Definition unter `/api/http/middlewares` auf `enabled`, ohne Fehler und ohne Eintrag
im Log.

## `@docker` oder `@file` — der Zusatz entscheidet

Traefik hängt an jeden Namen den Anbieter an, aus dem er stammt. Dieselbe Authelia
heißt `authelia@docker`, wenn sie ihre Middleware per Container-Label definiert, und
`authelia@file`, wenn sie aus einer statischen Konfigurationsdatei kommt. Unter dem
falschen Zusatz findet Traefik sie nicht.

Der Fehler sieht nicht nach einem Tippfehler aus, und er ist folgenreich: Der Router
verschwindet. Gemessen mit Traefik 3.6.25 gegen einen absichtlich falschen Wert
`authelia@file` — der Router stand unter `/api/http/routers` auf `"status":
"disabled"` mit dem Fehler `middleware "authelia@file" does not exist`, und der Pfad
`/` antwortete mit 404. Der `/api`-Router blieb dabei unberührt: Er hat seine eigene
Variable und antwortete weiter mit 401.

!!! success "Der falsche Name öffnet den Dienst nicht"
    Das ist die beruhigende Hälfte: Traefik lässt einen Router mit unbekannter
    Middleware nicht ungeschützt laufen, sondern gar nicht. Wer sich vertippt,
    bekommt einen toten Dienst und merkt es sofort. Dasselbe gilt für die eigene
    Middleware mit leerer `AUTHELIA_VERIFY_URL`: Sie antwortet mit 500, nicht mit
    dem Inhalt.

Welche Namen der eigene Traefik kennt, sagt seine API:

```bash
curl -sf http://<traefik-host>:8080/api/http/middlewares | jq -r '.[].name'
```

## Der Name der eigenen Middleware steht fest

`kaimarkit-auth` steht wörtlich in den Label-Schlüsseln, aus demselben Grund wie die
Routernamen: **Compose setzt Variablen nur in Label-Werte ein, nicht in
Label-Schlüssel.** Eine Variable dafür gibt es deshalb nicht in
`docker/.env.example`. Wer die Middleware anders nennen will, ändert
`docker/docker-compose.authelia.yml` von Hand; dort steht der Name dreimal, alle drei
Male in der Definition.

Am Router steht kein fester Name. Dort entscheidet `KAIMARKIT_MIDDLEWARES`, und die
eigene Middleware ist nur einer der zwei Werte, die dort sinnvoll sind.

## Die API bleibt erreichbar

Hinter Authelia bekommt jeder Aufruf ohne Browser-Sitzung eine Weiterleitung zum
Login. Ein `curl` bekäme also die Anmeldeseite statt Markdown, und jedes Skript
liefe ins Leere.

Dagegen legt die Schicht einen zweiten Router allein für `/api` an:

| Label | Wert | Wozu |
| --- | --- | --- |
| `…routers.kaimarkit-api.rule` | ``Host(`${KAIMARKIT_DOMAIN}`) && PathPrefix(`/api`)`` | Nur die API. |
| `…routers.kaimarkit-api.priority` | `100` | Vorrang vor dem Router für alles Übrige. |
| `…routers.kaimarkit-api.service` | `kaimarkit` | Derselbe Dienst wie beim ersten Router. |
| `…routers.kaimarkit-api.middlewares` | `${KAIMARKIT_API_MIDDLEWARES-authelia@docker}` | Der Schalter, um den es geht. |

Die feste Priorität ist Absicht. Ohne sie ordnet Traefik die Regeln nach Länge; das
genügte hier zwar, weil die `/api`-Regel die längere ist, hinge aber am Wortlaut der
anderen. Die Zahl macht den Vorrang davon unabhängig.

Für `KAIMARKIT_API_MIDDLEWARES` gibt es drei sinnvolle Werte.

**Ein Middlewarename** — der Standard, voreingestellt `authelia@docker`. Auch die API
verlangt eine Anmeldung, Skripte kommen nicht durch.

**Leer lassen** — die API steht offen, die Oberfläche bleibt geschützt. Traefik
liest ein leeres `middlewares=` als „keine Middleware“: Der Router bleibt aktiv und
meldet keinen Fehler. Geprüft mit Traefik 3.6.7 — der Router stand auf `enabled`,
die Middlewareliste war leer, und ein Aufruf auf `/api` kam durch, während derselbe
Aufruf auf `/` an Authelia hängenblieb. Ein auskommentierter Block in der
Compose-Datei erübrigt sich damit; die leere Variable genügt.

**Eine engere Middleware**, etwa `meine-allowlist@docker` — der Mittelweg: eine
IP-Allowlist statt der Anmeldung. Sie muss anderswo definiert sein, sonst verwirft
Traefik den Router.

`KAIMARKIT_MIDDLEWARES` kennt dieselben drei Werte, und ein leerer Wert bedeutet auch
dort „keine Middleware“ — dann steht die Oberfläche offen. Das ergibt selten Sinn:
Wer die Anmeldung vor der Oberfläche nicht braucht, braucht die Authelia-Schicht
nicht und bleibt bei [Traefik](traefik.md).

!!! warning "Offene API heißt offener Dienst"
    Die gesamte Funktion von kaimarkit steckt in `/api`. Wer die Middleware
    entfernt, gibt sie preis — die Anmeldung schützt dann nur noch die Oberfläche.
    Das ist im internen Netz vertretbar und im offenen Internet nicht.

In der Compose-Datei steht der Wert in Anführungszeichen. Sie sorgen dafür, dass
eine leere Variable als leere Zeichenkette ankommt; ein blanker Wert stünde in YAML
für `null`.

## Prüfen

Der Router und seine Middleware lassen sich unmittelbar ablesen:

```bash
curl -sf http://<traefik-host>:8080/api/http/routers | jq '.[] | select(.name | startswith("kaimarkit"))'
```

Beide Router müssen dort mit `"status": "enabled"` stehen und im Feld `middlewares`
den Namen führen, der in `docker/.env` steht. Steht einer auf `disabled`, nennt das
Feld `error` die fehlende Middleware beim Namen.

Dann die beiden Wege gegeneinander:

```bash
# Eigene Domain einsetzen.
curl -si https://kaimarkit.example.com/ | head -1    # 302 zur Anmeldeseite
curl -sf https://kaimarkit.example.com/api/health    # bei leerer Variable: 200
```

Die Wahl der Middleware ist gegen Traefik 3.6.25 durchgemessen, jedes Mal an
`/api/http/routers` abgelesen statt aus der Compose-Datei geschlossen:

| `KAIMARKIT_MIDDLEWARES` | Router | Antwort auf `/` |
| --- | --- | --- |
| `authelia@docker` | `enabled`, `["authelia@docker"]` | 401 von der ForwardAuth |
| `kaimarkit-auth@docker` | `enabled`, `["kaimarkit-auth@docker"]` | 401 von der ForwardAuth |
| `authelia@file` (nicht vorhanden) | `disabled`, Fehler `middleware … does not exist` | 404 |
| leer | `enabled`, keine Middleware | 200, ungeschützt |

Die 401 stammt aus dem Messaufbau, in dem an Authelias Stelle ein Dienst stand, der
jede Anfrage abweist. Eine echte Authelia antwortet an dieser Stelle mit 302 auf die
Anmeldeseite. Beides heißt dasselbe: Die Anfrage erreichte kaimarkit nicht.

Der vollständige Durchlauf ist gegen Authelia 4.38.19 hinter Traefik 3.6 gelaufen.
Ein Aufruf ohne Sitzung endete mit 302 auf der Anmeldeseite, und zwar mit dem
Rücksprungziel im Parameter `rd`. Nach der Anmeldung stand die Oberfläche unter
`KAIMARKIT_DOMAIN` und füllte ihre Enginewahl aus `/api/capabilities` — der Aufruf
kam also durch dieselbe Middleware. Nach dem Löschen des Sitzungscookies führte
derselbe Weg wieder zur Anmeldeseite.
