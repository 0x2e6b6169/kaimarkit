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

## Starten

```bash
cp docker/.env.example docker/.env
# In docker/.env eintragen: AUTHELIA_VERIFY_URL passend zum eigenen Authelia
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

## Die drei Variablen

`AUTHELIA_VERIFY_URL` nennt zwei verschiedene Adressen in einer Zeile:

```
http://authelia:9091/api/verify?rd=https://auth.example.com
```

Vor dem Fragezeichen steht die Adresse, unter der Traefik Authelia im Docker-Netz
erreicht — Containername und interner Port, unverschlüsselt, weil beide im selben
Netz stehen. Der Parameter `rd` dagegen ist die Anmeldeseite, wie der Browser sie
sieht: von außen erreichbar und mit TLS. Beide zeigen auf denselben Dienst, nur aus
verschiedenen Blickwinkeln. Wer nur eine der beiden anpasst, bekommt entweder einen
Verbindungsfehler oder eine Weiterleitung ins Leere.

`AUTHELIA_RESPONSE_HEADERS` legt fest, was Traefik von Authelia an die Anwendung
durchreicht: `Remote-User`, `Remote-Groups`, `Remote-Name`, `Remote-Email`.
kaimarkit wertet diese Kopfzeilen nicht aus. Sie stehen bereit, falls später jemand
danach unterscheiden will.

`KAIMARKIT_API_MIDDLEWARES` bekommt den eigenen Abschnitt weiter unten.

## Der Name der Middleware steht fest

`kaimarkit-auth` steht wörtlich in den Label-Schlüsseln, aus demselben Grund wie die
Routernamen: **Compose setzt Variablen nur in Label-Werte ein, nicht in
Label-Schlüssel.** Eine Variable dafür gibt es deshalb nicht in
`docker/.env.example`. Wer die Middleware anders nennen will, ändert
`docker/docker-compose.authelia.yml` von Hand; dort steht der Name viermal, dreimal
in der Definition und einmal am Router.

Der Zusatz `@docker` überall dort, wo die Middleware benannt wird, nennt ihre
Herkunft: Sie definiert sich am eigenen Dienst, und Traefik findet sie über den
Docker-Anbieter.

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
| `…routers.kaimarkit-api.middlewares` | `${KAIMARKIT_API_MIDDLEWARES}` | Der Schalter, um den es geht. |

Die feste Priorität ist Absicht. Ohne sie ordnet Traefik die Regeln nach Länge; das
genügte hier zwar, weil die `/api`-Regel die längere ist, hinge aber am Wortlaut der
anderen. Die Zahl macht den Vorrang davon unabhängig.

Für `KAIMARKIT_API_MIDDLEWARES` gibt es drei sinnvolle Werte.

**`kaimarkit-auth@docker`** — der Standard. Auch die API verlangt eine Anmeldung,
Skripte kommen nicht durch.

**Leer lassen** — die API steht offen, die Oberfläche bleibt geschützt. Traefik
liest ein leeres `middlewares=` als „keine Middleware“: Der Router bleibt aktiv und
meldet keinen Fehler. Geprüft mit Traefik 3.6.7 — der Router stand auf `enabled`,
die Middlewareliste war leer, und ein Aufruf auf `/api` kam durch, während derselbe
Aufruf auf `/` an Authelia hängenblieb. Ein auskommentierter Block in der
Compose-Datei erübrigt sich damit; die leere Variable genügt.

**Ein eigener Middlewarename**, etwa `meine-allowlist@docker` — der Mittelweg: eine
engere Middleware statt der Anmeldung, zum Beispiel eine IP-Allowlist. Sie muss
anderswo definiert sein, sonst verwirft Traefik den Router.

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

Beide Router müssen dort mit `"status": "enabled"` stehen. Steht einer auf
`warning`, fehlt eine benannte Middleware.

Dann die beiden Wege gegeneinander:

```bash
# Eigene Domain einsetzen.
curl -si https://kaimarkit.example.com/ | head -1    # 302 zur Anmeldeseite
curl -sf https://kaimarkit.example.com/api/health    # bei leerer Variable: 200
```

Der vollständige Durchlauf ist gegen Authelia 4.38.19 hinter Traefik 3.6 gelaufen.
Ein Aufruf ohne Sitzung endete mit 302 auf der Anmeldeseite, und zwar mit dem
Rücksprungziel im Parameter `rd`. Nach der Anmeldung stand die Oberfläche unter
`KAIMARKIT_DOMAIN` und füllte ihre Enginewahl aus `/api/capabilities` — der Aufruf
kam also durch dieselbe Middleware. Nach dem Löschen des Sitzungscookies führte
derselbe Weg wieder zur Anmeldeseite.
