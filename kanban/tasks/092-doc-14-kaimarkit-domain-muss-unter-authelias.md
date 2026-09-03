---
id: 92
title: DOC-14 · KAIMARKIT_DOMAIN muss unter Authelias Cookie-Domaene liegen
status: done
priority: high
created: 2026-09-01T19:10:53.816072854+02:00
updated: 2026-09-03T14:27:02.238236529+02:00
started: 2026-09-03T14:20:13.632175283+02:00
completed: 2026-09-03T14:26:50.275354889+02:00
assignee: akar
tags:
    - docs
    - infra
class: standard
---

## Befund (01.09.2026, am echten VPS-Aufbau des Nutzers gefunden)

Der Nutzer hat kaimarkit unter `kaimarkit.6b6a.de` hinter seine vorhandene Authelia gehängt. Ergebnis: **HTTP 400** auf jede Anfrage. Kein Hinweis auf die Ursache, weder in der Antwort noch in unserer Dokumentation.

Die Ursache: Seine Authelia ist für `0x2e6b6169.de` zuständig. Eine Forward-Auth-Anfrage für einen Host **außerhalb ihrer Cookie-Domäne** lehnt sie mit 400 ab, und Traefik reicht den Statuscode unverändert durch.

Belegt, nicht geschlossen — Authelia direkt gefragt, mit den Kopfzeilen, die Traefik ihr schickt:

    X-Forwarded-Host: kaimarkit.6b6a.de   ->  400

## Was `docs/betrieb/authelia.md` nicht sagt

**`KAIMARKIT_DOMAIN` muss unter der Cookie-Domäne der vorhandenen Authelia liegen.** Das steht nirgends. Die Seite erklärt die Middleware, die Response-Header und den `/api`-Schalter — aber nicht die Bedingung, ohne die nichts davon greift.

## Warum die Fehlersuche so teuer war

Der Statuscode **400** ist die einzige Auskunft, die man bekommt, und er zeigt in die falsche Richtung. Wir haben nacheinander geprüft: Netz, Middlewarename, Entrypoint, Certresolver, Router-Status, DNS — alles in Ordnung. Erst der direkte Aufruf an Authelia hat es gezeigt.

Der Unterschied, der die Richtung entscheidet, gehört in die Dokumentation:

- **404** — kein Router greift. Die Ursache liegt bei Traefik oder bei unseren Labels.
- **400 mit `content-length: 15`** (`400 Bad Request` als Klartext) — etwas hat geantwortet. Die Ursache liegt hinter der Middleware, also bei Authelia.

## Eigene Dateien

- `docs/betrieb/authelia.md`
- `docker/.env.example` (Kommentar bei `KAIMARKIT_DOMAIN`)

Konvention 6: Kommt dort ein Kommentar hinzu, gehört der Abgleich mit `docs/betrieb/konfiguration.md` dazu.

## Vorgaben

Die Bedingung gehört an die Stelle, an der `KAIMARKIT_DOMAIN` erklärt wird — nicht in einen Abschnitt „Fehlersuche" am Ende. Wer die Variable setzt, soll dort lesen, dass sie unter der Cookie-Domäne der Authelia liegen muss.

Dazu ein kurzer Abschnitt zur Unterscheidung 404 gegen 400 mit dem Aufruf, der es klärt:

    docker run --rm --network <traefik-netz> curlimages/curl -s -o /dev/null -w '%{http_code}\n' \
      -H "X-Forwarded-Proto: https" -H "X-Forwarded-Host: <domain>" -H "X-Forwarded-Uri: /" \
      http://<authelia>:9091/api/authz/forward-auth

Und ein Satz zum teureren Weg, damit ihn niemand für einen Handgriff hält: Eine zweite Cookie-Domäne in Authelia verlangt **je Domäne eine eigene `authelia_url`**, also ein erreichbares Anmeldeportal unter der neuen Domäne, mit eigenem Zertifikat und eigenem Router.

## Nachrangig, im selben Merge, wenn es passt

