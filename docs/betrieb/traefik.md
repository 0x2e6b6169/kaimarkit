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

Die Labels stehen als Map, nicht als Liste. Compose führt Listen additiv zusammen —
eine dritte Schicht könnte einen einzelnen Eintrag dann nicht mehr ersetzen, sondern
hängte ein zweites Label daneben. Bei einer Map ersetzt sie den Schlüssel. Die
[Authelia-Schicht](authelia.md) lebt von dieser Eigenschaft.

Die Labels im Einzelnen — die Präfixe `traefik.http.routers.kaimarkit` und
`traefik.http.services.kaimarkit` sind hier abgekürzt:

| Label | Wert | Wozu |
| --- | --- | --- |
| `traefik.enable` | `true` | Traefik nimmt den Container überhaupt an. |
| `traefik.docker.network` | `${TRAEFIK_NETWORK}` | Welches Netz Traefik benutzt. |
| `…routers.kaimarkit.rule` | ``Host(`${KAIMARKIT_DOMAIN}`)`` | Welche Anfragen hierher gehören. |
| `…routers.kaimarkit.entrypoints` | `${TRAEFIK_ENTRYPOINT}` | An welchem Eingang der Router hängt. |
| `…routers.kaimarkit.tls` | `true` | Der Router terminiert TLS. |
| `…routers.kaimarkit.tls.certresolver` | `${TRAEFIK_CERTRESOLVER}` | Wer das Zertifikat besorgt. |
| `…services.kaimarkit.loadbalancer.server.port` | `8000` | Der Port **im Container**. |

Das Netz-Label ist keine Zierde. Hängt der Container an mehreren Netzen, wählt
Traefik sonst unter Umständen das falsche und läuft in eine Adresse, die es nicht
erreicht.

Der Port 8000 ist der Port im Container. Traefik spricht den Dienst unmittelbar im
gemeinsamen Netz an, `KAIMARKIT_HOST_PORT` spielt hier keine Rolle mehr.

## Die Routernamen stehen fest

`kaimarkit` und `kaimarkit-api` stehen wörtlich in den Label-Schlüsseln, und das
lässt sich nicht über die Umgebung ändern: **Compose setzt Variablen nur in
Label-Werte ein, nicht in Label-Schlüssel.** Ein `${...}` links vom Doppelpunkt
bliebe unverändert stehen und ergäbe einen Routernamen mit einem Dollarzeichen
darin.

Deshalb gibt es dafür keine Variable in `docker/.env.example`. Wer die Router anders
nennen will, ändert `docker/docker-compose.traefik.yml` und
`docker/docker-compose.authelia.yml` von Hand — beide, denn die Authelia-Schicht
hängt ihre Middleware an denselben Routernamen.

!!! danger "Ein doppelter Routername legt beide Router still"
    Routernamen müssen auf dem Traefik-Host eindeutig sein. Deklariert ein anderer
    Container einen Router gleichen Namens mit abweichender Konfiguration, verwirft
    Traefik **beide** und schreibt „Router defined multiple times“ ins Protokoll.
    Nach außen antwortet dann keiner von beiden. Das fällt niemandem auf, der nur
    auf die Container schaut — sie laufen ja. Wer neben kaimarkit einen zweiten
    Dienst gleichen Namens betreibt, benennt einen von beiden um.

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
