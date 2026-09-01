# Traefik

Hinter Traefik hängt kaimarkit an einem Hostnamen, bekommt sein Zertifikat vom
Certresolver und veröffentlicht auf dem Host keinen Port mehr. Traefik erreicht den
Container über ein gemeinsames Docker-Netz.

`docker-compose.traefik.yml` ist eine Ergänzung zur Basisdatei und läuft nie allein.

## Was vorher da sein muss

- Ein laufender Traefik mit aktiviertem Docker-Anbieter.
- Das Docker-Netz aus `TRAEFIK_NETWORK`. Compose legt es nicht an, es steht in der
  Ergänzungsdatei als `external: true`. Falls es noch fehlt:
  `docker network create traefik-web`.
- Ein Entrypoint unter dem Namen aus `TRAEFIK_ENTRYPOINT` und ein Certresolver unter
  dem aus `TRAEFIK_CERTRESOLVER`. Beide gehören zur Traefik-Konfiguration, nicht zu
  kaimarkit.
- Ein DNS-Eintrag für `KAIMARKIT_DOMAIN`, der auf den Traefik-Host zeigt. Ohne ihn
  stellt der Certresolver kein Zertifikat aus.

## Starten

```bash
cp docker/.env.example docker/.env
# In docker/.env eintragen: KAIMARKIT_DOMAIN, TRAEFIK_NETWORK,
# TRAEFIK_ENTRYPOINT, TRAEFIK_CERTRESOLVER
make up-traefik
```

Ohne `make`, mit beiden Dateien in dieser Reihenfolge:

```bash
docker compose -f docker/docker-compose.yml \
               -f docker/docker-compose.traefik.yml up -d --build
```

Die Reihenfolge entscheidet: Die zweite Datei überschreibt Werte der ersten. Wer sie
vertauscht, holt sich den Host-Port der Basisdatei zurück.

## Wie die Labels gebaut sind

Die Labels stehen als Liste, nicht als Map. Der Grund steht in den Schlüsseln selbst:
Der Routername ist Teil des Labelnamens, und **Compose setzt Variablen nur in Werte
ein, nicht in Schlüssel**. In der Listenform ist das ganze Label ein Wert, deshalb
greift `${KAIMARKIT_TRAEFIK_NAME}` dort auch links vom Gleichheitszeichen. In Map-Form
bliebe ein `${...}` wörtlich stehen und ergäbe einen Routernamen mit einem
Dollarzeichen darin.

Gegen Listen spricht sonst, dass Compose sie aneinanderhängt, statt einzelne Einträge
zu ersetzen — eine dritte Schicht bekäme dann ein zweites Label daneben statt eines
geänderten. Das gilt für `ports` und `volumes`, nicht für `labels` und nicht für
`environment`: Deren Listen macht Compose beim Laden zu Maps und führt sie danach über
die Schlüssel zusammen. Nachgemessen mit Compose v5.1.4, zwei Dateien in Listenform,
ein Schlüssel in beiden — er stand danach einmal da, mit dem Wert der zweiten Datei;
die Schlüssel aus nur einer Datei blieben alle erhalten. Für `environment` ergab
dieselbe Messung dasselbe, auch bei gemischten Formen. Die
[Authelia-Schicht](authelia.md) ersetzt Einträge von hier also weiterhin.

Die Labels im Einzelnen. `<name>` steht für `KAIMARKIT_TRAEFIK_NAME`, voreingestellt
`kaimarkit`; die Präfixe `traefik.http.routers.<name>` und
`traefik.http.services.<name>` sind abgekürzt:

| Label | Wert | Wozu |
| --- | --- | --- |
| `traefik.enable` | `true` | Traefik nimmt den Container überhaupt an. |
| `traefik.docker.network` | `${TRAEFIK_NETWORK}` | Welches Netz Traefik benutzt. |
| `…routers.<name>.rule` | ``Host(`${KAIMARKIT_DOMAIN}`)`` | Welche Anfragen hierher gehören. |
| `…routers.<name>.entrypoints` | `${TRAEFIK_ENTRYPOINT}` | An welchem Eingang der Router hängt. |
| `…routers.<name>.tls` | `true` | Der Router terminiert TLS. |
| `…routers.<name>.tls.certresolver` | `${TRAEFIK_CERTRESOLVER}` | Wer das Zertifikat besorgt. |
| `…services.<name>.loadbalancer.server.port` | `8000` | Der Port **im Container**. |

Das Netz-Label ist keine Zierde. Hängt der Container an mehreren Netzen, wählt
Traefik sonst unter Umständen das falsche und läuft in eine Adresse, die es nicht
erreicht.

Der Port 8000 ist der Port im Container. Traefik spricht den Dienst unmittelbar im
gemeinsamen Netz an, `KAIMARKIT_HOST_PORT` spielt hier keine Rolle mehr.

## Der Namensraum der Traefik-Namen

Router, Dienst und Middleware bekommen ihre Namen aus einer einzigen Variablen,
`KAIMARKIT_TRAEFIK_NAME`. Voreingestellt lautet sie `kaimarkit`, und daraus wird:

| Was | Name |
| --- | --- |
| Router für die Oberfläche | `${KAIMARKIT_TRAEFIK_NAME}` |
| Router für `/api` | `${KAIMARKIT_TRAEFIK_NAME}-api` |
| Traefik-Dienst | `${KAIMARKIT_TRAEFIK_NAME}` |
| eigene ForwardAuth-Middleware | `${KAIMARKIT_TRAEFIK_NAME}-auth` |

Diese Namen gelten **je Traefik-Instanz, nicht je Container**. Wer zwei kaimarkit
hinter dieselbe Traefik hängt — Produktion und Test, zwei Mandanten —, gibt dem
zweiten Aufbau hier einen eigenen Wert.

Der Compose-Dienst heißt weiterhin `kaimarkit`. Die Variable ändert nichts an
`docker compose logs kaimarkit`, nichts an den Makefile-Zielen und nichts am
Containernamen; dafür gibt es `KAIMARKIT_CONTAINER_NAME`.

!!! danger "Ein doppelter Routername legt beide Router still"
    Deklariert ein zweiter Container einen Router gleichen Namens mit abweichender
    Konfiguration, verwirft Traefik **beide**. Nach außen antwortet dann keiner von
    beiden — und den Containern sieht man nichts an, sie laufen ja.

    Nachgemessen mit Traefik 3.6.25: Zwei kaimarkit unter verschiedenen Domains, beide
    mit demselben `KAIMARKIT_TRAEFIK_NAME`. Danach führte `/api/http/routers` keinen
    der beiden Router mehr auf, beide Domains antworteten mit 404, und im Protokoll
    stand `Router defined multiple times with different configurations` mit den Namen
    beider Container. Nachdem die zwei Aufbauten verschiedene Werte bekamen, lief
    jeder wieder unter seiner eigenen Domain.

### Zwei Instanzen nebeneinander

Der zweite Aufbau braucht vier eigene Werte in seiner `docker/.env`:

```
KAIMARKIT_PROJECT_NAME=kaimarkit-test
KAIMARKIT_CONTAINER_NAME=kaimarkit-test
KAIMARKIT_TRAEFIK_NAME=kaimarkit-test
KAIMARKIT_DOMAIN=kaimarkit-test.example.com
```

Die ersten beiden trennen Compose-Projekt und Container, der dritte trennt die
Traefik-Namen, der vierte die Domain. Wer den dritten vergisst, bekommt den Fall aus
dem Kasten darüber: zwei laufende Container und zwei tote Domains.

Ob die Trennung greift, sagt die Traefik-API — nicht die Compose-Datei:

```bash
curl -sf http://<traefik-host>:8080/api/http/routers | jq -r '.[].name'
curl -sf http://<traefik-host>:8080/api/http/services | jq -r '.[] | "\(.name) \(.loadBalancer.servers // [])"'
```

Jeder Name darf dort nur einmal vorkommen, und die beiden Dienste müssen auf
verschiedene Container-Adressen zeigen.

## `!reset` braucht Compose 2.24

Die Basisdatei veröffentlicht einen Port auf dem Host. Hinter Traefik soll sie das
nicht mehr, und genau das erledigt die Zeile

```yaml
ports: !reset []
```

Ohne den Tag führt Compose die beiden Portlisten zusammen, und der Dienst hängt
weiter am Host-Port — offen neben dem Reverse Proxy, was den ganzen Aufbau
entwertet. Der Tag verlangt **Compose 2.24 oder neuer**. Die eigene Version zeigt:

```bash
docker compose version
```

Ist sie älter, gibt es einen Ausweichweg. Er dreht die Richtung um: Statt die
Veröffentlichung nachträglich zurückzunehmen, kommt sie gar nicht erst in die Basis.

1. Den ganzen `ports:`-Block aus `docker/docker-compose.yml` streichen.
2. Eine eigene `docker/docker-compose.local.yml` anlegen:

    ```yaml
    services:
      kaimarkit:
        ports:
          - "${KAIMARKIT_BIND_ADDR}:${KAIMARKIT_HOST_PORT}:8000"
    ```

3. Die Zeile `ports: !reset []` aus `docker/docker-compose.traefik.yml` streichen.

Der lokale Betrieb nimmt danach beide Dateien:

```bash
docker compose -f docker/docker-compose.yml \
               -f docker/docker-compose.local.yml up -d --build
```

Der Traefik-Aufbau bleibt beim Aufruf von oben und braucht kein `!reset` mehr.

## Prüfen

```bash
docker compose -f docker/docker-compose.yml \
               -f docker/docker-compose.traefik.yml ps
docker port kaimarkit          # muss leer bleiben
curl -sf https://kaimarkit.example.com/api/health   # eigene Domain einsetzen
```

`docker port` ist die Probe auf `!reset`: Kommt dort eine Zeile, hängt der Dienst
noch am Host-Port, und die Compose-Version ist zu alt.

Antwortet Traefik mit 404, kennt es den Router nicht. Dann steht der Container
meistens nicht im richtigen Netz — `docker inspect -f '{{json .NetworkSettings.Networks}}' kaimarkit`
zeigt, an welchen er hängt.

Soll zusätzlich eine Anmeldung davor, geht es weiter mit [Authelia](authelia.md).
