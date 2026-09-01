---
id: 88
title: IN-17 · Drei Kommentare in den Compose-Dateien sagen Falsches
status: done
priority: medium
created: 2026-09-01T18:16:39.541396522+02:00
updated: 2026-09-01T18:26:20.065160826+02:00
started: 2026-09-01T18:26:14.076779579+02:00
completed: 2026-09-01T18:26:14.076779579+02:00
assignee: akar
tags:
    - infra
    - docs
class: standard
---

## Befund (01.09.2026, drei Meldungen aus IN-16)

Drei Stellen in den Compose-Dateien sagen etwas Falsches oder verschweigen etwas, das man beim nächsten Anfassen wissen muss. Alle drei kommen aus dem, was IN-16 (#87) nachgemessen hat.

### 1. Eine Begründung, die widerlegt ist

`docker/docker-compose.yml`, Zeilen 25–27, begründet die Map-Form für `environment` so: „Compose führt Listen additiv zusammen, Maps ersetzen einzelne Schlüssel."

Für `labels` **stimmt das nicht** — IN-16 hat gemessen, dass Compose eine Label-Liste beim Laden zur Map normalisiert und über die Schlüssel zusammenführt. Dieselbe Aussage steht auch auf den Traefik-Seiten und hat dort seit IN-3 (#24) den Verzicht auf die Listenform begründet.

**Die Map-Form für `environment` bleibt trotzdem richtig** — lesbarer, und eine Ergänzungsdatei überschreibt einen einzelnen Schlüssel sichtbar. Nur die Begründung ist es nicht.

**Erst messen, dann schreiben:** Ob Compose auch `environment`-Listen zur Map normalisiert, ist ungeprüft. Die neue Begründung muss zu dem passen, was gemessen wurde, nicht zu dem, was plausibel klingt.

### 2. Zwei Formen nebeneinander, beide richtig

Seit IN-16 stehen in der Traefik-Schicht zwei Zeilen mit verschiedener Ersetzungsform:

    ${KAIMARKIT_TRAEFIK_NAME:-kaimarkit}    mit Doppelpunkt
    ${KAIMARKIT_MIDDLEWARES}                ohne

Der Unterschied ist beabsichtigt: Ein leerer Namensraum ergäbe `traefik.http.routers..rule` — unbrauchbar, deshalb greift die Voreinstellung auch bei leerem Wert. Ein leeres `KAIMARKIT_MIDDLEWARES` ist dagegen eine **gültige Angabe**: „keine Middleware", der dokumentierte Weg für ein `curl` ohne Browsersitzung.

Ohne einen Satz dazu sieht es nach Unachtsamkeit aus, und jemand vereinheitlicht es — und nimmt damit den einen Weg weg, den `docs/betrieb/authelia.md` ausdrücklich beschreibt.

### 3. Eine Falle beim Umsortieren

Verkettung in der `.env` funktioniert **nur vorwärts**: Steht die referenzierte Variable weiter unten, setzt Compose still eine leere Zeichenkette ein und warnt bloß. In `docker/.env.example` stimmt die Reihenfolge heute. Wer die Datei umsortiert, merkt den Bruch nicht.

## Eigene Dateien

- `docker/docker-compose.yml` (Kommentar bei `environment`)
- `docker/docker-compose.traefik.yml` (Kommentar bei den beiden Ersetzungsformen)
- `docker/.env.example` (Hinweis zur Reihenfolge)
- `docs/betrieb/traefik.md`, falls die widerlegte Aussage dort ebenfalls steht

## Vorgaben

Kein Verhalten ändern. Es geht ausschließlich um Kommentare und Dokumentation.

Zu 1: Die widerlegte Aussage kommt weg. Was an ihre Stelle tritt, richtet sich nach der Messung — steht die Begründung für `environment` nach der Prüfung ohne Stütze da, ist „Map-Form, weil lesbarer und weil eine Ergänzung sichtbar einen Schlüssel ersetzt" ehrlicher als eine neue technische Behauptung.

Zu 2: Ein Satz, der beide Formen nebeneinander erklärt und sagt, warum sie verschieden bleiben müssen.

Zu 3: Ein Satz am Kopf von `.env.example`.

## Prüfung

- Keine Datei behauptet mehr, Compose führe Label-Listen additiv zusammen.
- Der Satz zu den zwei Ersetzungsformen nennt beide Gründe und macht klar, dass das Vereinheitlichen einen dokumentierten Weg zerstört.
- `docker compose -f … config` liefert vor und nach dem Ticket dieselbe Ausgabe — es hat sich nichts als Kommentare geändert. Das ist die Prüfung, dass kein Verhalten mitgegangen ist.
- `mkdocs build --strict` läuft durch.


---

## Umgesetzt (akar-30)

Branch `task/88-compose-comments`, Commit `cbd76ec`, Merge `d166878`.

### Gemessen: environment-Listen verhalten sich wie labels

Compose v5.1.4, zwei Dateien, Dienst `app`:

    Basis:      environment: [ONLY_BASE=base, SHARED=from-base, DUP=first, DUP=second]
    Ergaenzung: environment: [SHARED=from-override, ONLY_OVER=over]
    -> DUP: second | ONLY_BASE: base | ONLY_OVER: over | SHARED: from-override

Der doppelte Schluessel steht einmal da, mit dem Wert der zweiten Datei. Die
Schluessel, die nur eine Datei nennt, bleiben alle erhalten — es ist also weder
ein Aneinanderhaengen noch ein Ersetzen der ganzen Liste, sondern eine
Zusammenfuehrung ueber die Schluessel. Dasselbe Ergebnis bei gemischten Formen,
in beiden Richtungen: Map in der Basis und Liste in der Ergaenzung, und
umgekehrt. Compose normalisiert die Liste beim Laden zur Map, wie bei `labels`.

**Gegenprobe, damit die Aussage eine Grenze hat:** `ports` und `volumes` haengt
Compose tatsaechlich aneinander — zwei Dateien, je ein Eintrag, danach standen
beide da. Das ist der Grund fuer das `!reset` in der Traefik-Schicht, und es
bleibt richtig.

**Folge fuer den Kommentar:** Die Begruendung fuer die Map-Form bei `environment`
steht ohne technische Stuetze da. Sie lautet jetzt „lesbarer, und eine
Ergaenzungsdatei ersetzt sichtbar einen einzelnen Schluessel", mit der Messung
und dem Satz „Die Listenform verloere also nichts" dahinter. Keine neue
Behauptung an die Stelle der alten.

### Die drei Punkte

1. `docker/docker-compose.yml` — die widerlegte Begruendung ist weg, die Messung
   steht dort.
2. `docker/docker-compose.authelia.yml` — der Satz zu den beiden
   Ersetzungsformen. **Abweichung von der Dateiliste des Tickets:** Der Rumpf
   nennt dafuer `docker-compose.traefik.yml`, aber `${KAIMARKIT_MIDDLEWARES}`
   steht dort gar nicht. Beide Formen stehen in der Authelia-Schicht, in Zeile 75
   sogar in derselben Zeile. Der Satz gehoert deshalb dorthin; in
   `docker-compose.traefik.yml` steht nur ein Dreizeiler, der auf die andere
   Schicht verweist, damit ihr Leser die Abweichung nicht fuer einen Fehler haelt.
   Kein offenes Ticket besass `docker-compose.authelia.yml`.
   Genannt sind beide dokumentierten Angaben: leeres `KAIMARKIT_API_MIDDLEWARES`
   (curl ohne Browsersitzung an `/api`) und leeres `KAIMARKIT_MIDDLEWARES`
   (Oberflaeche offen) — beide beschreibt `docs/betrieb/authelia.md`.
3. `docker/.env.example` — Satz am Kopf. Nachgemessen: `MW=${X}-auth@docker` nach
   `X=probe` ergibt `probe-auth@docker`; in umgekehrter Reihenfolge
   `-auth@docker`, dazu nur `level=warning ... Defaulting to a blank string`.
   Der ausfuehrliche Hinweis in der Authelia-Gruppe (aus IN-16) bleibt stehen; am
   Kopf steht er, weil ihn liest, wer die Datei umsortiert.

`docs/betrieb/traefik.md` sagte „Gegen Listen spricht sonst, dass Compose sie
aneinanderhaengt" und schraenkte das nur fuer `labels` ein. Der Satz nennt jetzt
die Trennlinie: `ports` und `volumes` einerseits, `labels` und `environment`
andererseits.

### Pruefung

- Keine Datei behauptet mehr, Compose fuehre Label-Listen additiv zusammen:
  `grep -rniE "additiv|aneinander"` ueber `docker/` und `docs/` liefert nur noch
  die Stellen zu `ports`/`volumes` und die berichtigten Saetze.
- Der Satz zu den zwei Formen nennt beide Gruende und sagt, was das
  Vereinheitlichen kostet.
- **`docker compose config` byteweise gleich, vorher und nachher.** Gegen die
  Arbeitskopie `docker/.env` in allen drei Kombinationen (Basis; + Traefik;
  + Traefik + Authelia): stdout und stderr identisch. Zusaetzlich gegen
  `.env.example`: einmal nur die `.env.example` variiert (identisch), einmal nur
  die Compose-Dateien (identisch bis auf den Build-Kontext, der vom Ablageort der
  Dateien kommt, nicht von der Aenderung).
- `mkdocs build --strict` laeuft durch.
- Der Container `kaimarkit` des Nutzers auf 127.0.0.1:8080 blieb unangetastet;
  nichts wurde gestartet oder gestoppt. `docker/.env` nicht ueberschrieben — fuer
  die Messung eine Kopie in den Worktree gelegt, die `.gitignore` faengt sie ab.

## Befunde ausserhalb dieses Tickets

1. **`ENTWURF.md:449` sagt dasselbe Falsche**: „Labels in Map-Form, nicht als
   Liste: Compose fuehrt Listen additiv zusammen …". Nicht angefasst — `ENTWURF.md`
   haelt laut CLAUDE.md die Herkunft fest, nicht die Vorschrift, und stand nicht in
   der Dateiliste. Wenn der Entwurf trotzdem stimmen soll, ist das ein eigenes
   Ticket.
2. **Umlaute in `docker/`**: Die vier Dateien unter `docker/` stehen vollstaendig
   in ASCII-Umschrift, die Seiten unter `docs/` mit Umlauten. Die neuen Saetze
   sind mit Umlauten geschrieben, wie es die Prosa-Regel verlangt; die Dateien
   sind dadurch gemischt. Ein Ticket „Umschrift in den Compose-Dateien und im
   Dockerfile" wuerde das aufloesen — dieselbe Art wie BE-21/BE-22/BE-23, nur
   fuer Kommentare statt fuer nutzersichtbare Meldungen.