`TRAEFIK_ENTRYPOINT` und `TRAEFIK_CERTRESOLVER` stehen in `.env.example` wie Voreinstellungen da. Es sind Beispielwerte, die zu einer vorhandenen Traefik passen müssen; beim Netz sagt der Kommentar es bereits („muss bereits existieren"), bei diesen beiden nicht. Beim Nutzer stimmten sie zufällig — das ist der Fall, der es das nächste Mal schwerer macht.

## Prüfung

- Wer `docs/betrieb/authelia.md` von oben liest, erfährt die Domänenbedingung **bevor** er `KAIMARKIT_DOMAIN` setzt.
- Der genannte Aufruf ist am laufenden Aufbau ausgeführt worden und liefert das beschriebene Ergebnis — nicht abgeschrieben.
- `mkdocs build --strict` läuft durch.

[[2026-09-01]] Tue 21:29
**Gelöst, und es waren zwei Dinge statt einem** (Nutzer, 01.09.2026): die Cookie-Domäne **und** ein Eintrag für den Dienst in Authelias `access_control`.

Der zweite Teil gehört mit in dieses Ticket. Wer nur die Domäne richtigstellt, kommt bis zur Anmeldung und bekommt danach eine Zugriffsverweigerung — wieder ohne Hinweis auf die Ursache, und wieder sucht man sie zuerst bei kaimarkit.

Die Dokumentation muss also **beides** nennen, in der Reihenfolge, in der man darauf stößt:

1. `KAIMARKIT_DOMAIN` liegt unter der Cookie-Domäne der vorhandenen Authelia. Sonst: 400 vor jeder Anmeldung.
2. Authelias `access_control` braucht eine Regel für diese Domäne. Ohne sie gilt die `default_policy` — steht die auf `deny`, folgt nach erfolgreicher Anmeldung eine Verweigerung.

Beides sind Änderungen an **Authelias** Konfiguration, nicht an unserer. Genau deshalb gehören sie auf unsere Seite: Wer kaimarkit hinter eine vorhandene Authelia hängt, erfährt sonst nirgends, was er dort tun muss.

Der Aufbau des Nutzers läuft seither unter `kaimarkit.0x2e6b6169.de`.

[[2026-09-03]] Thu 14:20
Nachtrag von katche vor der Freigabe, zur zweiten Pruefzeile: Der Aufruf ist am
01.09.2026 am Aufbau des Nutzers ausgefuehrt worden, das Ergebnis steht oben im
Befund (X-Forwarded-Host: kaimarkit.6b6a.de -> 400). Diese Lane kann ihn nicht
wiederholen; der VPS gehoert dem Nutzer, und hier laeuft keine Authelia. Die Zeile
meint deshalb: den vorhandenen Beleg unveraendert uebernehmen, mit Datum und
Herkunft, statt einen Aufruf zu erfinden, der nie gelaufen ist. Kein Grund zur
Uebergabe.
In der Doku steht die Domaene als Platzhalter, nicht als fester Name. Der Aufbau des
Nutzers laeuft inzwischen unter kaimarkit.0x2e6b6169.de; die alte Domaene aus dem
Befund gehoert nicht in die Seite.

[[2026-09-03]] Thu 14:26
Umgesetzt in Merge 9111827 (Commit 8994bc8), Zweig task/92-authelia-cookie-domain entfernt.

Reihenfolge der Ueberschriften in docs/betrieb/authelia.md nach der Aenderung:
`# Authelia` -> `## Zwei Eingriffe in Authelias Konfiguration` (neu) -> `## Was
vorher da sein muss` -> `## Starten` -> `## Zwei Wege zur Middleware` -> `## @docker
oder @file` -> `## Der Name der eigenen Middleware folgt dem Namensraum` -> `## Die
API bleibt erreichbar` -> `## Pruefen` -> `## 404 oder 400 — der Statuscode zeigt die
Richtung` (neu). Der neue Abschnitt steht vor `Starten`, wo docker/.env kopiert und
KAIMARKIT_DOMAIN gesetzt wird — wer von oben liest, hat die Domaenenbedingung und die
access_control-Regel vorher gelesen. Die Bedingung steht ausdruecklich nicht im
Fehlersuche-Abschnitt; der ganz am Ende erklaert nur, wohin 404 und 400 zeigen. Auch
die Liste 'Was vorher da sein muss' verweist jetzt auf beides statt nur auf die
Zugriffsregel.

Beleg fuer den 400er: steht mit Datum und Herkunft in der Seite — 'Dieser Aufruf hat
die Ursache am 01.09.2026 am VPS-Aufbau des Nutzers gezeigt: Fuer einen Host
ausserhalb der Cookie-Domaene antwortete Authelia mit 400.' Uebernommener Befund,
keine eigene Messung; hier laeuft keine Authelia, der Aufruf wurde nicht wiederholt.
Die Domaene steht ueberall als Platzhalter (kaimarkit.example.com, auth.example.com);
kaimarkit.6b6a.de kommt in der Seite nicht vor.

Konvention 6, Abgleich docker/.env.example gegen docs/betrieb/konfiguration.md: Drei
Variablen haben einen Kommentar bekommen, alle drei sind in konfiguration.md
gleichlautend beschrieben.
- KAIMARKIT_DOMAIN: neuer Kommentarblock (Cookie-Domaene, 400 vor der Anmeldung,
  access_control/default_policy, Verweis auf authelia.md). In konfiguration.md die
  Tabellenzeile ergaenzt ('Hinter Authelia muss er unter deren Cookie-Domaene
  liegen') und am Ende des Authelia-Abschnitts ein Absatz, der beide Bedingungen
  nennt und auf authelia.md verweist.
- TRAEFIK_ENTRYPOINT und TRAEFIK_CERTRESOLVER: Punkt 6 des Rumpfs ist drin. Neuer
  Kommentar 'Beispielwerte, keine Voreinstellungen: Entrypoint und Certresolver
  muessen so heissen wie in der statischen Konfiguration der vorhandenen Traefik.'
  In konfiguration.md beide Tabellenzeilen um 'Beispielwert.' ergaenzt, dazu ein
  Absatz unter der Traefik-Tabelle mit derselben Aussage. Keine weitere Variable
  angefasst.

mkdocs build --strict in der pyenv-Umgebung claude-code: laeuft durch, keine Warnung
und kein Fehler. Die rote Bannermeldung zu MkDocs 2.0 kommt vom Material-Theme, ist
eine Herstellernotiz und keine Bauwarnung.

Befund fuer den PO, nicht geaendert: docker/.env.example schreibt Umlaute
durchgaengig in ASCII-Umschrift ('noetig', 'Groesse'), obwohl Gedankenstriche darin
stehen, die Datei also UTF-8 ist. Die neuen Kommentare folgen dieser
Dateikonvention, damit vier Zeilen nicht aus zweihundert herausfallen. Die ganze
Datei umzustellen waere ein eigenes Ticket.
